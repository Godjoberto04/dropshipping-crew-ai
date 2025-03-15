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

    def analyze_product(
        self, 
        product_name: str,
        product_keywords: List[str] = None,
        timeframes: List[str] = None,
        geo: str = None
    ) -> Dict[str, Any]:
        """
        Analyse complète d'un produit sur plusieurs périodes.
        
        Args:
            product_name: Nom du produit
            product_keywords: Mots-clés supplémentaires liés au produit
            timeframes: Liste des périodes à analyser
            geo: Zone géographique
            
        Returns:
            Dictionnaire avec l'analyse complète du produit
        """
        if product_keywords is None:
            product_keywords = []
            
        # Fusion et déduplication du nom de produit et des mots-clés
        all_keywords = [product_name] + product_keywords
        unique_keywords = list(dict.fromkeys(all_keywords))
        
        if timeframes is None:
            timeframes = ['short_term', 'medium_term', 'long_term']
            
        # Résultats pour chaque période
        results_by_timeframe = {}
        
        for timeframe in timeframes:
            try:
                # On analyse uniquement le nom du produit en détail
                results = self.analyze_keywords(
                    keywords=[product_name],
                    timeframe=timeframe,
                    geo=geo
                )
                results_by_timeframe[timeframe] = results
            except Exception as e:
                logger.warning(f"Erreur lors de l'analyse pour {timeframe}: {str(e)}")
                results_by_timeframe[timeframe] = {"error": str(e)}
        
        # Analyse des mots-clés associés sur la période moyenne
        related_keywords_analysis = {}
        
        if len(product_keywords) > 0:
            for keyword in product_keywords[:4]:  # Limité à 4 pour éviter trop de requêtes
                try:
                    keyword_results = self.analyze_keywords(
                        keywords=[keyword],
                        timeframe='medium_term',
                        geo=geo
                    )
                    related_keywords_analysis[keyword] = keyword_results
                except Exception as e:
                    logger.warning(f"Erreur lors de l'analyse du mot-clé {keyword}: {str(e)}")
        
        # Création d'un rapport complet
        product_analysis = {
            'product_name': product_name,
            'keywords': unique_keywords,
            'analysis_by_timeframe': results_by_timeframe,
            'related_keywords_analysis': related_keywords_analysis,
            'overall_trend_score': self._calculate_overall_trend_score(results_by_timeframe),
            'is_trending': self._is_product_trending(results_by_timeframe),
            'seasonality': self._detect_seasonality(results_by_timeframe),
            'conclusion': self._generate_product_conclusion(results_by_timeframe)
        }
        
        return product_analysis

    def compare_products(
        self,
        products: List[str],
        timeframe: str = 'medium_term',
        geo: str = None,
        category: int = 0,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Compare plusieurs produits sur la base de leurs tendances.
        
        Args:
            products: Liste des noms de produits à comparer (max 5)
            timeframe: Période d'analyse
            geo: Zone géographique
            category: ID de catégorie Google Trends
            use_cache: Utiliser le cache si disponible
            
        Returns:
            Dictionnaire avec les résultats de la comparaison
            
        Raises:
            ValueError: Si les paramètres sont invalides
            Exception: Si la comparaison échoue
        """
        # Validation des paramètres
        if not products:
            raise ValueError("Au moins un produit est requis")
            
        if len(products) < 2:
            raise ValueError("Au moins deux produits sont nécessaires pour une comparaison")
            
        if len(products) > 5:
            logger.warning("Plus de 5 produits fournis. Seuls les 5 premiers seront comparés.")
            products = products[:5]
        
        logger.info(f"Comparaison de {len(products)} produits: {', '.join(products)}")
        
        try:
            # Utilisation de la fonction d'analyse de mots-clés existante
            analysis_results = self.analyze_keywords(
                keywords=products,
                timeframe=timeframe,
                geo=geo,
                category=category,
                use_cache=use_cache
            )
            
            # Extraction des métriques de tendance pour la comparaison
            trend_metrics = analysis_results.get('trend_metrics', {})
            
            # Création d'un classement des produits
            ranked_products = []
            for product, metrics in trend_metrics.items():
                ranked_products.append({
                    'name': product,
                    'trend_score': metrics.get('trend_score', 0),
                    'current_interest': metrics.get('current_interest', 0),
                    'growth_rate': metrics.get('growth_rate', 0),
                    'is_growing': metrics.get('is_growing', False),
                    'is_seasonal': metrics.get('is_seasonal', False)
                })
            
            # Tri des produits par score de tendance (du plus élevé au plus bas)
            ranked_products.sort(key=lambda x: x['trend_score'], reverse=True)
            
            # Ajout des données d'intérêt au fil du temps pour visualisation
            interest_over_time = {}
            if not analysis_results.get('interest_over_time', pd.DataFrame()).empty:
                for product in products:
                    if product in analysis_results['interest_over_time'].columns:
                        interest_over_time[product] = analysis_results['interest_over_time'][product].tolist()
            
            # Construction du résultat de la comparaison
            comparison_result = {
                'ranked_products': ranked_products,
                'interest_over_time': interest_over_time,
                'analysis_period': timeframe,
                'timestamp': time.time(),
                'top_product': ranked_products[0]['name'] if ranked_products else None,
                'product_trends': {p['name']: {'score': p['trend_score'], 'growing': p['is_growing']} for p in ranked_products}
            }
            
            return comparison_result
            
        except Exception as e:
            error_msg = f"Erreur lors de la comparaison des produits: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise