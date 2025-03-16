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
