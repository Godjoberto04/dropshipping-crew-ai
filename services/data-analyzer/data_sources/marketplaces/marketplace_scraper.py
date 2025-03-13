#!/usr/bin/env python3
"""
Module de base pour les scrapers de marketplaces.
Fournit une classe abstraite qui définit l'interface commune pour tous les scrapers.
"""

import os
import json
import time
import random
import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Tuple
import hashlib
from datetime import datetime, timedelta

from config import settings, get_logger

logger = get_logger("marketplace_scraper")

class MarketplaceScraper(ABC):
    """
    Classe abstraite servant de base pour tous les scrapers de marketplaces.
    Définit l'interface commune et implémente des fonctionnalités partagées.
    """
    
    # Nom de la marketplace (à surcharger dans les sous-classes)
    MARKETPLACE_NAME = "generic"
    
    # Configuration par défaut des headers HTTP
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "fr,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    
    def __init__(
        self,
        proxies: Optional[Dict[str, str]] = None,
        cache_dir: Optional[str] = None,
        cache_expiry: int = 86400,  # 24 heures par défaut
        rate_limit: float = 1.0,    # 1 requête par seconde par défaut
        max_retries: int = 3,
        retry_delay: int = 5,
        timeout: int = 30,
        simulate: bool = False
    ):
        """
        Initialise le scraper de marketplace.
        
        Args:
            proxies: Dictionnaire de proxies (format requests)
            cache_dir: Répertoire de cache
            cache_expiry: Durée de validité du cache en secondes
            rate_limit: Nombre de requêtes par seconde
            max_retries: Nombre maximal de tentatives en cas d'échec
            retry_delay: Délai entre les tentatives en secondes
            timeout: Timeout des requêtes en secondes
            simulate: Mode de simulation (données générées, pas de requêtes réelles)
        """
        self.proxies = proxies
        
        # Si la configuration des proxies est activée et qu'aucun proxy n'est fourni
        if not self.proxies and getattr(settings, 'PROXY_ENABLED', False):
            self.proxies = {'https': getattr(settings, 'PROXY_URL', None)}
        
        self.cache_expiry = cache_expiry
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.simulate = simulate
        
        # Configuration du cache
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            self.cache_dir = os.path.join(
                settings.CACHE_DIR, 'marketplaces', self.MARKETPLACE_NAME
            )
        
        # Création du répertoire de cache s'il n'existe pas
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Suivi des temps de requête pour le rate limiting
        self._last_request_time = 0
        
        logger.info(f"Scraper {self.MARKETPLACE_NAME} initialisé (simulate: {self.simulate})")
    
    def _respect_rate_limit(self):
        """Respecte le rate limit configuré."""
        if self.simulate:
            return
            
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        
        # Si moins de temps s'est écoulé que l'intervalle requis
        if elapsed < (1.0 / self.rate_limit):
            sleep_time = (1.0 / self.rate_limit) - elapsed
            time.sleep(sleep_time)
            
        self._last_request_time = time.time()
    
    def _get_cache_key(self, action: str, params: Dict[str, Any]) -> str:
        """
        Génère une clé de cache pour une action et des paramètres donnés.
        
        Args:
            action: Type d'action (search, product_details, etc.)
            params: Paramètres de l'action
            
        Returns:
            str: Clé de cache (hash MD5)
        """
        # Préparation des paramètres pour le hachage
        hashable_params = json.dumps(params, sort_keys=True)
        key_base = f"{self.MARKETPLACE_NAME}_{action}_{hashable_params}"
        
        # Génération du hash
        cache_key = hashlib.md5(key_base.encode()).hexdigest()
        
        return cache_key
    
    def _get_cache_file(self, cache_key: str) -> str:
        """
        Génère le chemin du fichier de cache pour une clé donnée.
        
        Args:
            cache_key: Clé de cache
            
        Returns:
            str: Chemin du fichier de cache
        """
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]):
        """
        Sauvegarde des données dans le cache.
        
        Args:
            cache_key: Clé de cache
            data: Données à mettre en cache
        """
        try:
            cache_file = self._get_cache_file(cache_key)
            
            # Ajout des métadonnées
            cache_data = {
                'data': data,
                'timestamp': time.time(),
                'expiry': time.time() + self.cache_expiry
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False)
                
            logger.debug(f"Données sauvegardées dans le cache: {cache_key}")
            
        except Exception as e:
            logger.warning(f"Erreur lors de la sauvegarde en cache: {str(e)}")
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Charge des données depuis le cache si elles sont valides.
        
        Args:
            cache_key: Clé de cache
            
        Returns:
            dict ou None: Données si elles sont valides, None sinon
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
    
    def _make_request(
        self,
        url: str,
        method: str = 'GET',
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        allow_redirects: bool = True
    ) -> requests.Response:
        """
        Effectue une requête HTTP avec gestion des erreurs et des tentatives.
        
        Args:
            url: URL de la requête
            method: Méthode HTTP (GET, POST, etc.)
            headers: En-têtes HTTP
            params: Paramètres de requête
            data: Données de formulaire
            json_data: Données JSON
            allow_redirects: Autoriser les redirections
            
        Returns:
            Response: Objet réponse requests
            
        Raises:
            Exception: En cas d'échec après toutes les tentatives
        """
        if self.simulate:
            raise ValueError("Les requêtes ne sont pas disponibles en mode simulation")
        
        # Respect du rate limit
        self._respect_rate_limit()
        
        # Fusion des en-têtes par défaut avec les en-têtes fournis
        merged_headers = self.DEFAULT_HEADERS.copy()
        if headers:
            merged_headers.update(headers)
        
        # Réalisation de plusieurs tentatives en cas d'échec
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=merged_headers,
                    params=params,
                    data=data,
                    json=json_data,
                    proxies=self.proxies,
                    timeout=self.timeout,
                    allow_redirects=allow_redirects
                )
                
                # Vérification du statut de la réponse
                response.raise_for_status()
                
                return response
                
            except (requests.RequestException, Exception) as e:
                logger.warning(f"Tentative {attempt}/{self.max_retries} échouée: {str(e)}")
                
                if attempt < self.max_retries:
                    # Attente avant la prochaine tentative (avec jitter aléatoire)
                    jitter = random.uniform(0, 1)
                    delay = self.retry_delay * (1 + jitter)
                    time.sleep(delay)
                else:
                    logger.error(f"Échec après {self.max_retries} tentatives: {str(e)}")
                    raise
    
    def _generate_simulated_data(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère des données simulées pour le mode de simulation.
        À surcharger dans les sous-classes pour des simulations spécifiques.
        
        Args:
            action: Type d'action (search, product_details, etc.)
            params: Paramètres de l'action
            
        Returns:
            dict: Données simulées
        """
        return {
            'simulated': True,
            'action': action,
            'params': params,
            'marketplace': self.MARKETPLACE_NAME,
            'message': f"Données simulées génériques pour {action} sur {self.MARKETPLACE_NAME}"
        }
    
    def execute_action(
        self,
        action: str,
        params: Dict[str, Any],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Exécute une action avec gestion du cache et des erreurs.
        
        Args:
            action: Type d'action (search, product_details, etc.)
            params: Paramètres de l'action
            use_cache: Utiliser le cache si disponible
            
        Returns:
            dict: Résultat de l'action
            
        Raises:
            ValueError: Si l'action n'est pas valide
            Exception: En cas d'échec de l'action
        """
        logger.info(f"Exécution de l'action '{action}' sur {self.MARKETPLACE_NAME}")
        
        # Vérification du cache
        if use_cache:
            cache_key = self._get_cache_key(action, params)
            cached_data = self._load_from_cache(cache_key)
            
            if cached_data:
                return cached_data
        
        # Mode simulation
        if self.simulate:
            data = self._generate_simulated_data(action, params)
            
            # Mise en cache des données simulées
            if use_cache:
                cache_key = self._get_cache_key(action, params)
                self._save_to_cache(cache_key, data)
                
            return data
        
        try:
            # Exécution de l'action réelle (à implémenter dans les sous-classes)
            if action == 'search':
                data = self.search(**params)
            elif action == 'product_details':
                data = self.get_product_details(**params)
            elif action == 'related_products':
                data = self.get_related_products(**params)
            elif action == 'seller_info':
                data = self.get_seller_info(**params)
            else:
                # Action personnalisée à implémenter dans les sous-classes
                method_name = f"execute_{action}"
                if hasattr(self, method_name) and callable(getattr(self, method_name)):
                    data = getattr(self, method_name)(**params)
                else:
                    raise ValueError(f"Action inconnue: {action}")
            
            # Mise en cache
            if use_cache:
                cache_key = self._get_cache_key(action, params)
                self._save_to_cache(cache_key, data)
                
            return data
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de l'action '{action}': {str(e)}")
            raise
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Recherche des produits dans la marketplace.
        
        Args:
            query: Terme de recherche
            **kwargs: Paramètres supplémentaires spécifiques à la marketplace
            
        Returns:
            dict: Résultats de recherche
        """
        pass
    
    @abstractmethod
    def get_product_details(self, product_id: str, **kwargs) -> Dict[str, Any]:
        """
        Récupère les détails d'un produit.
        
        Args:
            product_id: Identifiant du produit
            **kwargs: Paramètres supplémentaires
            
        Returns:
            dict: Détails du produit
        """
        pass
    
    def get_related_products(self, product_id: str, **kwargs) -> Dict[str, Any]:
        """
        Récupère les produits associés à un produit.
        
        Args:
            product_id: Identifiant du produit
            **kwargs: Paramètres supplémentaires
            
        Returns:
            dict: Produits associés
        """
        # Implémentation par défaut (à surcharger si besoin)
        return {
            'product_id': product_id,
            'related_products': [],
            'message': 'Fonctionnalité non implémentée pour cette marketplace'
        }
    
    def get_seller_info(self, seller_id: str, **kwargs) -> Dict[str, Any]:
        """
        Récupère les informations sur un vendeur.
        
        Args:
            seller_id: Identifiant du vendeur
            **kwargs: Paramètres supplémentaires
            
        Returns:
            dict: Informations sur le vendeur
        """
        # Implémentation par défaut (à surcharger si besoin)
        return {
            'seller_id': seller_id,
            'info': {},
            'message': 'Fonctionnalité non implémentée pour cette marketplace'
        }
    
    def extract_price(self, price_str: str) -> float:
        """
        Extrait un prix à partir d'une chaîne.
        
        Args:
            price_str: Chaîne contenant un prix
            
        Returns:
            float: Prix extrait
        """
        try:
            # Suppression des caractères non numériques (sauf le point décimal)
            cleaned = ''.join(c for c in price_str if c.isdigit() or c == '.' or c == ',')
            
            # Remplacement de la virgule par un point
            cleaned = cleaned.replace(',', '.')
            
            # Conversion en float
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0
    
    def standardize_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardise les données d'un produit dans un format commun.
        
        Args:
            product_data: Données brutes du produit
            
        Returns:
            dict: Données standardisées
        """
        # Structure de base standardisée
        standard_product = {
            'marketplace': self.MARKETPLACE_NAME,
            'product_id': product_data.get('id', ''),
            'title': product_data.get('title', ''),
            'price': float(product_data.get('price', 0.0)),
            'currency': product_data.get('currency', 'EUR'),
            'url': product_data.get('url', ''),
            'image_url': product_data.get('image_url', ''),
            'rating': float(product_data.get('rating', 0.0)),
            'review_count': int(product_data.get('review_count', 0)),
            'available': bool(product_data.get('available', True)),
            'shipping_price': float(product_data.get('shipping_price', 0.0)),
            'shipping_time': product_data.get('shipping_time', ''),
            'seller': product_data.get('seller', {}),
            'description': product_data.get('description', ''),
            'features': product_data.get('features', []),
            'variants': product_data.get('variants', []),
            'source_data': product_data  # Données brutes pour référence
        }
        
        return standard_product
