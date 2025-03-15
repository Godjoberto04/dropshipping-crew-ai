#!/usr/bin/env python3
"""
Module d'analyse de tendances via Google Trends.
Permet d'évaluer l'évolution de l'intérêt pour des produits ou mots-clés sur différentes périodes et régions.
"""

import os
import json
import time
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import pickle
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
            
    def get_rising_products(
        self, 
        category: str = None,
        geo: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Identifie les produits en tendance montante dans une catégorie.
        
        Args:
            category: Catégorie de produits (par défaut: toutes)
            geo: Zone géographique
            limit: Nombre maximum de produits à retourner
            
        Returns:
            Liste des produits en tendance avec leurs métriques
        """
        try:
            # Déterminer les requêtes de recherche pour la catégorie
            category_keywords = self._get_category_keywords(category)
            
            if not category_keywords:
                logger.warning(f"Aucun mot-clé trouvé pour la catégorie: {category}")
                return []
            
            # Analyse des tendances pour la catégorie
            category_trends = self.analyze_keywords(
                keywords=[category] if category else category_keywords[0],
                timeframe='short_term',
                geo=geo
            )
            
            # Extraction des requêtes en tendance montante
            rising_queries = []
            
            if 'related_queries' in category_trends:
                for keyword, queries in category_trends['related_queries'].items():
                    if 'rising' in queries and not queries['rising'].empty:
                        rising_df = queries['rising']
                        if 'query' in rising_df.columns and 'value' in rising_df.columns:
                            for _, row in rising_df.iterrows():
                                rising_queries.append({
                                    'query': row['query'],
                                    'value': row['value'],
                                    'source_keyword': keyword
                                })
            
            # Si on n'a pas assez de requêtes, explorer plus de mots-clés de la catégorie
            if len(rising_queries) < limit and len(category_keywords) > 1:
                for keyword in category_keywords[1:3]:  # Limité à 3 mots-clés supplémentaires
                    try:
                        kw_trends = self.analyze_keywords(
                            keywords=[keyword],
                            timeframe='short_term',
                            geo=geo
                        )
                        
                        if 'related_queries' in kw_trends and keyword in kw_trends['related_queries']:
                            queries = kw_trends['related_queries'][keyword]
                            if 'rising' in queries and not queries['rising'].empty:
                                rising_df = queries['rising']
                                if 'query' in rising_df.columns and 'value' in rising_df.columns:
                                    for _, row in rising_df.iterrows():
                                        rising_queries.append({
                                            'query': row['query'],
                                            'value': row['value'],
                                            'source_keyword': keyword
                                        })
                    except Exception as e:
                        logger.warning(f"Erreur lors de l'analyse du mot-clé de catégorie {keyword}: {str(e)}")
            
            # Analyse des produits en tendance montante
            rising_products = []
            
            for query_data in rising_queries:
                try:
                    # Vérifier si la requête semble être un produit
                    if self._is_likely_product(query_data['query']):
                        product_name = query_data['query']
                        
                        # Analyse du produit
                        product_analysis = self.analyze_keywords(
                            keywords=[product_name],
                            timeframe='short_term',
                            geo=geo
                        )
                        
                        # Extraction des métriques du produit
                        if 'trend_metrics' in product_analysis and product_name in product_analysis['trend_metrics']:
                            metrics = product_analysis['trend_metrics'][product_name]
                            
                            rising_products.append({
                                'name': product_name,
                                'trend_score': metrics.get('trend_score', 0),
                                'growth_rate': metrics.get('growth_rate', 0),
                                'is_growing': metrics.get('is_growing', False),
                                'rising_value': query_data['value'],
                                'category': category or query_data['source_keyword']
                            })
                except Exception as e:
                    logger.warning(f"Erreur lors de l'analyse du produit {query_data['query']}: {str(e)}")
            
            # Tri des produits par score de tendance
            rising_products.sort(key=lambda x: x['trend_score'], reverse=True)
            
            # Limitation au nombre demandé
            return rising_products[:limit]
            
        except Exception as e:
            error_msg = f"Erreur lors de la recherche de produits en tendance: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return []
    
    def _calculate_overall_trend_score(self, results_by_timeframe: Dict[str, Dict[str, Any]]) -> float:
        """
        Calcule un score global de tendance basé sur les analyses de différentes périodes.
        
        Args:
            results_by_timeframe: Résultats d'analyse par période
            
        Returns:
            Score global (0-100)
        """
        # Pondération des périodes (ordre d'importance)
        period_weights = {
            'short_term': 0.5,    # Court terme (50%)
            'medium_term': 0.3,   # Moyen terme (30%)
            'long_term': 0.2      # Long terme (20%)
        }
        
        scores = []
        weights = []
        
        for timeframe, results in results_by_timeframe.items():
            # Vérifier si l'analyse a réussi et contient des métriques
            if 'error' in results or 'trend_metrics' not in results:
                continue
                
            # Récupérer les métriques pour le premier mot-clé (normalement un seul pour analyze_product)
            trend_metrics = results.get('trend_metrics', {})
            if not trend_metrics:
                continue
                
            # Prendre le premier mot-clé (il devrait n'y en avoir qu'un seul)
            first_keyword = list(trend_metrics.keys())[0]
            metrics = trend_metrics[first_keyword]
            
            # Récupérer le score de tendance
            trend_score = metrics.get('trend_score', 0)
            
            # Poids pour cette période
            weight = period_weights.get(timeframe, 0.1)  # Valeur par défaut si période inconnue
            
            scores.append(trend_score)
            weights.append(weight)
        
        # Si aucun score valide, retourner 0
        if not scores:
            return 0
            
        # Normalisation des poids
        total_weight = sum(weights)
        if total_weight <= 0:
            return 0
            
        normalized_weights = [w / total_weight for w in weights]
        
        # Calcul de la moyenne pondérée
        overall_score = sum(s * w for s, w in zip(scores, normalized_weights))
        
        return overall_score
    
    def _is_product_trending(self, results_by_timeframe: Dict[str, Dict[str, Any]]) -> bool:
        """
        Détermine si un produit est en tendance basé sur les analyses.
        
        Args:
            results_by_timeframe: Résultats d'analyse par période
            
        Returns:
            True si le produit est en tendance, False sinon
        """
        # Pondération des périodes pour déterminer si un produit est en tendance
        # Court terme plus important que long terme
        period_score_thresholds = {
            'short_term': 70,     # Score minimum pour le court terme
            'medium_term': 60,    # Score minimum pour le moyen terme
            'long_term': 50       # Score minimum pour le long terme
        }
        
        period_growth_thresholds = {
            'short_term': 10,     # Croissance minimum pour le court terme
            'medium_term': 5,     # Croissance minimum pour le moyen terme
            'long_term': 0        # Croissance minimum pour le long terme
        }
        
        # Vérification des critères par période
        trend_scores = {}
        growth_rates = {}
        
        for timeframe, results in results_by_timeframe.items():
            # Vérifier si l'analyse a réussi et contient des métriques
            if 'error' in results or 'trend_metrics' not in results:
                continue
                
            # Récupérer les métriques pour le premier mot-clé
            trend_metrics = results.get('trend_metrics', {})
            if not trend_metrics:
                continue
                
            # Prendre le premier mot-clé (il devrait n'y en avoir qu'un seul)
            first_keyword = list(trend_metrics.keys())[0]
            metrics = trend_metrics[first_keyword]
            
            # Récupérer le score de tendance et le taux de croissance
            trend_scores[timeframe] = metrics.get('trend_score', 0)
            growth_rates[timeframe] = metrics.get('growth_rate', 0)
        
        # Vérification des critères pour chaque période
        for timeframe in ['short_term', 'medium_term', 'long_term']:
            if timeframe in trend_scores:
                score_threshold = period_score_thresholds.get(timeframe, 0)
                growth_threshold = period_growth_thresholds.get(timeframe, 0)
                
                # Pour être "en tendance", au moins une période doit satisfaire les deux critères
                if (trend_scores[timeframe] >= score_threshold and 
                    growth_rates[timeframe] >= growth_threshold):
                    return True
        
        # Vérification de la croissance récente avec momentum
        if 'short_term' in trend_scores and 'medium_term' in trend_scores:
            # Si le score court terme est supérieur au score moyen terme
            if (trend_scores['short_term'] > trend_scores['medium_term'] and
                trend_scores['short_term'] >= 65):
                return True
        
        # Si aucun critère n'est satisfait, le produit n'est pas en tendance
        return False