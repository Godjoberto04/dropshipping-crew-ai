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
    
    def _load_from_cache(self, cache_file: str, max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """
        Charge les données depuis le cache si disponibles et non expirées.
        
        Args:
            cache_file: Chemin du fichier de cache
            max_age_hours: Âge maximal du cache en heures
            
        Returns:
            Données du cache ou None si non disponibles ou expirées
        """
        if not os.path.exists(cache_file):
            return None
            
        # Vérification de l'âge du fichier
        file_age = time.time() - os.path.getmtime(cache_file)
        max_age_seconds = max_age_hours * 3600
        
        if file_age > max_age_seconds:
            logger.info(f"Cache expiré ({file_age/3600:.1f} heures) : {cache_file}")
            return None
            
        try:
            # Chargement du fichier de cache
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                
            logger.info(f"Données chargées depuis le cache : {cache_file}")
            return cached_data
            
        except Exception as e:
            logger.warning(f"Erreur lors du chargement du cache : {str(e)}")
            return None
    
    def _save_to_cache(self, cache_file: str, data: Dict[str, Any]) -> bool:
        """
        Sauvegarde les données dans le cache.
        
        Args:
            cache_file: Chemin du fichier de cache
            data: Données à mettre en cache
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            # Conversion des DataFrames pandas en format sérialisable
            serializable_data = {}
            
            for key, value in data.items():
                if isinstance(value, pd.DataFrame):
                    # Convertir le DataFrame en dictionnaire
                    serializable_data[key] = {
                        'type': 'dataframe',
                        'index': value.index.tolist(),
                        'columns': value.columns.tolist(),
                        'data': value.values.tolist()
                    }
                else:
                    serializable_data[key] = value
            
            # Sauvegarde dans le fichier de cache
            with open(cache_file, 'wb') as f:
                pickle.dump(serializable_data, f)
                
            logger.info(f"Données sauvegardées dans le cache : {cache_file}")
            return True
            
        except Exception as e:
            logger.warning(f"Erreur lors de la sauvegarde du cache : {str(e)}")
            return False

    def _calculate_trend_metrics(self, interest_over_time: pd.DataFrame, keywords: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Calcule les métriques de tendance à partir des données d'intérêt au fil du temps.
        
        Args:
            interest_over_time: DataFrame contenant les données d'intérêt au fil du temps
            keywords: Liste des mots-clés analysés
            
        Returns:
            Dictionnaire avec les métriques de tendance pour chaque mot-clé
        """
        trend_metrics = {}
        
        # Si les données sont vides, retourner un dictionnaire vide
        if interest_over_time.empty:
            for keyword in keywords:
                trend_metrics[keyword] = {
                    'current_interest': 0,
                    'average_interest': 0,
                    'growth_rate': 0,
                    'volatility': 0,
                    'momentum': 0,
                    'trend_score': 0,
                    'is_growing': False,
                    'is_seasonal': False
                }
            return trend_metrics
        
        # Pour chaque mot-clé, calculer les métriques
        for keyword in keywords:
            if keyword not in interest_over_time.columns:
                logger.warning(f"Mot-clé {keyword} non trouvé dans les données d'intérêt")
                trend_metrics[keyword] = {
                    'current_interest': 0,
                    'average_interest': 0,
                    'growth_rate': 0,
                    'volatility': 0,
                    'momentum': 0,
                    'trend_score': 0,
                    'is_growing': False,
                    'is_seasonal': False
                }
                continue
                
            # Extraction des données pour ce mot-clé
            keyword_data = interest_over_time[keyword].dropna()
            
            if len(keyword_data) < 2:
                logger.warning(f"Données insuffisantes pour le mot-clé {keyword}")
                trend_metrics[keyword] = {
                    'current_interest': keyword_data.iloc[-1] if len(keyword_data) == 1 else 0,
                    'average_interest': keyword_data.mean() if len(keyword_data) == 1 else 0,
                    'growth_rate': 0,
                    'volatility': 0,
                    'momentum': 0,
                    'trend_score': 0,
                    'is_growing': False,
                    'is_seasonal': False
                }
                continue
            
            # Calcul de l'intérêt actuel (dernière valeur)
            current_interest = keyword_data.iloc[-1]
            
            # Calcul de l'intérêt moyen
            average_interest = keyword_data.mean()
            
            # Calcul du taux de croissance
            start_value = keyword_data.iloc[0]
            end_value = keyword_data.iloc[-1]
            growth_rate = ((end_value - start_value) / max(1, start_value)) * 100
            
            # Calcul de la volatilité (écart-type normalisé)
            volatility = keyword_data.std() / max(1, average_interest) * 100
            
            # Calcul du momentum (moyenne des 3 derniers points vs précédents)
            momentum = 0
            if len(keyword_data) >= 6:
                recent_avg = keyword_data.iloc[-3:].mean()
                previous_avg = keyword_data.iloc[-6:-3].mean()
                momentum = ((recent_avg - previous_avg) / max(1, previous_avg)) * 100
            
            # Détection de la saisonnalité (simplifié)
            is_seasonal = False
            seasonal_score = 0
            if len(keyword_data) >= 52:  # Au moins un an de données
                try:
                    # Test simple d'autocorrélation avec décalage de 52 semaines (1 an)
                    lag = 52
                    if len(keyword_data) > lag:
                        shifted_data = keyword_data.shift(lag).dropna()
                        correlation = keyword_data.iloc[-len(shifted_data):].corr(shifted_data)
                        if correlation > 0.5:  # Corrélation forte indique la saisonnalité
                            is_seasonal = True
                            seasonal_score = correlation * 100
                except Exception as e:
                    logger.warning(f"Erreur lors du calcul de la saisonnalité pour {keyword}: {str(e)}")
            
            # Calcul global du score de tendance
            # Ce score combine plusieurs métriques pour évaluer l'intérêt global pour un mot-clé
            trend_score = self._calculate_trend_score(
                current_interest=current_interest,
                growth_rate=growth_rate,
                volatility=volatility,
                momentum=momentum,
                average_interest=average_interest
            )
            
            # Détection de croissance
            is_growing = growth_rate > 5 or momentum > 10
            
            # Organisation des métriques pour ce mot-clé
            trend_metrics[keyword] = {
                'current_interest': current_interest,
                'average_interest': average_interest,
                'growth_rate': growth_rate,
                'volatility': volatility,
                'momentum': momentum,
                'is_growing': is_growing,
                'is_seasonal': is_seasonal,
                'seasonality_score': seasonal_score,
                'trend_score': trend_score
            }
        
        return trend_metrics
    
    def _calculate_trend_score(
        self,
        current_interest: float,
        growth_rate: float,
        volatility: float,
        momentum: float,
        average_interest: float
    ) -> float:
        """
        Calcule un score de tendance global.
        
        Args:
            current_interest: Intérêt actuel
            growth_rate: Taux de croissance
            volatility: Volatilité (plus bas est meilleur)
            momentum: Momentum récent
            average_interest: Intérêt moyen
            
        Returns:
            Score global (0-100)
        """
        # Normalisation des valeurs d'entrée
        norm_current = min(100, current_interest)
        
        # Normalisation du taux de croissance (-100% à +100% -> 0-100)
        norm_growth = 50  # Valeur par défaut pour une croissance neutre
        if growth_rate > 100:
            norm_growth = 100
        elif growth_rate > 50:
            norm_growth = 90
        elif growth_rate > 25:
            norm_growth = 80
        elif growth_rate > 10:
            norm_growth = 70
        elif growth_rate > 0:
            norm_growth = 60
        elif growth_rate > -10:
            norm_growth = 40
        elif growth_rate > -25:
            norm_growth = 30
        elif growth_rate > -50:
            norm_growth = 20
        else:
            norm_growth = 10
        
        # Normalisation de la volatilité (inversée, moins = mieux)
        # 0% = 100 points, 100% = 0 points
        norm_volatility = max(0, 100 - volatility)
        
        # Normalisation du momentum
        norm_momentum = 50  # Valeur par défaut pour un momentum neutre
        if momentum > 50:
            norm_momentum = 100
        elif momentum > 25:
            norm_momentum = 90
        elif momentum > 10:
            norm_momentum = 80
        elif momentum > 0:
            norm_momentum = 70
        elif momentum > -10:
            norm_momentum = 40
        elif momentum > -25:
            norm_momentum = 30
        else:
            norm_momentum = 20
        
        # Calcul de la moyenne pondérée
        score = (
            (norm_current * 0.3) +      # Intérêt actuel: 30%
            (norm_growth * 0.3) +        # Croissance: 30%
            (norm_volatility * 0.1) +    # Volatilité: 10%
            (norm_momentum * 0.3)        # Momentum: 30%
        )
        
        return score

    def _is_likely_product(self, query: str) -> bool:
        """
        Détermine si une requête est probablement un produit et non une requête générique.
        
        Args:
            query: Requête à analyser
            
        Returns:
            True si la requête semble être un produit, False sinon
        """
        # Mots-clés qui indiquent généralement une requête et non un produit
        generic_terms = ['comment', 'pourquoi', 'quand', 'quoi', 'qui', 'où', 'quel', 'quelle', 
                         'how', 'why', 'when', 'what', 'who', 'where', 'which']
        
        # Vérification des mots génériques
        for term in generic_terms:
            if term in query.lower().split():
                return False
                
        # Vérification de la longueur (les produits ont généralement des noms plus longs)
        if len(query.split()) <= 1:
            return False
            
        # Un produit a souvent un nom et une caractéristique
        return True
        
    def _get_category_keywords(self, category: str = None) -> List[str]:
        """
        Obtient les mots-clés liés à une catégorie.
        
        Args:
            category: Catégorie de produits
            
        Returns:
            Liste de mots-clés liés à la catégorie
        """
        if not category:
            return ["trending products", "best selling products", "popular products"]
            
        # Mots-clés spécifiques par catégorie
        category_keywords = {
            "fashion": ["fashion trends", "clothing trends", "accessories trends"],
            "electronics": ["tech gadgets", "electronics trends", "smart devices"],
            "home": ["home decor trends", "furniture trends", "home improvement"],
            "beauty": ["beauty products", "skincare trends", "makeup trends"],
            "fitness": ["fitness equipment", "workout gear", "exercise trends"],
            "toys": ["toys trends", "games trends", "children gifts"],
            "jewelry": ["jewelry trends", "watches trends", "accessories"]
        }
        
        # Recherche de la correspondance la plus proche
        for key, keywords in category_keywords.items():
            if key in category.lower():
                return [category] + keywords
                
        # Catégorie non reconnue, retourner des mots-clés génériques avec la catégorie
        return [category, f"{category} trends", f"{category} products", "popular products"]
