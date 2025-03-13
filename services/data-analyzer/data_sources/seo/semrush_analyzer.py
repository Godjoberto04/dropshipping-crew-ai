#!/usr/bin/env python3
"""
Module d'analyse SEO via l'API SEMrush.
Permet d'obtenir des données sur le volume de recherche, la difficulté des mots-clés,
la concurrence, etc.
"""

import os
import json
import time
import requests
import pandas as pd
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
from urllib.parse import quote
import hashlib
import datetime
import random

from config import settings, get_logger

logger = get_logger("semrush_analyzer")

class SEMrushAnalyzer:
    """Classe d'analyse SEO via l'API SEMrush."""
    
    # Endpoints de l'API SEMrush
    API_URL = "https://api.semrush.com"
    KEYWORD_ANALYTICS_ENDPOINT = "/analytics/keywordanalysis/v1/"
    KEYWORD_OVERVIEW_ENDPOINT = "/analytics/keywordoverview/v1/"
    DOMAIN_OVERVIEW_ENDPOINT = "/analytics/domainoverview/v1/"
    RELATED_KEYWORDS_ENDPOINT = "/keywords/related/"
    
    # Bases de données par pays
    DATABASES = {
        'us': 'us',
        'uk': 'uk',
        'ca': 'ca',
        'fr': 'fr',
        'de': 'de',
        'es': 'es',
        'it': 'it',
        'br': 'br',
        'au': 'au',
        'ru': 'ru',
        'jp': 'jp',
        'in': 'in',
        'cn': 'cn',
    }
    
    def __init__(
        self,
        api_key: str = None,
        rate_limit: int = None,
        daily_limit: int = None,
        cache_dir: str = None,
    ):
        """
        Initialise l'analyseur SEMrush.
        
        Args:
            api_key: Clé API SEMrush
            rate_limit: Limite de requêtes par seconde
            daily_limit: Limite quotidienne de requêtes
            cache_dir: Répertoire de cache
        """
        self.api_key = api_key or getattr(settings, 'SEMRUSH_API_KEY', None)
        self.rate_limit = rate_limit or getattr(settings, 'SEMRUSH_RATE_LIMIT', 5)
        self.daily_limit = daily_limit or getattr(settings, 'SEMRUSH_DAILY_LIMIT', 500)
        
        # Vérification de la clé API
        if not self.api_key:
            logger.warning("Aucune clé API SEMrush fournie. L'analyseur fonctionnera en mode simulation.")
            self._simulation_mode = True
        else:
            self._simulation_mode = False
        
        # Répertoire de cache
        self.cache_dir = cache_dir or os.path.join(settings.CACHE_DIR, 'semrush')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # État de la limite
        self._last_request_time = 0
        self._daily_requests = 0
        self._daily_reset_date = datetime.datetime.now().date()
        
        logger.info(f"SEMrushAnalyzer initialisé (simulation_mode: {self._simulation_mode})")
    
    def _reset_daily_counter(self):
        """Réinitialise le compteur quotidien si nécessaire."""
        current_date = datetime.datetime.now().date()
        if current_date > self._daily_reset_date:
            self._daily_requests = 0
            self._daily_reset_date = current_date
            logger.debug("Compteur quotidien de requêtes SEMrush réinitialisé")
    
    def _respect_rate_limit(self):
        """Respecte la limite de requêtes par seconde."""
        if self._simulation_mode:
            return
            
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        
        # Si moins d'une seconde s'est écoulée depuis la dernière requête
        if elapsed < (1.0 / self.rate_limit):
            sleep_time = (1.0 / self.rate_limit) - elapsed
            time.sleep(sleep_time)
            
        self._last_request_time = time.time()
    
    def _check_daily_limit(self):
        """
        Vérifie si la limite quotidienne est atteinte.
        
        Returns:
            bool: True si la limite n'est pas atteinte, False sinon
        """
        if self._simulation_mode:
            return True
            
        self._reset_daily_counter()
        
        if self._daily_requests >= self.daily_limit:
            logger.warning(f"Limite quotidienne de requêtes SEMrush atteinte ({self.daily_limit})")
            return False
            
        return True
    
    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """
        Génère une clé de cache à partir des paramètres.
        
        Args:
            endpoint: Endpoint de l'API
            params: Paramètres de la requête
            
        Returns:
            str: Clé de cache
        """
        # On retire la clé API des paramètres pour le cache
        cache_params = params.copy()
        if 'key' in cache_params:
            del cache_params['key']
            
        # Création d'une chaîne pour la clé de cache
        param_str = json.dumps(cache_params, sort_keys=True)
        key_base = f"{endpoint}_{param_str}"
        
        # Hachage pour un nom de fichier plus court
        hashed_key = hashlib.md5(key_base.encode()).hexdigest()
        
        return hashed_key
    
    def _get_cache_file(self, cache_key: str) -> str:
        """
        Génère le chemin du fichier de cache.
        
        Args:
            cache_key: Clé de cache
            
        Returns:
            str: Chemin du fichier de cache
        """
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any], cache_duration: int = 24*60*60):
        """
        Sauvegarde les données dans le cache.
        
        Args:
            cache_key: Clé de cache
            data: Données à sauvegarder
            cache_duration: Durée de validité du cache en secondes (défaut: 24h)
        """
        try:
            cache_file = self._get_cache_file(cache_key)
            
            # Ajout des métadonnées de cache
            cache_data = {
                'data': data,
                'timestamp': time.time(),
                'expiry': time.time() + cache_duration
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False)
                
            logger.debug(f"Données sauvegardées dans le cache: {cache_key}")
                
        except Exception as e:
            logger.warning(f"Erreur lors de la sauvegarde du cache: {str(e)}")
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Charge des données depuis le cache si elles sont valides.
        
        Args:
            cache_key: Clé de cache
            
        Returns:
            Dict ou None: Données du cache si valides, None sinon
        """
        try:
            cache_file = self._get_cache_file(cache_key)
            
            if not os.path.exists(cache_file):
                return None
                
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Vérification de l'expiration
            if time.time() > cache_data.get('expiry', 0):
                logger.debug(f"Cache expiré: {cache_key}")
                return None
                
            logger.debug(f"Données chargées depuis le cache: {cache_key}")
            return cache_data.get('data')
            
        except Exception as e:
            logger.warning(f"Erreur lors du chargement du cache: {str(e)}")
            return None
    
    def _api_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        use_cache: bool = True,
        cache_duration: int = 24*60*60
    ) -> Dict[str, Any]:
        """
        Effectue une requête à l'API SEMrush avec gestion du cache et des limites.
        
        Args:
            endpoint: Endpoint de l'API
            params: Paramètres de la requête
            use_cache: Utiliser le cache si disponible
            cache_duration: Durée de validité du cache en secondes
            
        Returns:
            dict: Données de réponse
            
        Raises:
            Exception: Si la requête échoue
        """
        # Génération de la clé de cache
        cache_key = self._get_cache_key(endpoint, params)
        
        # Vérification du cache
        if use_cache:
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        # Mode simulation : générer des données fictives
        if self._simulation_mode:
            logger.info(f"Mode simulation: génération de données fictives pour {endpoint}")
            simulated_data = self._generate_simulated_data(endpoint, params)
            
            if use_cache:
                self._save_to_cache(cache_key, simulated_data, cache_duration)
                
            return simulated_data
        
        # Vérification des limites
        if not self._check_daily_limit():
            raise Exception("Limite quotidienne de requêtes SEMrush atteinte")
            
        self._respect_rate_limit()
        
        # Ajout de la clé API
        params['key'] = self.api_key
        
        # Construction de l'URL
        url = f"{self.API_URL}{endpoint}"
        
        try:
            # Exécution de la requête
            response = requests.get(url, params=params)
            self._daily_requests += 1
            
            # Vérification de la réponse
            if response.status_code != 200:
                logger.error(f"Erreur API SEMrush: {response.status_code} - {response.text}")
                raise Exception(f"Erreur API SEMrush: {response.status_code} - {response.text}")
            
            # Traitement de la réponse
            data = response.json()
            
            # Mise en cache
            if use_cache:
                self._save_to_cache(cache_key, data, cache_duration)
                
            return data
            
        except requests.RequestException as e:
            logger.error(f"Erreur de requête SEMrush: {str(e)}")
            raise Exception(f"Erreur de requête SEMrush: {str(e)}")
    
    def _generate_simulated_data(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère des données simulées pour le mode sans API.
        
        Args:
            endpoint: Endpoint de l'API
            params: Paramètres de la requête
            
        Returns:
            dict: Données simulées
        """
        # Récupération du mot-clé des paramètres
        keyword = params.get('phrase') or params.get('keyword') or "unknown"
        
        # Génération d'un hash déterministe basé sur le mot-clé pour des résultats cohérents
        keyword_hash = abs(hash(keyword))
        
        if self.KEYWORD_OVERVIEW_ENDPOINT in endpoint:
            # Simulation de données de vue d'ensemble de mot-clé
            word_count = len(keyword.split())
            length_modifier = (len(keyword) % 10) / 10  # Modificateur basé sur la longueur (0-1)
            
            # Volume calculé de manière pseudo-aléatoire mais déterministe
            base_volume = 500 + (keyword_hash % 9500)  # Volume entre 500 et 10000
            
            # Les mots-clés plus longs ont généralement un volume plus faible
            volume = int(base_volume * (1.2 - (word_count * 0.1) - length_modifier))
            volume = max(10, min(50000, volume))  # Limites de 10 à 50000
            
            # CPC calculé entre 0.1 et 10.0 euros
            cpc = 0.1 + ((keyword_hash % 99) / 10)
            
            # Difficulté de 1 à 100, influencée par le volume et le CPC
            difficulty = min(100, int(20 + (volume / 500) + (cpc * 5) + (keyword_hash % 20)))
            
            # Résultats pour une recherche - Généralement corrélés avec la popularité
            results_count = volume * (100 + (keyword_hash % 900))
            
            # Tendance (-50 à +50)
            trend = (keyword_hash % 100) - 50
            
            # Concurrence (0.0 à 1.0)
            competition = min(1.0, (difficulty / 100) * (0.5 + (keyword_hash % 50) / 100))
            
            return {
                'keyword': keyword,
                'volume': volume,
                'cpc': round(cpc, 2),
                'difficulty': difficulty,
                'results_count': results_count,
                'trend': trend,
                'competition': round(competition, 2),
                'simulated': True
            }
            
        elif self.RELATED_KEYWORDS_ENDPOINT in endpoint:
            # Simulation de mots-clés associés
            related_keywords = []
            
            # Générer quelques variantes du mot-clé
            base_words = keyword.split()
            
            # Préfixes et suffixes couramment utilisés
            prefixes = ["best", "top", "cheap", "premium", "professional", "new", "buy", "review", "compare"]
            suffixes = ["online", "shop", "2023", "guide", "for beginners", "vs", "alternative", "near me"]
            
            # Générer des variantes avec préfixes
            for prefix in prefixes[:3 + (keyword_hash % 3)]:  # 3-5 préfixes
                modified = f"{prefix} {keyword}"
                
                # Volume et CPC des variantes
                related_volume = max(10, volume // (2 + (hash(modified) % 8)))
                related_cpc = max(0.1, cpc * (0.7 + (hash(modified) % 6) / 10))
                related_difficulty = max(1, min(100, difficulty + ((hash(modified) % 40) - 20)))
                
                related_keywords.append({
                    'keyword': modified,
                    'volume': related_volume,
                    'cpc': round(related_cpc, 2),
                    'difficulty': related_difficulty,
                    'simulated': True
                })
            
            # Générer des variantes avec suffixes
            for suffix in suffixes[:2 + (keyword_hash % 4)]:  # 2-5 suffixes
                modified = f"{keyword} {suffix}"
                
                # Volume et CPC des variantes
                related_volume = max(10, volume // (2 + (hash(modified) % 8)))
                related_cpc = max(0.1, cpc * (0.7 + (hash(modified) % 6) / 10))
                related_difficulty = max(1, min(100, difficulty + ((hash(modified) % 40) - 20)))
                
                related_keywords.append({
                    'keyword': modified,
                    'volume': related_volume,
                    'cpc': round(related_cpc, 2),
                    'difficulty': related_difficulty,
                    'simulated': True
                })
            
            return {
                'related_keywords': related_keywords,
                'count': len(related_keywords),
                'simulated': True
            }
            
        else:
            # Données génériques pour les autres endpoints
            return {
                'endpoint': endpoint,
                'params': params,
                'simulated': True,
                'message': "Données simulées génériques pour cet endpoint"
            }
    
    def analyze_keyword(
        self,
        keyword: str,
        database: str = 'fr',
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Analyse un mot-clé spécifique.
        
        Args:
            keyword: Mot-clé à analyser
            database: Base de données SEMrush (pays)
            use_cache: Utiliser le cache si disponible
            
        Returns:
            dict: Données d'analyse du mot-clé
            
        Raises:
            ValueError: Si les paramètres sont invalides
            Exception: Si l'analyse échoue
        """
        if not keyword:
            raise ValueError("Le mot-clé ne peut pas être vide")
            
        # Normalisation de la base de données
        if database.lower() in self.DATABASES:
            database = self.DATABASES[database.lower()]
        
        logger.info(f"Analyse du mot-clé: '{keyword}' (base de données: {database})")
        
        try:
            # Requête à l'API
            params = {
                'phrase': keyword,
                'database': database,
                'export_columns': 'Ph,Nq,Cp,Co,Nr'  # Colonnes: Keyword, Volume, CPC, Competition, Results
            }
            
            data = self._api_request(
                self.KEYWORD_OVERVIEW_ENDPOINT,
                params,
                use_cache=use_cache
            )
            
            # Traitement et standardisation des données
            result = self._process_keyword_data(data)
            
            # Ajout d'informations supplémentaires
            result['database'] = database
            result['timestamp'] = time.time()
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du mot-clé '{keyword}': {str(e)}")
            raise
    
    def analyze_keywords(
        self,
        keywords: List[str],
        database: str = 'fr',
        use_cache: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyse plusieurs mots-clés.
        
        Args:
            keywords: Liste de mots-clés à analyser
            database: Base de données SEMrush (pays)
            use_cache: Utiliser le cache si disponible
            
        Returns:
            dict: Dictionnaire avec un mot-clé comme clé et les données d'analyse comme valeur
            
        Raises:
            ValueError: Si les paramètres sont invalides
            Exception: Si l'analyse échoue
        """
        if not keywords:
            raise ValueError("La liste de mots-clés ne peut pas être vide")
            
        logger.info(f"Analyse de {len(keywords)} mots-clés (base de données: {database})")
        
        results = {}
        
        for keyword in keywords:
            try:
                results[keyword] = self.analyze_keyword(keyword, database, use_cache)
            except Exception as e:
                logger.warning(f"Erreur lors de l'analyse de '{keyword}': {str(e)}")
                results[keyword] = {'error': str(e)}
        
        return results
    
    def get_competitors(
        self,
        keyword: str,
        database: str = 'fr',
        limit: int = 10,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtient les principaux concurrents pour un mot-clé.
        
        Args:
            keyword: Mot-clé à analyser
            database: Base de données SEMrush (pays)
            limit: Nombre maximum de concurrents à retourner
            use_cache: Utiliser le cache si disponible
            
        Returns:
            list: Liste des concurrents avec leurs données
            
        Raises:
            ValueError: Si les paramètres sont invalides
            Exception: Si l'analyse échoue
        """
        if not keyword:
            raise ValueError("Le mot-clé ne peut pas être vide")
            
        # Cette fonctionnalité nécessite un endpoint spécifique qui n'est pas simulé ici
        # Dans une implémentation réelle, il faudrait interroger l'API SEMrush appropriée
        
        if self._simulation_mode:
            # En mode simulation, retourner des données fictives
            competitor_domains = [
                f"competitor{i}.com" for i in range(1, min(limit + 1, 10))
            ]
            
            competitors = []
            for domain in competitor_domains:
                keyword_hash = hash(keyword + domain)
                
                # Simulation de données pour chaque concurrent
                competitors.append({
                    'domain': domain,
                    'visibility': round(10 + (keyword_hash % 90), 1),
                    'traffic': 1000 + (keyword_hash % 9000),
                    'keywords': 100 + (keyword_hash % 900),
                    'position': 1 + (keyword_hash % 10),
                    'simulated': True
                })
            
            return competitors
        
        # Implémentation réelle avec l'API SEMrush
        # (à implémenter lorsque l'accès à l'API sera disponible)
        raise NotImplementedError("Cette fonctionnalité nécessite un accès à l'API SEMrush")
    
    def get_keyword_suggestions(
        self,
        keyword: str,
        database: str = 'fr',
        limit: int = 20,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtient des suggestions de mots-clés associés.
        
        Args:
            keyword: Mot-clé de base
            database: Base de données SEMrush (pays)
            limit: Nombre maximum de suggestions à retourner
            use_cache: Utiliser le cache si disponible
            
        Returns:
            list: Liste des mots-clés suggérés avec leurs données
            
        Raises:
            ValueError: Si les paramètres sont invalides
            Exception: Si l'analyse échoue
        """
        if not keyword:
            raise ValueError("Le mot-clé ne peut pas être vide")
            
        # Normalisation de la base de données
        if database.lower() in self.DATABASES:
            database = self.DATABASES[database.lower()]
        
        logger.info(f"Recherche de suggestions pour: '{keyword}' (base de données: {database})")
        
        try:
            # Requête à l'API
            params = {
                'phrase': keyword,
                'database': database,
                'limit': limit
            }
            
            data = self._api_request(
                self.RELATED_KEYWORDS_ENDPOINT,
                params,
                use_cache=use_cache
            )
            
            # Extraction des suggestions de mots-clés
            if self._simulation_mode:
                suggestions = data.get('related_keywords', [])
            else:
                # Traitement de la réponse réelle de l'API SEMrush
                # À adapter selon le format de réponse de l'API
                suggestions = data.get('data', [])
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de suggestions pour '{keyword}': {str(e)}")
            raise
    
    def _process_keyword_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite et standardise les données de mot-clé.
        
        Args:
            data: Données brutes de l'API
            
        Returns:
            dict: Données traitées et standardisées
        """
        # Si c'est déjà au format standard, le retourner tel quel
        if 'keyword' in data and 'volume' in data:
            return data
            
        # Sinon, convertir au format standard
        result = {
            'keyword': data.get('Ph') or data.get('phrase') or data.get('keyword', 'unknown'),
            'volume': int(data.get('Nq') or data.get('volume', 0)),
            'cpc': float(data.get('Cp') or data.get('cpc', 0.0)),
            'competition': float(data.get('Co') or data.get('competition', 0.0)),
            'results_count': int(data.get('Nr') or data.get('results_count', 0)),
        }
        
        # Conversion de la compétition de 0-1 à 0-100 pour harmoniser avec d'autres métriques
        result['competition_score'] = int(result['competition'] * 100)
        
        # Calcul de la difficulté SEO (0-100) si non fourni
        # Formula simplifiée: (volume^0.3 * competition * 20) limité à 100
        if 'difficulty' not in data:
            volume_factor = result['volume'] ** 0.3 if result['volume'] > 0 else 0
            competition_factor = result['competition']
            result['difficulty'] = min(100, int(volume_factor * competition_factor * 20))
        else:
            result['difficulty'] = data['difficulty']
        
        # Calcul d'un score d'opportunité (plus élevé = meilleure opportunité)
        # Formula: (volume / 100) / ((difficulty + 10) / 10) - Valeurs élevées pour volume élevé et difficulté faible
        volume_norm = result['volume'] / 100
        difficulty_norm = (result['difficulty'] + 10) / 10
        
        result['opportunity_score'] = round(volume_norm / difficulty_norm, 2)
        
        return result
