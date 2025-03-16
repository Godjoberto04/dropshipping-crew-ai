#!/usr/bin/env python3
"""
Module d'analyse SEO via l'API Ahrefs.
Permet d'obtenir des données sur le volume de recherche, la difficulté des mots-clés,
le potentiel de backlinks, la compétition, etc.
"""

import os
import json
import time
import requests
import pandas as pd
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
from urllib.parse import quote, urlencode
import hashlib
import datetime
import random

from config import settings, get_logger

logger = get_logger("ahrefs_analyzer")

class AhrefsAnalyzer:
    """Classe d'analyse SEO via l'API Ahrefs."""
    
    # Endpoints de l'API Ahrefs
    API_URL = "https://api.ahrefs.com/v1"
    KEYWORD_DIFFICULTY_ENDPOINT = "/kwdifficulty"
    KEYWORD_IDEAS_ENDPOINT = "/keywords-ideas"
    KEYWORD_METRICS_ENDPOINT = "/keywords-metrics"
    BACKLINKS_ENDPOINT = "/backlinks"
    DOMAIN_RATING_ENDPOINT = "/domain-rating"
    DOMAIN_METRICS_ENDPOINT = "/domain-metrics"
    
    # Bases de données par pays
    COUNTRY_CODES = {
        'us': 'us',
        'uk': 'gb',
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
        Initialise l'analyseur Ahrefs.
        
        Args:
            api_key: Clé API Ahrefs
            rate_limit: Limite de requêtes par seconde
            daily_limit: Limite quotidienne de requêtes
            cache_dir: Répertoire de cache
        """
        self.api_key = api_key or getattr(settings, 'AHREFS_API_KEY', None)
        self.rate_limit = rate_limit or getattr(settings, 'AHREFS_RATE_LIMIT', 3)
        self.daily_limit = daily_limit or getattr(settings, 'AHREFS_DAILY_LIMIT', 300)
        
        # Vérification de la clé API
        if not self.api_key:
            logger.warning("Aucune clé API Ahrefs fournie. L'analyseur fonctionnera en mode simulation.")
            self._simulation_mode = True
        else:
            self._simulation_mode = False
        
        # Répertoire de cache
        self.cache_dir = cache_dir or os.path.join(settings.CACHE_DIR, 'ahrefs')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # État de la limite
        self._last_request_time = 0
        self._daily_requests = 0
        self._daily_reset_date = datetime.datetime.now().date()
        
        logger.info(f"AhrefsAnalyzer initialisé (simulation_mode: {self._simulation_mode})")
    
    def _reset_daily_counter(self):
        """Réinitialise le compteur quotidien si nécessaire."""
        current_date = datetime.datetime.now().date()
        if current_date > self._daily_reset_date:
            self._daily_requests = 0
            self._daily_reset_date = current_date
            logger.debug("Compteur quotidien de requêtes Ahrefs réinitialisé")
    
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
            logger.warning(f"Limite quotidienne de requêtes Ahrefs atteinte ({self.daily_limit})")
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
        if 'token' in cache_params:
            del cache_params['token']
            
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
        Effectue une requête à l'API Ahrefs avec gestion du cache et des limites.
        
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
            raise Exception("Limite quotidienne de requêtes Ahrefs atteinte")
            
        self._respect_rate_limit()
        
        # Ajout de la clé API
        params['token'] = self.api_key
        
        # Construction de l'URL
        url = f"{self.API_URL}{endpoint}"
        
        try:
            # Exécution de la requête
            response = requests.get(url, params=params)
            self._daily_requests += 1
            
            # Vérification de la réponse
            if response.status_code != 200:
                logger.error(f"Erreur API Ahrefs: {response.status_code} - {response.text}")
                raise Exception(f"Erreur API Ahrefs: {response.status_code} - {response.text}")
            
            # Traitement de la réponse
            data = response.json()
            
            # Mise en cache
            if use_cache:
                self._save_to_cache(cache_key, data, cache_duration)
                
            return data
            
        except requests.RequestException as e:
            logger.error(f"Erreur de requête Ahrefs: {str(e)}")
            raise Exception(f"Erreur de requête Ahrefs: {str(e)}")
            
    def _generate_simulated_data(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère des données simulées pour le mode sans API.
        
        Args:
            endpoint: Endpoint de l'API
            params: Paramètres de la requête
            
        Returns:
            dict: Données simulées
        """
        # Récupération du mot-clé ou du domaine des paramètres
        keyword = params.get('keyword') or params.get('target') or "unknown"
        
        # Génération d'un hash déterministe basé sur le mot-clé pour des résultats cohérents
        keyword_hash = abs(hash(keyword))
        
        if self.KEYWORD_DIFFICULTY_ENDPOINT in endpoint:
            # Simulation de données de difficulté de mot-clé
            word_count = len(keyword.split())
            length_modifier = (len(keyword) % 10) / 10  # Modificateur basé sur la longueur (0-1)
            
            # KD (Keyword Difficulty) calculé de manière pseudo-aléatoire mais déterministe
            kd_base = 20 + (keyword_hash % 60)  # KD entre 20 et 80 par défaut
            
            # Ajustements basés sur la longueur du mot-clé
            kd = int(kd_base * (0.8 + (word_count * 0.1) + length_modifier))
            kd = max(1, min(100, kd))  # Limites de 1 à 100
            
            return {
                'keyword': keyword,
                'keyword_difficulty': kd,
                'cpc': round(0.5 + ((keyword_hash % 95) / 10), 2),  # CPC entre 0.5 et 10.0
                'country': params.get('country', 'us'),
                'simulated': True
            }
            
        elif self.KEYWORD_IDEAS_ENDPOINT in endpoint:
            # Simulation de suggestions de mots-clés
            suggestions = []
            num_suggestions = min(20, params.get('limit', 10))
            
            # Préfixes et suffixes pour générer des variantes
            prefixes = ["best", "top", "cheap", "premium", "professional", "new", "buy", "review", "compare"]
            suffixes = ["online", "shop", "2023", "guide", "for beginners", "vs", "alternative", "near me"]
            
            # Générer des variantes
            variations = []
            
            # Variations avec préfixes
            for prefix in prefixes[:min(5, num_suggestions // 2)]:
                variations.append(f"{prefix} {keyword}")
                
            # Variations avec suffixes
            for suffix in suffixes[:min(5, num_suggestions // 2)]:
                variations.append(f"{keyword} {suffix}")
                
            # Variations mixtes pour compléter
            mixed_count = max(0, num_suggestions - len(variations))
            for i in range(mixed_count):
                idx_prefix = (keyword_hash + i) % len(prefixes)
                idx_suffix = (keyword_hash + i * 7) % len(suffixes)
                variations.append(f"{prefixes[idx_prefix]} {keyword} {suffixes[idx_suffix]}")
            
            # Limiter au nombre demandé
            variations = variations[:num_suggestions]
            
            # Générer des données pour chaque suggestion
            for variation in variations:
                variation_hash = hash(variation)
                # Volume de recherche entre 100 et 10000
                volume = 100 + (abs(variation_hash) % 9900)
                # KD entre 10 et 90
                kd = 10 + (abs(variation_hash) % 80)
                # CPC entre 0.5 et 15.0
                cpc = 0.5 + ((abs(variation_hash) % 145) / 10)
                # Nombre de clicks entre 0 et volume (environ 2/3 du volume)
                clicks = int(volume * (0.3 + (abs(variation_hash) % 50) / 100))
                
                suggestions.append({
                    'keyword': variation,
                    'volume': volume,
                    'keyword_difficulty': kd,
                    'cpc': round(cpc, 2),
                    'clicks': clicks,
                    'return_rate': round(0.5 + (abs(variation_hash) % 50) / 100, 2),
                    'simulated': True
                })
            
            return {
                'ideas': suggestions,
                'count': len(suggestions),
                'simulated': True
            }
            
        elif self.KEYWORD_METRICS_ENDPOINT in endpoint:
            # Simulation de métriques de mot-clé
            word_count = len(keyword.split())
            
            # Volume de recherche basé sur le hash du mot-clé et la longueur
            volume_base = 500 + (keyword_hash % 9500)
            volume = int(volume_base * (1.1 - (word_count * 0.05)))
            volume = max(50, min(50000, volume))
            
            # KD (Keyword Difficulty)
            kd = 10 + (keyword_hash % 80)
            
            # Calcul du nombre de résultats (moyenne de 250,000 par point de KD)
            results = kd * (200000 + (keyword_hash % 100000))
            
            # Calcul du CPC (Cost Per Click) entre 0.5 et 10.0
            cpc = 0.5 + ((keyword_hash % 95) / 10)
            
            # Calcul du CTR (Click Through Rate) entre 40% et 95%
            ctr = 40 + (keyword_hash % 55)
            
            # Calcul des clics (basé sur le volume et le CTR)
            clicks = int(volume * (ctr / 100))
            
            return {
                'keyword': keyword,
                'volume': volume,
                'keyword_difficulty': kd,
                'serp_features': {
                    'featured_snippet': (keyword_hash % 3) == 0,
                    'knowledge_panel': (keyword_hash % 5) == 0,
                    'shopping_results': (keyword_hash % 4) == 0,
                    'image_pack': (keyword_hash % 3) == 1,
                    'news_results': (keyword_hash % 7) == 0
                },
                'cpc': round(cpc, 2),
                'clicks': clicks,
                'results': results,
                'ctr': ctr,
                'simulated': True,
                'country': params.get('country', 'us')
            }
            
        elif self.DOMAIN_RATING_ENDPOINT in endpoint or self.DOMAIN_METRICS_ENDPOINT in endpoint:
            # Simulation de métriques de domaine
            domain = params.get('target', 'example.com')
            domain_hash = abs(hash(domain))
            
            # Domain Rating (DR) entre 5 et 90
            dr = 5 + (domain_hash % 85)
            
            # Backlinks et domains référents
            backlinks_count = dr * (1000 + (domain_hash % 2000))
            referring_domains = int(backlinks_count / (10 + (domain_hash % 20)))
            
            # Trafic organique
            organic_traffic = dr * (50 + (domain_hash % 200))
            
            return {
                'domain': domain,
                'domain_rating': dr,
                'ahrefs_rank': max(1, 1000000 - (dr * 10000)),
                'backlinks': backlinks_count,
                'referring_domains': referring_domains,
                'referring_pages': backlinks_count,
                'referring_ips': int(referring_domains * 0.8),
                'referring_subnets': int(referring_domains * 0.6),
                'organic_keywords': int(organic_traffic * 0.8),
                'organic_traffic': organic_traffic,
                'traffic_value': int(organic_traffic * (0.5 + (domain_hash % 10) / 10)),
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
    
    def _process_keyword_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite et standardise les données de mot-clé.
        
        Args:
            data: Données brutes de l'API
            
        Returns:
            dict: Données traitées et standardisées
        """
        # Si c'est déjà au format standard ou en mode simulation, retourner tel quel
        if 'simulated' in data or ('keyword' in data and 'volume' in data and 'keyword_difficulty' in data):
            # S'assurer que tous les champs requis sont présents
            if 'competition' not in data and 'cpc' in data:
                # Estimateur simple: CPC élevé = concurrence élevée
                data['competition'] = min(1.0, data['cpc'] / 20.0)
                
            if 'competition_score' not in data and 'competition' in data:
                data['competition_score'] = int(data['competition'] * 100)
                
            if 'opportunity_score' not in data and 'volume' in data and 'keyword_difficulty' in data:
                # Calcul d'un score d'opportunité (plus élevé = meilleure opportunité)
                volume_norm = data['volume'] / 100
                difficulty_norm = (data['keyword_difficulty'] + 10) / 10
                data['opportunity_score'] = round(volume_norm / difficulty_norm, 2)
                
            return data
            
        # Sinon, convertir au format standard (dépend de la structure exacte renvoyée par l'API)
        # Ceci est une approximation à adapter selon la structure réelle de l'API Ahrefs
        result = {
            'keyword': data.get('keyword', 'unknown'),
            'volume': int(data.get('volume', 0)),
            'keyword_difficulty': int(data.get('difficulty', data.get('keyword_difficulty', 0))),
            'cpc': float(data.get('cpc', 0.0)),
            'results': int(data.get('results', 0)),
            'clicks': int(data.get('clicks', 0)),
        }
        
        # Calcul de la compétition si non fournie
        if 'competition' not in data:
            # Estimateur simple: difficulté élevée = concurrence élevée
            result['competition'] = min(1.0, result['keyword_difficulty'] / 100.0)
        else:
            result['competition'] = data['competition']
        
        # Conversion de la compétition de 0-1 à 0-100 pour harmoniser avec d'autres métriques
        result['competition_score'] = int(result['competition'] * 100)
        
        # Calcul d'un score d'opportunité (plus élevé = meilleure opportunité)
        volume_norm = result['volume'] / 100
        difficulty_norm = (result['keyword_difficulty'] + 10) / 10
        
        result['opportunity_score'] = round(volume_norm / difficulty_norm, 2)
        
        return result
