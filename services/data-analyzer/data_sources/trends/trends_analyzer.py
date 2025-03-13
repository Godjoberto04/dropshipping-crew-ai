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
    
    def _calculate_trend_metrics(self, interest_df: pd.DataFrame, keywords: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Calcule des métriques de tendance à partir des données d'intérêt.
        
        Args:
            interest_df: DataFrame avec l'intérêt au fil du temps
            keywords: Liste des mots-clés
            
        Returns:
            Dictionnaire avec les métriques par mot-clé
        """
        metrics = {}
        
        if interest_df.empty:
            return metrics
        
        for keyword in keywords:
            if keyword not in interest_df.columns:
                continue
                
            keyword_data = interest_df[keyword].dropna()
            
            if len(keyword_data) < 2:
                continue
                
            # Calcul de l'intérêt actuel (valeur la plus récente)
            current_interest = keyword_data.iloc[-1]
            
            # Calcul de l'intérêt moyen
            avg_interest = keyword_data.mean()
            
            # Calcul du taux de croissance
            start_value = keyword_data.iloc[0]
            end_value = keyword_data.iloc[-1]
            growth_rate = ((end_value - start_value) / start_value) * 100 if start_value > 0 else 0
            
            # Calcul de la volatilité (écart-type)
            volatility = keyword_data.std()
            
            # Calcul du momentum (moyenne des 3 derniers points vs 3 précédents)
            if len(keyword_data) >= 6:
                recent_avg = keyword_data.iloc[-3:].mean()
                previous_avg = keyword_data.iloc[-6:-3].mean()
                momentum = ((recent_avg - previous_avg) / previous_avg) * 100 if previous_avg > 0 else 0
            else:
                momentum = 0
            
            # Détection de tendance croissante
            is_growing = growth_rate > 5
            
            # Détection de saisonnalité
            is_seasonal = False
            seasonality_score = 0
            
            if len(keyword_data) >= 52:  # Au moins un an de données hebdomadaires
                # Détection simple de saisonnalité (corrélation avec données décalées)
                for shift in [52]:  # Vérification des motifs annuels
                    if shift < len(keyword_data):
                        correlation = keyword_data.autocorr(shift)
                        if correlation > 0.5:  # Forte corrélation indique une saisonnalité
                            is_seasonal = True
                            seasonality_score = correlation * 100
            
            metrics[keyword] = {
                'current_interest': current_interest,
                'average_interest': avg_interest,
                'growth_rate': growth_rate,
                'volatility': volatility,
                'momentum': momentum,
                'is_growing': is_growing,
                'is_seasonal': is_seasonal,
                'seasonality_score': seasonality_score,
                'trend_score': self._calculate_trend_score(current_interest, growth_rate, volatility, momentum)
            }
        
        return metrics
    
    def _calculate_trend_score(
        self, 
        current_interest: float, 
        growth_rate: float, 
        volatility: float, 
        momentum: float
    ) -> float:
        """
        Calcule un score de tendance global (0-100).
        
        Args:
            current_interest: Niveau d'intérêt actuel
            growth_rate: Taux de croissance en pourcentage
            volatility: Volatilité (écart-type)
            momentum: Momentum récent en pourcentage
            
        Returns:
            Score de tendance global (0-100)
        """
        # Conversion des valeurs en scores 0-100
        current_score = min(100, current_interest)
        
        growth_score = 50
        if growth_rate > 100:
            growth_score = 100
        elif growth_rate > 50:
            growth_score = 90
        elif growth_rate > 25:
            growth_score = 80
        elif growth_rate > 10:
            growth_score = 70
        elif growth_rate > 0:
            growth_score = 60
        elif growth_rate > -10:
            growth_score = 40
        elif growth_rate > -25:
            growth_score = 30
        elif growth_rate > -50:
            growth_score = 20
        else:
            growth_score = 10
        
        # Une volatilité plus faible est préférable
        volatility_score = max(0, 100 - volatility)
        
        # Score de momentum
        momentum_score = 50
        if momentum > 50:
            momentum_score = 100
        elif momentum > 25:
            momentum_score = 90
        elif momentum > 10:
            momentum_score = 80
        elif momentum > 0:
            momentum_score = 70
        elif momentum > -10:
            momentum_score = 40
        elif momentum > -25:
            momentum_score = 30
        else:
            momentum_score = 20
        
        # Calcul de la moyenne pondérée
        trend_score = (
            (current_score * 0.3) +
            (growth_score * 0.3) +
            (volatility_score * 0.1) +
            (momentum_score * 0.3)
        )
        
        return trend_score
    
    def _generate_summary(
        self, 
        trend_metrics: Dict[str, Dict[str, Any]], 
        related_queries: Dict[str, Dict[str, pd.DataFrame]]
    ) -> Dict[str, Any]:
        """
        Génère un résumé des tendances.
        
        Args:
            trend_metrics: Métriques de tendance par mot-clé
            related_queries: Requêtes associées
            
        Returns:
            Résumé formaté
        """
        summary = {
            'highlights': [],
            'top_related_queries': {},
            'trend_status': {}
        }
        
        # Traitement des métriques de tendance
        for keyword, metrics in trend_metrics.items():
            # Statut de tendance
            if metrics['trend_score'] >= 80:
                trend_status = "forte hausse"
            elif metrics['trend_score'] >= 65:
                trend_status = "hausse"
            elif metrics['trend_score'] >= 45:
                trend_status = "stable"
            elif metrics['trend_score'] >= 30:
                trend_status = "baisse"
            else:
                trend_status = "forte baisse"
                
            summary['trend_status'][keyword] = trend_status
            
            # Points saillants
            if metrics['is_growing']:
                summary['highlights'].append(
                    f"'{keyword}' montre une tendance à la hausse avec {metrics['growth_rate']:.1f}% de croissance"
                )
            
            if metrics['is_seasonal']:
                summary['highlights'].append(
                    f"'{keyword}' présente des variations saisonnières (score: {metrics['seasonality_score']:.1f})"
                )
            
            if metrics['current_interest'] > 75:
                summary['highlights'].append(
                    f"'{keyword}' suscite un intérêt élevé actuellement ({metrics['current_interest']:.1f}/100)"
                )
        
        # Requêtes associées
        for keyword, queries in related_queries.items():
            top_rising = []
            if 'rising' in queries and not queries['rising'].empty:
                # Récupérer jusqu'à 5 requêtes montantes
                top_rising = queries['rising'].head(5).to_dict('records')
                
            top_related = []
            if 'top' in queries and not queries['top'].empty:
                # Récupérer jusqu'à 5 requêtes principales
                top_related = queries['top'].head(5).to_dict('records')
                
            summary['top_related_queries'][keyword] = {
                'rising': top_rising,
                'top': top_related
            }
        
        return summary
    
    def _calculate_overall_trend_score(self, results_by_timeframe: Dict[str, Dict[str, Any]]) -> float:
        """
        Calcule un score de tendance global en combinant plusieurs périodes.
        
        Args:
            results_by_timeframe: Résultats d'analyse par période
            
        Returns:
            Score de tendance global
        """
        scores = []
        weights = {
            'short_term': 0.5,  # Les tendances à court terme ont plus d'importance
            'medium_term': 0.3,
            'long_term': 0.2
        }
        
        for timeframe, results in results_by_timeframe.items():
            if 'error' in results:
                continue
                
            trend_metrics = results.get('trend_metrics', {})
            if not trend_metrics:
                continue
                
            # Prendre le premier mot-clé
            if not trend_metrics:
                continue
            first_keyword = next(iter(trend_metrics))
            metrics = trend_metrics.get(first_keyword, {})
            
            score = metrics.get('trend_score', 0)
            weight = weights.get(timeframe, 0.2)  # Poids par défaut
            
            scores.append((score, weight))
        
        if not scores:
            return 50  # Score neutre par défaut
            
        # Calcul de la moyenne pondérée
        total_score = sum(score * weight for score, weight in scores)
        total_weight = sum(weight for _, weight in scores)
        
        return total_score / total_weight if total_weight > 0 else 50
    
    def _is_product_trending(self, results_by_timeframe: Dict[str, Dict[str, Any]]) -> bool:
        """
        Détermine si un produit est en tendance.
        
        Args:
            results_by_timeframe: Résultats d'analyse par période
            
        Returns:
            True si le produit est en tendance, False sinon
        """
        short_term_results = results_by_timeframe.get('short_term', {})
        medium_term_results = results_by_timeframe.get('medium_term', {})
        
        if 'error' in short_term_results or 'error' in medium_term_results:
            return False
        
        # Analyse des métriques à court terme
        short_term_metrics = short_term_results.get('trend_metrics', {})
        if not short_term_metrics:
            return False
        
        if not short_term_metrics:
            return False
        first_keyword = next(iter(short_term_metrics))
        metrics = short_term_metrics.get(first_keyword, {})
        
        # Considéré comme tendance si croissance ET score élevés
        is_growing = metrics.get('is_growing', False)
        trend_score = metrics.get('trend_score', 0)
        
        return is_growing and trend_score >= 70
    
    def _detect_seasonality(self, results_by_timeframe: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Détecte les motifs saisonniers dans les données.
        
        Args:
            results_by_timeframe: Résultats d'analyse par période
            
        Returns:
            Informations sur la saisonnalité
        """
        long_term_results = results_by_timeframe.get('long_term', {})
        five_year_results = results_by_timeframe.get('five_years', {})
        
        # Préférer l'analyse sur 5 ans si disponible
        results = five_year_results if 'error' not in five_year_results and five_year_results else long_term_results
        
        if 'error' in results:
            return {
                'is_seasonal': False,
                'confidence': 0,
                'pattern': 'unknown'
            }
        
        trend_metrics = results.get('trend_metrics', {})
        if not trend_metrics:
            return {
                'is_seasonal': False,
                'confidence': 0,
                'pattern': 'unknown'
            }
        
        if not trend_metrics:
            return {
                'is_seasonal': False,
                'confidence': 0,
                'pattern': 'unknown'
            }
        
        first_keyword = next(iter(trend_metrics))
        metrics = trend_metrics.get(first_keyword, {})
        
        is_seasonal = metrics.get('is_seasonal', False)
        seasonality_score = metrics.get('seasonality_score', 0)
        
        # Résultat simplifié
        return {
            'is_seasonal': is_seasonal,
            'confidence': seasonality_score / 100 if is_seasonal else 0,
            'pattern': 'annual' if is_seasonal else 'none'
        }
        
    def _generate_product_conclusion(self, results_by_timeframe: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère une conclusion pour l'analyse d'un produit.
        
        Args:
            results_by_timeframe: Résultats d'analyse par période
            
        Returns:
            Conclusion structurée
        """
        overall_score = self._calculate_overall_trend_score(results_by_timeframe)
        is_trending = self._is_product_trending(results_by_timeframe)
        seasonality = self._detect_seasonality(results_by_timeframe)
        
        if overall_score >= 75:
            opportunity_level = "Excellente"
            recommendation = "Ce produit montre un fort potentiel et est recommandé comme opportunité prioritaire."
        elif overall_score >= 60:
            opportunity_level = "Bonne"
            recommendation = "Ce produit présente un bon potentiel et mérite d'être considéré."
        elif overall_score >= 45:
            opportunity_level = "Moyenne"
            recommendation = "Ce produit présente un potentiel modéré. À considérer avec d'autres facteurs favorables."
        elif overall_score >= 30:
            opportunity_level = "Faible"
            recommendation = "Ce produit présente un faible potentiel. Non recommandé sauf circonstances particulières."
        else:
            opportunity_level = "Très faible"
            recommendation = "Ce produit ne présente pas de potentiel significatif. À éviter."
            
        timing_advice = "La tendance est stable. Aucune urgence particulière pour lancer ce produit."
        if is_trending:
            timing_advice = "La tendance est en hausse. C'est un bon moment pour lancer ce produit."
        
        if seasonality['is_seasonal']:
            if seasonality['pattern'] == 'annual':
                timing_advice += " Notez que ce produit présente une saisonnalité annuelle. Planifiez en conséquence."
        
        return {
            'opportunity_level': opportunity_level,
            'recommendation': recommendation,
            'timing_advice': timing_advice,
            'overall_score': overall_score,
            'key_points': []  # Points clés de l'analyse (simplifiés pour cette implémentation)
        }
