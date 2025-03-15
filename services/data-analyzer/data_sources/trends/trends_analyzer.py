#!/usr/bin/env python3
"""
Module d'analyse de tendances via Google Trends.
Permet d'évaluer l'évolution de l'intérêt pour des produits ou mots-clés sur différentes périodes et régions.
"""

import os
import json
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError

from config import settings, get_logger

logger = get_logger("trends_analyzer")

class TrendsAnalyzer:
    """Classe d'analyse de tendances via Google Trends."""
    
    def __init__(
        self,
        hl: str = None,
        tz: int = None,
        geo: str = None,
        timeout: Tuple[int, int] = (10, 25),
        retries: int = 2,
        backoff_factor: float = 0.1,
        proxies: Dict[str, str] = None,
        cache_dir: str = None
    ):
        """
        Initialise l'analyseur de tendances.
        
        Args:
            hl: Langue pour Google Trends (fr, en-US, etc.)
            tz: Fuseau horaire (-360 à 360)
            geo: Pays par défaut (FR, US, etc.)
            timeout: Timeout pour les requêtes (connect, read)
            retries: Nombre de tentatives en cas d'échec
            backoff_factor: Facteur de recul pour les tentatives
            proxies: Configuration de proxy
            cache_dir: Répertoire de cache
        """
        self.hl = hl or settings.PYTRENDS_HL
        self.tz = tz or settings.PYTRENDS_TZ
        self.geo = geo or settings.PYTRENDS_GEO
        self.timeframes = settings.PYTRENDS_TIMEFRAMES
        
        # Configuration de proxy si activée
        self.proxies = None
        if settings.PROXY_ENABLED and settings.PROXY_URL:
            self.proxies = {'https': settings.PROXY_URL}
        
        # Si des proxies spécifiques sont fournis, ils ont priorité
        if proxies:
            self.proxies = proxies
            
        # Initialisation de la connexion PyTrends
        self.pytrends = TrendReq(
            hl=self.hl,
            tz=self.tz,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor,
            proxies=self.proxies
        )
        
        # Répertoire de cache
        self.cache_dir = cache_dir or os.path.join(settings.CACHE_DIR, 'trends')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        logger.info(f"TrendsAnalyzer initialisé (langue: {self.hl}, région: {self.geo})")
        
    def _get_cache_file_path(self, keywords: List[str], timeframe: str, geo: str, cat: int) -> str:
        """
        Génère le chemin du fichier de cache.
        
        Args:
            keywords: Liste de mots-clés
            timeframe: Période d'analyse
            geo: Région
            cat: Catégorie
            
        Returns:
            Chemin du fichier de cache
        """
        # Création d'une clé de cache basée sur les paramètres
        keywords_str = "_".join(sorted([k.replace(" ", "-") for k in keywords]))
        cache_key = f"{keywords_str}_{timeframe}_{geo}_{cat}"
        
        # Utilisation d'un hachage si la clé est trop longue
        if len(cache_key) > 100:
            import hashlib
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _save_to_cache(self, cache_file: str, data: Dict[str, Any]) -> None:
        """
        Sauvegarde les données dans le cache.
        
        Args:
            cache_file: Chemin du fichier de cache
            data: Données à sauvegarder
        """
        try:
            # Conversion des DataFrames en dictionnaires
            cache_data = {}
            for key, value in data.items():
                if isinstance(value, pd.DataFrame):
                    cache_data[key] = value.to_dict()
                else:
                    cache_data[key] = value
                    
            # Ajout de métadonnées de cache
            cache_data['_cache_timestamp'] = time.time()
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False)
                
        except Exception as e:
            logger.warning(f"Erreur lors de la sauvegarde du cache: {str(e)}")
    
    def _load_from_cache(self, cache_file: str, max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """
        Charge des données depuis le cache si elles existent et sont récentes.
        
        Args:
            cache_file: Chemin du fichier de cache
            max_age_hours: Âge maximum du cache en heures
            
        Returns:
            Données du cache ou None si cache invalide/inexistant
        """
        try:
            if not os.path.exists(cache_file):
                return None
                
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # Vérification de l'âge du cache
            timestamp = cache_data.get('_cache_timestamp', 0)
            cache_age = time.time() - timestamp
            max_age_seconds = max_age_hours * 3600
            
            if cache_age > max_age_seconds:
                logger.debug(f"Cache expiré ({cache_age/3600:.1f} heures > {max_age_hours} heures)")
                return None
                
            # Conversion des dictionnaires en DataFrames
            result = {}
            for key, value in cache_data.items():
                if key.startswith('_'):  # Ignorer les métadonnées
                    continue
                    
                if isinstance(value, dict) and ('index' in value or 'columns' in value):
                    try:
                        result[key] = pd.DataFrame.from_dict(value)
                    except Exception:
                        result[key] = value
                else:
                    result[key] = value
                    
            logger.debug(f"Données chargées depuis le cache ({cache_file})")
            return result
            
        except Exception as e:
            logger.warning(f"Erreur lors du chargement du cache: {str(e)}")
            return None
            
    def analyze_keywords(
        self, 
        keywords: Union[str, List[str]], 
        timeframe: str = 'medium_term',
        geo: str = None,
        category: int = 0,
        use_cache: bool = True,
        cache_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Analyse des mots-clés en utilisant Google Trends.
        
        Args:
            keywords: Mot-clé unique ou liste de mots-clés (max 5)
            timeframe: Période d'analyse ('short_term', 'medium_term', 'long_term', 'five_years' ou format PyTrends)
            geo: Zone géographique (pays, région)
            category: ID de catégorie Google Trends
            use_cache: Utiliser le cache si disponible
            cache_hours: Âge maximal du cache en heures
            
        Returns:
            Dictionnaire avec les résultats d'analyse
            
        Raises:
            ValueError: Si les paramètres sont invalides
            Exception: Si l'analyse échoue
        """
        # Validation et normalisation des mots-clés
        if isinstance(keywords, str):
            keywords = [keywords]
            
        if not keywords:
            raise ValueError("Au moins un mot-clé est requis")
            
        # Google Trends limite à 5 mots-clés
        if len(keywords) > 5:
            logger.warning(f"Plus de 5 mots-clés fournis. Seuls les 5 premiers seront utilisés.")
            keywords = keywords[:5]
            
        # Validation du timeframe
        if timeframe in self.timeframes:
            timeframe_str = self.timeframes[timeframe]
        else:
            timeframe_str = timeframe
            
        # Paramètres par défaut
        geo = geo or self.geo
        
        # Vérifier le cache si demandé
        cache_file = self._get_cache_file_path(keywords, timeframe_str, geo, category)
        if use_cache:
            cached_data = self._load_from_cache(cache_file, max_age_hours=cache_hours)
            if cached_data:
                return cached_data
        
        logger.info(f"Analyse de {len(keywords)} mots-clés: {', '.join(keywords)}")
        logger.info(f"Paramètres: timeframe={timeframe_str}, geo={geo}, category={category}")
        
        try:
            # Construction de la requête
            self.pytrends.build_payload(
                kw_list=keywords,
                cat=category,
                timeframe=timeframe_str,
                geo=geo
            )
            
            # Récupération des données d'intérêt au fil du temps
            interest_over_time = self.pytrends.interest_over_time()
            
            # Récupération des requêtes associées
            related_queries = self.pytrends.related_queries()
            
            # Récupération des sujets associés
            related_topics = self.pytrends.related_topics()
            
            # Récupération de l'intérêt par région
            try:
                interest_by_region = self.pytrends.interest_by_region(resolution='COUNTRY')
            except Exception as e:
                logger.warning(f"Erreur lors de la récupération de l'intérêt par région: {str(e)}")
                interest_by_region = pd.DataFrame()
                
            # Calcul des métriques de tendance
            trend_metrics = self._calculate_trend_metrics(interest_over_time, keywords)
            
            # Organisation des résultats
            results = {
                'interest_over_time': interest_over_time,
                'related_queries': related_queries,
                'related_topics': related_topics,
                'interest_by_region': interest_by_region,
                'trend_metrics': trend_metrics,
                'summary': self._generate_summary(trend_metrics, related_queries)
            }
            
            # Mise en cache des résultats
            if use_cache:
                self._save_to_cache(cache_file, results)
                
            return results
            
        except ResponseError as e:
            error_msg = f"Erreur de l'API Google Trends: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Erreur lors de l'analyse des tendances: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise