#!/usr/bin/env python3
"""
Client Shopify pour l'agent Order Manager
Fait partie du projet Dropshipping Crew AI
"""

import os
import json
import base64
import aiohttp
from typing import List, Dict, Any, Optional
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class ShopifyClient:
    """
    Client pour interagir avec l'API Shopify.
    Gère les opérations liées aux commandes et notifications.
    """
    
    def __init__(self, shop_url: str = None, api_key: str = None, api_password: str = None):
        """
        Initialise le client Shopify.
        
        Args:
            shop_url: URL de la boutique Shopify (ex: mystore.myshopify.com)
            api_key: Clé API Shopify
            api_password: Mot de passe API Shopify
        """
        self.shop_url = shop_url or os.getenv("SHOPIFY_SHOP_URL")
        self.api_key = api_key or os.getenv("SHOPIFY_API_KEY")
        self.api_password = api_password or os.getenv("SHOPIFY_API_PASSWORD")
        
        if not all([self.shop_url, self.api_key, self.api_password]):
            logger.warning("Configuration Shopify incomplète. Certaines fonctionnalités peuvent ne pas fonctionner.")
        
        # Création des credentials pour l'authentification
        self.auth = aiohttp.BasicAuth(self.api_key, self.api_password)
        
        # Construction de l'URL de base de l'API
        self.base_url = f"https://{self.shop_url}/admin/api/2022-01"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, json.JSONDecodeError))
    )
    async def get_new_orders(self, since_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Récupère les nouvelles commandes depuis Shopify.
        
        Args:
            since_id: Identifiant de la dernière commande traitée
            limit: Nombre maximum de commandes à récupérer
            
        Returns:
            Liste des nouvelles commandes
        """
        # Construction de l'URL
        url = f"{self.base_url}/orders.json?status=any&limit={limit}"
        
        if since_id:
            url += f"&since_id={since_id}"
        
        # Appel de l'API
        async with aiohttp.ClientSession() as session:
            async with session.get(url, auth=self.auth) as response:
                response.raise_for_status()
                data = await response.json()
                
                # Retourne la liste des commandes
                return data.get("orders", [])
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, json.JSONDecodeError))
    )
    async def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une commande spécifique depuis Shopify.
        
        Args:
            order_id: Identifiant de la commande Shopify
            
        Returns:
            Détails de la commande ou None si non trouvée
        """
        # Construction de l'URL
        url = f"{self.base_url}/orders/{order_id}.json"
        
        # Appel de l'API
        async with aiohttp.ClientSession() as session:
            async with session.get(url, auth=self.auth) as response:
                if response.status == 404:
                    return None
                
                response.raise_for_status()
                data = await response.json()
                
                # Retourne la commande
                return data.get("order")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, json.JSONDecodeError))
    )
    async def update_order_status(self, order_id: str, fulfillment_status: str) -> bool:
        """
        Met à jour le statut d'une commande Shopify.
        
        Args:
            order_id: Identifiant de la commande Shopify
            fulfillment_status: Nouveau statut d'exécution
            
        Returns:
            Succès de l'opération
        """
        # Construction de l'URL
        url = f"{self.base_url}/orders/{order_id}.json"
        
        # Préparation des données
        data = {
            "order": {
                "id": order_id,
                "fulfillment_status": fulfillment_status
            }
        }
        
        # Appel de l'API
        async with aiohttp.ClientSession() as session:
            async with session.put(url, auth=self.auth, json=data) as response:
                response.raise_for_status()
                return True
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, json.JSONDecodeError))
    )
    async def add_fulfillment(self, order_id: str, tracking_number: str, tracking_company: str) -> bool:
        """
        Ajoute un fulfillment à une commande Shopify avec des informations de suivi.
        
        Args:
            order_id: Identifiant de la commande Shopify
            tracking_number: Numéro de suivi
            tracking_company: Nom du transporteur
            
        Returns:
            Succès de l'opération
        """
        # Récupération des line items de la commande
        order = await self.get_order(order_id)
        if not order:
            logger.error(f"Commande {order_id} introuvable pour l'ajout du fulfillment")
            return False
        
        # Extraction des line item IDs
        line_item_ids = [item["id"] for item in order.get("line_items", [])]
        if not line_item_ids:
            logger.error(f"Aucun article trouvé dans la commande {order_id}")
            return False
        
        # Construction de l'URL
        url = f"{self.base_url}/orders/{order_id}/fulfillments.json"
        
        # Préparation des données
        data = {
            "fulfillment": {
                "line_items": [{"id": line_id} for line_id in line_item_ids],
                "tracking_number": tracking_number,
                "tracking_company": tracking_company,
                "notify_customer": True
            }
        }
        
        # Appel de l'API
        async with aiohttp.ClientSession() as session:
            async with session.post(url, auth=self.auth, json=data) as response:
                response.raise_for_status()
                return True
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, json.JSONDecodeError))
    )
    async def send_order_update(self, order_id: str, subject: str, message: str) -> bool:
        """
        Envoie une mise à jour concernant une commande au client.
        
        Args:
            order_id: Identifiant de la commande Shopify
            subject: Sujet du message
            message: Contenu du message
            
        Returns:
            Succès de l'opération
        """
        # Construction de l'URL
        url = f"{self.base_url}/orders/{order_id}/send_invoice.json"
        
        # Préparation des données
        data = {
            "email": {
                "subject": subject,
                "body": message,
                "from": os.getenv("NOTIFICATION_EMAIL", "orders@example.com"),
                "custom_message": message
            }
        }
        
        # Appel de l'API
        async with aiohttp.ClientSession() as session:
            async with session.post(url, auth=self.auth, json=data) as response:
                response.raise_for_status()
                return True
