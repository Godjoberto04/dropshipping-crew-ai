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

    def _generate_summary(self, trend_metrics: Dict[str, Dict[str, Any]], related_queries: Dict[str, Dict[str, pd.DataFrame]]) -> Dict[str, Any]:
        """
        Génère un résumé des résultats d'analyse de tendances.
        
        Args:
            trend_metrics: Métriques de tendance calculées
            related_queries: Requêtes associées récupérées de Google Trends
            
        Returns:
            Dictionnaire avec le résumé des résultats
        """
        summary = {
            'top_keyword': None,
            'top_score': 0,
            'growing_keywords': [],
            'declining_keywords': [],
            'seasonal_keywords': [],
            'related_terms': {},
            'insights': []
        }
        
        # Identification du mot-clé avec le meilleur score
        for keyword, metrics in trend_metrics.items():
            trend_score = metrics.get('trend_score', 0)
            
            if trend_score > summary['top_score']:
                summary['top_score'] = trend_score
                summary['top_keyword'] = keyword
                
            # Classification des mots-clés par tendance
            if metrics.get('is_growing', False):
                summary['growing_keywords'].append(keyword)
            elif metrics.get('growth_rate', 0) < -5:  # Seuil arbitraire pour "en déclin"
                summary['declining_keywords'].append(keyword)
                
            # Identification des mots-clés saisonniers
            if metrics.get('is_seasonal', False):
                summary['seasonal_keywords'].append(keyword)
                
            # Génération d'insights pour ce mot-clé
            keyword_insights = []
            
            if metrics.get('is_growing', False) and metrics.get('growth_rate', 0) > 25:
                keyword_insights.append(f"Forte croissance (+{metrics.get('growth_rate', 0):.1f}%)")
                
            if metrics.get('is_seasonal', False):
                keyword_insights.append(f"Motif saisonnier détecté (score: {metrics.get('seasonality_score', 0):.1f})")
                
            if metrics.get('volatility', 0) > 25:
                keyword_insights.append("Volatilité élevée")
                
            if metrics.get('momentum', 0) > 15:
                keyword_insights.append(f"Momentum positif (+{metrics.get('momentum', 0):.1f}%)")
            elif metrics.get('momentum', 0) < -15:
                keyword_insights.append(f"Momentum négatif ({metrics.get('momentum', 0):.1f}%)")
                
            if keyword_insights:
                summary['insights'].append({
                    'keyword': keyword,
                    'insights': keyword_insights
                })
            
            # Extraction des termes associés
            if keyword in related_queries and related_queries[keyword]:
                top_related = []
                rising_related = []
                
                if 'top' in related_queries[keyword] and not related_queries[keyword]['top'].empty:
                    top_df = related_queries[keyword]['top']
                    top_related = top_df.head(5)['query'].tolist() if 'query' in top_df.columns else []
                    
                if 'rising' in related_queries[keyword] and not related_queries[keyword]['rising'].empty:
                    rising_df = related_queries[keyword]['rising']
                    rising_related = rising_df.head(5)['query'].tolist() if 'query' in rising_df.columns else []
                    
                summary['related_terms'][keyword] = {
                    'top': top_related,
                    'rising': rising_related
                }
        
        # Génération de statistiques générales
        summary['stats'] = {
            'total_keywords': len(trend_metrics),
            'growing_count': len(summary['growing_keywords']),
            'declining_count': len(summary['declining_keywords']),
            'seasonal_count': len(summary['seasonal_keywords']),
            'timestamp': time.time()
        }
        
        return summary

    def _detect_seasonality(self, results_by_timeframe: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Détecte les motifs saisonniers dans les données.
        
        Args:
            results_by_timeframe: Résultats d'analyse par période
            
        Returns:
            Dictionnaire avec les informations de saisonnalité
        """
        seasonality_result = {
            'is_seasonal': False,
            'seasonality_score': 0,
            'peak_months': [],
            'pattern_description': '',
            'confidence': 'low'
        }
        
        # Vérification si les périodes longues contiennent des données
        long_term_results = results_by_timeframe.get('long_term', None) or results_by_timeframe.get('five_years', None)
        
        if not long_term_results or 'error' in long_term_results:
            return seasonality_result
            
        # Vérifier si les données d'intérêt au fil du temps sont disponibles
        interest_over_time = long_term_results.get('interest_over_time', pd.DataFrame())
        
        if interest_over_time.empty or len(interest_over_time) < 52:  # Au moins un an de données
            return seasonality_result
            
        # Extraction des données du premier mot-clé (normalement un seul pour analyze_product)
        if len(interest_over_time.columns) == 0:
            return seasonality_result
            
        keyword = interest_over_time.columns[0]
        keyword_data = interest_over_time[keyword]
        
        # Conversion de l'index en datetime si ce n'est pas déjà le cas
        if not isinstance(interest_over_time.index, pd.DatetimeIndex):
            try:
                interest_over_time.index = pd.to_datetime(interest_over_time.index)
                keyword_data.index = interest_over_time.index
            except Exception as e:
                logger.warning(f"Impossible de convertir l'index en datetime: {str(e)}")
                return seasonality_result
        
        try:
            # Calcul de l'autocorrélation pour détecter la saisonnalité
            max_lag = min(52, len(keyword_data) // 2)  # Maximum 1 an de lag, ou la moitié des données
            seasonal_lags = [12, 24, 26, 52]  # Lags correspondant à des motifs saisonniers potentiels
            seasonal_lag = 0
            max_correlation = 0.3  # Seuil minimum de corrélation pour considérer comme saisonnier
            
            for lag in seasonal_lags:
                if lag < max_lag:
                    # Calcul de l'autocorrélation
                    shifted_data = keyword_data.shift(lag).dropna()
                    if len(shifted_data) > 10:  # Au moins 10 points de données
                        correlation = keyword_data.iloc[-len(shifted_data):].corr(shifted_data)
                        if correlation > max_correlation:
                            max_correlation = correlation
                            seasonal_lag = lag
            
            # Si un motif saisonnier est détecté
            if seasonal_lag > 0:
                seasonality_result['is_seasonal'] = True
                seasonality_result['seasonality_score'] = max_correlation * 100
                
                # Détermination de la confiance
                if max_correlation > 0.7:
                    seasonality_result['confidence'] = 'high'
                elif max_correlation > 0.5:
                    seasonality_result['confidence'] = 'medium'
                else:
                    seasonality_result['confidence'] = 'low'
                
                # Identification des mois de pic
                monthly_avg = keyword_data.groupby(keyword_data.index.month).mean()
                threshold = monthly_avg.mean() + (monthly_avg.std() * 0.5)
                peak_months_indices = monthly_avg[monthly_avg > threshold].index.tolist()
                
                # Conversion des indices de mois en noms de mois
                month_names = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                              'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                peak_months = [month_names[i-1] for i in peak_months_indices]
                seasonality_result['peak_months'] = peak_months
                
                # Description du motif
                if seasonal_lag == 12:
                    pattern = "mensuel"
                elif seasonal_lag in [24, 26]:
                    pattern = "bimensuel"
                elif seasonal_lag == 52:
                    pattern = "annuel"
                else:
                    pattern = f"périodique ({seasonal_lag} semaines)"
                    
                seasonality_result['pattern_description'] = f"Motif {pattern} détecté"
                if peak_months:
                    seasonality_result['pattern_description'] += f", avec des pics en {', '.join(peak_months)}"
                
        except Exception as e:
            logger.warning(f"Erreur lors de la détection de saisonnalité: {str(e)}")
            
        return seasonality_result
