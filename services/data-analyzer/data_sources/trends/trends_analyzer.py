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