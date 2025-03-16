#!/usr/bin/env python3
"""
Module pour suivre et analyser les prix des concurrents.
"""

import asyncio
import re
import json
import time
import logging
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import aiohttp
import requests

from config import settings, get_logger

logger = get_logger("competitor_tracker")

class CompetitorTracker:
    """
    Classe pour suivre et analyser les prix des concurrents,
    et ajuster les prix de la boutique en conséquence.
    """
    
    def __init__(self):
        """Initialise le tracker de prix concurrents."""
        self.session = None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]
        self.current_user_agent_index = 0
        
        # Limites pour éviter d'être bloqué
        self.request_delay = 2.0  # secondes entre chaque requête
        self.max_requests_per_domain = 5  # nombre maximal de requêtes par domaine
        self.domain_counters = {}  # compteur de requêtes par domaine
        
        logger.info("Tracker de prix concurrents initialisé")
    
    def _create_session(self):
        """Crée une nouvelle session HTTP."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "User-Agent": self._get_next_user_agent(),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Cache-Control": "max-age=0"
                }
            )
    
    def _get_next_user_agent(self) -> str:
        """Retourne le prochain user agent dans la rotation."""
        user_agent = self.user_agents[self.current_user_agent_index]
        self.current_user_agent_index = (self.current_user_agent_index + 1) % len(self.user_agents)
        return user_agent
    
    async def _close_session(self):
        """Ferme la session HTTP."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _fetch_page(self, url: str) -> Optional[str]:
        """
        Récupère le contenu d'une page web.
        
        Args:
            url: URL de la page à récupérer
            
        Returns:
            Contenu HTML de la page ou None en cas d'erreur
        """
        # Vérifier les limites par domaine
        domain = urlparse(url).netloc
        if domain in self.domain_counters and self.domain_counters[domain] >= self.max_requests_per_domain:
            logger.warning(f"Limite de requêtes atteinte pour le domaine: {domain}")
            return None
        
        # Incrémenter le compteur de domaine
        self.domain_counters[domain] = self.domain_counters.get(domain, 0) + 1
        
        # Pause pour respecter le délai entre requêtes
        await asyncio.sleep(self.request_delay)
        
        try:
            self._create_session()
            async with self.session.get(url, ssl=False) as response:
                if response.status != 200:
                    logger.warning(f"Erreur lors de la récupération de {url}: {response.status}")
                    return None
                return await response.text()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de {url}: {str(e)}")
            return None
    
    async def _extract_price(self, html: str, product_name: str, price_selectors: List[str] = None) -> Optional[float]:
        """
        Extrait le prix d'un produit à partir du HTML d'une page.
        
        Args:
            html: Contenu HTML de la page
            product_name: Nom du produit recherché
            price_selectors: Liste de sélecteurs CSS pour trouver le prix
            
        Returns:
            Prix extrait ou None si non trouvé
        """
        if html is None:
            return None
        
        # Sélecteurs CSS communs pour les prix
        if price_selectors is None:
            price_selectors = [
                ".product__price", ".price", ".product-price", ".price-item",
                "[data-price]", "[itemprop='price']", ".current-price", ".price--sale"
            ]
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Chercher dans les éléments avec le nom du produit d'abord
            product_elements = soup.find_all(text=re.compile(re.escape(product_name), re.IGNORECASE))
            for element in product_elements:
                parent = element.parent
                for _ in range(5):  # Remonter jusqu'à 5 niveaux
                    if parent is None:
                        break
                    
                    # Chercher le prix près de cet élément
                    for selector in price_selectors:
                        price_element = parent.select_one(selector)
                        if price_element:
                            price_text = price_element.get_text().strip()
                            price = self._parse_price(price_text)
                            if price is not None:
                                return price
                    
                    parent = parent.parent
            
            # Si aucun prix n'est trouvé près du nom du produit, chercher globalement
            for selector in price_selectors:
                price_elements = soup.select(selector)
                for price_element in price_elements:
                    price_text = price_element.get_text().strip()
                    price = self._parse_price(price_text)
                    if price is not None:
                        return price
                    
            return None
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du prix: {str(e)}")
            return None
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """
        Convertit un texte de prix en valeur numérique.
        
        Args:
            price_text: Texte contenant un prix
            
        Returns:
            Valeur numérique du prix ou None si la conversion échoue
        """
        try:
            # Supprimer les caractères non numériques sauf le point et la virgule
            price_text = re.sub(r'[^\d.,]', '', price_text)
            
            # Normaliser la virgule en point
            price_text = price_text.replace(',', '.')
            
            # Gérer les formats avec plusieurs points (ex: 1.234.56)
            if price_text.count('.') > 1:
                parts = price_text.split('.')
                price_text = ''.join(parts[:-1]) + '.' + parts[-1]
                
            return float(price_text)
        except (ValueError, TypeError):
            return None
    
    async def track_price(self, product: Dict[str, Any], competitor_url: str) -> Dict[str, Any]:
        """
        Suit le prix d'un produit sur un site concurrent.
        
        Args:
            product: Informations sur le produit
            competitor_url: URL du site concurrent
            
        Returns:
            Informations sur le prix concurrent
        """
        product_name = product.get("name", "")
        variants = product.get("variants", [])
        
        logger.info(f"Suivi du prix pour '{product_name}' sur {competitor_url}")
        
        html = await self._fetch_page(competitor_url)
        if html is None:
            return {
                "product_id": product.get("id"),
                "competitor_url": competitor_url,
                "price_found": False,
                "timestamp": time.time()
            }
        
        price = await self._extract_price(html, product_name)
        
        return {
            "product_id": product.get("id"),
            "competitor_url": competitor_url,
            "price_found": price is not None,
            "price": price,
            "currency": "EUR",  # Par défaut, à améliorer pour détection automatique
            "timestamp": time.time()
        }
    
    async def track_prices(self, products: List[Dict[str, Any]], competitors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Suit les prix de plusieurs produits sur plusieurs sites concurrents.
        
        Args:
            products: Liste des produits à suivre
            competitors: Liste des concurrents (avec URLs)
            
        Returns:
            Liste des informations de prix
        """
        results = []
        
        try:
            # Réinitialiser les compteurs de domaine
            self.domain_counters = {}
            
            for product in products:
                for competitor in competitors:
                    # Construire l'URL du produit concurrent
                    competitor_url = competitor.get("product_url_template", "").format(
                        product_name=product.get("name", "").replace(" ", "-").lower()
                    )
                    
                    # Suivre le prix
                    price_info = await self.track_price(product, competitor_url)
                    price_info["competitor_name"] = competitor.get("name")
                    results.append(price_info)
            
            return results
        finally:
            # Fermer la session HTTP
            await self._close_session()
    
    async def adjust_prices(self, products: List[Dict[str, Any]], strategy: str = "competitive", 
                          threshold: float = 0.05) -> List[Dict[str, Any]]:
        """
        Ajuste les prix des produits en fonction de la stratégie choisie.
        
        Args:
            products: Liste des produits à ajuster
            strategy: Stratégie d'ajustement (competitive, premium, value)
            threshold: Seuil de différence de prix pour l'ajustement (en pourcentage)
            
        Returns:
            Liste des ajustements de prix effectués
        """
        adjustments = []
        
        for product in products:
            product_id = product.get("id")
            current_price = product.get("price")
            
            if current_price is None:
                logger.warning(f"Pas de prix actuel pour le produit {product_id}")
                continue
            
            # Récupérer les prix concurrents (simulé ici, à remplacer par une requête réelle)
            competitor_prices = product.get("competitor_prices", [])
            if not competitor_prices:
                logger.warning(f"Pas de prix concurrents pour le produit {product_id}")
                continue
            
            # Calculer le prix moyen des concurrents
            valid_prices = [p for p in competitor_prices if p is not None]
            if not valid_prices:
                logger.warning(f"Pas de prix concurrents valides pour le produit {product_id}")
                continue
                
            avg_competitor_price = sum(valid_prices) / len(valid_prices)
            min_competitor_price = min(valid_prices)
            max_competitor_price = max(valid_prices)
            
            # Calculer le nouveau prix selon la stratégie
            new_price = current_price
            
            if strategy == "competitive":
                # Prix légèrement inférieur à la moyenne des concurrents
                target_price = avg_competitor_price * 0.98
                if abs(current_price - target_price) / current_price > threshold:
                    new_price = target_price
            
            elif strategy == "premium":
                # Prix supérieur à la moyenne des concurrents
                target_price = max_competitor_price * 1.05
                if current_price < target_price and abs(current_price - target_price) / current_price > threshold:
                    new_price = target_price
            
            elif strategy == "value":
                # Prix inférieur au prix minimum concurrent
                target_price = min_competitor_price * 0.95
                if current_price > target_price and abs(current_price - target_price) / current_price > threshold:
                    new_price = target_price
            
            # Arrondir le prix pour qu'il soit "marketing friendly"
            new_price = self._format_price(new_price)
            
            # Enregistrer l'ajustement
            if new_price != current_price:
                adjustments.append({
                    "product_id": product_id,
                    "old_price": current_price,
                    "new_price": new_price,
                    "price_change": new_price - current_price,
                    "price_change_percent": (new_price - current_price) / current_price * 100,
                    "strategy": strategy,
                    "timestamp": time.time()
                })
        
        return adjustments
    
    def _format_price(self, price: float) -> float:
        """
        Formate un prix pour le rendre plus attractif marketing (e.g., 19.99 au lieu de 20.00).
        
        Args:
            price: Prix à formater
            
        Returns:
            Prix formaté
        """
        # Arrondir au centime près
        price = round(price * 100) / 100
        
        # Si le prix est supérieur à 10, utiliser .99 à la fin
        if price >= 10:
            whole_part = int(price)
            if price == whole_part:  # Si c'est un nombre entier
                price = whole_part - 0.01
            else:
                # Transformer 20.50 en 19.99 ou 20.20 en 19.99
                fractional = price - whole_part
                if fractional < 0.99:
                    price = whole_part - 0.01
        
        return price
