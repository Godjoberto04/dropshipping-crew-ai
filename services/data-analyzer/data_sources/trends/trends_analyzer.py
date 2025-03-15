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
            # Préparation des données pour l'analyse
            df = pd.DataFrame({'value': keyword_data})
            df['month'] = df.index.month
            df['year'] = df.index.year
            
            # Calcul des moyennes mensuelles par année
            monthly_avg = df.groupby(['year', 'month'])['value'].mean().reset_index()
            
            # Calcul des moyennes globales par mois (toutes années confondues)
            global_monthly_avg = monthly_avg.groupby('month')['value'].mean()
            
            # Nombre d'années uniques dans les données
            unique_years = df['year'].nunique()
            
            # Si moins de 2 ans de données, confiance faible
            if unique_years < 2:
                return seasonality_result
            
            # Calcul des pics saisonniers (mois avec valeur > moyenne + 10%)
            global_mean = global_monthly_avg.mean()
            peak_threshold = global_mean * 1.1
            peak_months_indices = global_monthly_avg[global_monthly_avg > peak_threshold].index.tolist()
            
            # Conversion des indices de mois en noms de mois
            month_names = {
                1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 
                5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août', 
                9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
            }
            
            peak_months = [month_names[m] for m in peak_months_indices]
            
            # Calcul du coefficient de variation mensuel (pour mesurer la consistance année après année)
            monthly_cv = df.groupby('month')['value'].std() / df.groupby('month')['value'].mean()
            avg_cv = monthly_cv.mean()
            
            # Calcul du score de saisonnalité (inverse du coefficient de variation)
            seasonality_score = max(0, min(100, 100 * (1 - avg_cv)))
            
            # Détection d'autocorrélation annuelle
            autocorrelation = None
            if len(keyword_data) > 52:
                # Extraction des données sans NaN
                clean_data = keyword_data.dropna()
                
                if len(clean_data) > 52:
                    # Calculer la corrélation entre la série et elle-même décalée d'un an
                    # Cette méthode est simplifiée, une analyse plus sophistiquée utiliserait
                    # des techniques comme la décomposition de série temporelle
                    shifted_data = clean_data.shift(52)
                    common_indices = clean_data.index.intersection(shifted_data.dropna().index)
                    
                    if len(common_indices) >= 26:  # Au moins 6 mois de données communes
                        autocorrelation = clean_data.loc[common_indices].corr(shifted_data.loc[common_indices])
            
            # Détermination de la saisonnalité
            is_seasonal = False
            confidence = 'low'
            
            # Critères pour la saisonnalité:
            # 1. Présence de pics mensuels significatifs
            # 2. Autocorrélation annuelle élevée (si disponible)
            # 3. Coefficient de variation assez bas (consistance)
            
            if len(peak_months) >= 1 and seasonality_score > 60:
                is_seasonal = True
                confidence = 'medium'
                
                # Améliorer la confiance si l'autocorrélation est élevée
                if autocorrelation is not None and autocorrelation > 0.5:
                    confidence = 'high'
                    seasonality_score = min(100, seasonality_score + 20)  # Bonus au score
            
            # Génération de la description du motif
            pattern_description = ''
            if is_seasonal:
                if len(peak_months) == 1:
                    pattern_description = f"Pic d'intérêt annuel en {peak_months[0]}"
                elif len(peak_months) == 2:
                    pattern_description = f"Pics d'intérêt en {peak_months[0]} et {peak_months[1]}"
                else:
                    joined_months = ", ".join(peak_months[:-1]) + f" et {peak_months[-1]}"
                    pattern_description = f"Pics d'intérêt multiples durant l'année ({joined_months})"
                    
                if confidence == 'high':
                    pattern_description += " avec une forte consistance année après année"
            
            # Construction du résultat
            seasonality_result = {
                'is_seasonal': is_seasonal,
                'seasonality_score': seasonality_score,
                'peak_months': peak_months,
                'pattern_description': pattern_description,
                'confidence': confidence
            }
            
            return seasonality_result
            
        except Exception as e:
            logger.warning(f"Erreur lors de la détection de saisonnalité: {str(e)}", exc_info=True)
            return seasonality_result

    def _generate_product_conclusion(self, results_by_timeframe: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère une conclusion globale pour l'analyse d'un produit.
        
        Args:
            results_by_timeframe: Résultats d'analyse par période
            
        Returns:
            Dictionnaire avec les conclusions
        """
        conclusion = {
            'overall_assessment': '',
            'recommendation': '',
            'key_insights': [],
            'considerations': [],
            'confidence': 'medium'
        }
        
        # Variables de synthèse
        short_term_growing = False
        medium_term_growing = False
        is_seasonal = False
        seasonality_info = {}
        trend_score = 0
        
        # Vérification des périodes et extraction des métriques clés
        for timeframe, results in results_by_timeframe.items():
            if 'error' in results or 'trend_metrics' not in results:
                continue
                
            trend_metrics = results.get('trend_metrics', {})
            if not trend_metrics:
                continue
                
            # Prendre le premier mot-clé (normalement un seul pour analyze_product)
            keyword = list(trend_metrics.keys())[0]
            metrics = trend_metrics[keyword]
            
            if timeframe == 'short_term':
                short_term_growing = metrics.get('is_growing', False)
                
            if timeframe == 'medium_term':
                medium_term_growing = metrics.get('is_growing', False)
                
            if timeframe in ('long_term', 'five_years'):
                is_seasonal = metrics.get('is_seasonal', False)
                if is_seasonal:
                    seasonality_info = {
                        'peak_months': results_by_timeframe.get('seasonality', {}).get('peak_months', []),
                        'score': metrics.get('seasonality_score', 0)
                    }
        
        # Récupération du score de tendance global (déjà calculé)
        trend_score = results_by_timeframe.get('overall_trend_score', 0)
        if not isinstance(trend_score, (int, float)):
            try:
                trend_score = float(trend_score)
            except (ValueError, TypeError):
                trend_score = 0
                
        # Détermination du niveau de confiance
        confidence_level = 'medium'  # Valeur par défaut
        analysis_count = sum(1 for r in results_by_timeframe.values() if 'error' not in r)
        if analysis_count >= 3:
            confidence_level = 'high'
        elif analysis_count <= 1:
            confidence_level = 'low'
            
        # Génération de l'évaluation globale
        overall_assessment = ""
        if trend_score >= 75:
            overall_assessment = "Produit à fort potentiel avec un intérêt soutenu."
        elif trend_score >= 60:
            overall_assessment = "Produit avec un bon potentiel et un intérêt significatif."
        elif trend_score >= 45:
            overall_assessment = "Produit avec un potentiel modéré et un intérêt stable."
        elif trend_score >= 30:
            overall_assessment = "Produit avec un potentiel limité et un intérêt faible."
        else:
            overall_assessment = "Produit à faible potentiel avec un intérêt minimal."
            
        # Génération de la recommandation
        recommendation = ""
        if trend_score >= 75 and short_term_growing:
            recommendation = "Fortement recommandé pour le dropshipping. Ce produit montre un fort intérêt et une tendance croissante."
        elif trend_score >= 60 and (short_term_growing or medium_term_growing):
            recommendation = "Recommandé pour le dropshipping. Ce produit présente un bon niveau d'intérêt et une tendance positive."
        elif trend_score >= 60 and is_seasonal:
            peak_months_str = ", ".join(seasonality_info.get('peak_months', []))
            recommendation = f"Recommandé pour le dropshipping saisonnier. Ce produit présente un fort intérêt saisonnier, particulièrement en {peak_months_str}."
        elif trend_score >= 45:
            recommendation = "Peut être considéré pour le dropshipping avec prudence. Ce produit présente un intérêt modéré."
        else:
            recommendation = "Non recommandé pour le dropshipping. Ce produit présente un intérêt insuffisant pour être rentable."
            
        # Génération des insights clés
        key_insights = []
        
        if short_term_growing and medium_term_growing:
            key_insights.append("Croissance soutenue sur le court et moyen terme, indiquant une tendance solide.")
        elif short_term_growing:
            key_insights.append("Croissance récente, potentiellement une tendance émergente.")
        elif not short_term_growing and not medium_term_growing and trend_score >= 60:
            key_insights.append("Intérêt stable et significatif, indiquant un produit établi.")
            
        if is_seasonal:
            peak_months_str = ", ".join(seasonality_info.get('peak_months', []))
            key_insights.append(f"Produit saisonnier avec des pics d'intérêt en {peak_months_str}.")
            
        # Génération des considérations
        considerations = []
        
        if is_seasonal:
            considerations.append("Planifier les stocks et le marketing en fonction de la saisonnalité identifiée.")
            
        if short_term_growing and not medium_term_growing:
            considerations.append("La croissance récente pourrait être temporaire. Surveiller l'évolution avant d'investir massivement.")
            
        if not short_term_growing and not medium_term_growing and trend_score >= 45:
            considerations.append("Le marché semble stable. Considérer la différenciation pour se démarquer de la concurrence.")
            
        if trend_score < 45:
            considerations.append("Le faible intérêt général suggère un marché de niche. Évaluer la concurrence et les marges.")
            
        # Construction du résultat final
        conclusion['overall_assessment'] = overall_assessment
        conclusion['recommendation'] = recommendation
        conclusion['key_insights'] = key_insights
        conclusion['considerations'] = considerations
        conclusion['confidence'] = confidence_level
        
        return conclusion
    
    def _get_cache_file_path(self, keywords: List[str], timeframe: str, geo: str, category: int) -> str:
        """
        Génère le chemin du fichier de cache pour une requête spécifique.
        
        Args:
            keywords: Liste des mots-clés
            timeframe: Période d'analyse
            geo: Zone géographique
            category: ID de catégorie
            
        Returns:
            Chemin du fichier de cache
        """
        # Tri des mots-clés pour assurer la cohérence du cache quelle que soit leur ordre
        sorted_keywords = sorted(keywords)
        
        # Création d'une chaîne représentant les paramètres de la requête
        params_str = f"{'-'.join(sorted_keywords)}_{timeframe}_{geo or 'all'}_{category}"
        
        # Création d'un hash pour éviter les problèmes de caractères spéciaux dans les noms de fichiers
        params_hash = hashlib.md5(params_str.encode('utf-8')).hexdigest()
        
        # Construction du chemin complet
        cache_file = os.path.join(self.cache_dir, f"trends_{params_hash}.pkl")
        
        return cache_file
