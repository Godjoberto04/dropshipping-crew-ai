#!/usr/bin/env python3
"""
Intégration avec l'API CJ Dropshipping
Fait partie du projet Dropshipping Crew AI
"""

import os
import json
import hmac
import time
import hashlib
import base64
import aiohttp
from urllib.parse import urlencode
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base import SupplierInterface, OrderResult


class CJDropshippingSupplier(SupplierInterface):
    """
    Implémentation de l'interface fournisseur pour CJ Dropshipping.
    
    Cette classe utilise l'API CJ Dropshipping pour gérer les commandes,
    le suivi, et la recherche de produits.
    """
    
    # Constantes API
    API_VERSION = "v1"
    API_TIMEOUT = 30
    
    # Endpoints
    ENDPOINT_PLACE_ORDER = "/api/order/placeOrder"
    ENDPOINT_GET_ORDER = "/api/order/getOrderDetail"
    ENDPOINT_CANCEL_ORDER = "/api/order/cancelOrder"
    ENDPOINT_TRACKING_INFO = "/api/order/getTrackingNumberInfo"
    ENDPOINT_SEARCH_PRODUCTS = "/api/product/list"
    ENDPOINT_PRODUCT_DETAILS = "/api/product/detail"
    
    # Valeurs par défaut
    DEFAULT_CURRENCY = "USD"
    DEFAULT_LANGUAGE = "en"
    
    def __init__(self, api_key: str, api_url: str = "https://developers.cjdropshipping.com"):
        """
        Initialise le fournisseur CJ Dropshipping.
        
        Args:
            api_key: Clé API CJ Dropshipping
            api_url: URL de base de l'API CJ Dropshipping
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip("/")
        self.email = os.getenv("CJDROPSHIPPING_EMAIL", "")
        
        # Configuration des en-têtes HTTP
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "CJ-Access-Token": self.api_key
        }
        
        # Si aucun email n'est fourni, utiliser une valeur par défaut
        if not self.email:
            logger.warning("Aucun email CJ Dropshipping fourni. Certaines fonctionnalités pourraient ne pas être disponibles.")
    
    async def _api_request(self, endpoint: str, method: str = "GET", params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Effectue une requête à l'API CJ Dropshipping.
        
        Args:
            endpoint: Point de terminaison API (ex: /api/order/placeOrder)
            method: Méthode HTTP (GET, POST, etc.)
            params: Paramètres de requête pour l'URL
            data: Données à envoyer dans le corps de la requête
            
        Returns:
            Réponse de l'API
            
        Raises:
            Exception: En cas d'erreur de requête ou de réponse
        """
        # Construction de l'URL complète
        url = f"{self.api_url}/{self.API_VERSION}{endpoint}"
        if method == "GET" and params:
            url += f"?{urlencode(params)}"
        
        try:
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(
                        url, 
                        headers=self.headers, 
                        timeout=self.API_TIMEOUT,
                        params=params if method == "GET" else None
                    ) as response:
                        response_text = await response.text()
                        response.raise_for_status()
                        return json.loads(response_text)
                else:  # POST, PUT, etc.
                    async with session.request(
                        method, 
                        url, 
                        headers=self.headers, 
                        params=params if method != "GET" else None,
                        json=data, 
                        timeout=self.API_TIMEOUT
                    ) as response:
                        response_text = await response.text()
                        response.raise_for_status()
                        return json.loads(response_text)
        
        except aiohttp.ClientResponseError as e:
            logger.error(f"Erreur API CJ Dropshipping ({e.status}): {e.message}")
            raise Exception(f"Erreur de réponse API ({e.status}): {e.message}")
        
        except aiohttp.ClientError as e:
            logger.error(f"Erreur de connexion à l'API CJ Dropshipping: {str(e)}")
            raise Exception(f"Erreur de connexion: {str(e)}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {response_text}")
            raise Exception(f"Réponse non valide: {str(e)}")
        
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'appel à l'API CJ Dropshipping: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, json.JSONDecodeError))
    )
    async def place_order(self, order_data: Dict[str, Any]) -> OrderResult:
        """
        Place une commande auprès de CJ Dropshipping.
        
        Args:
            order_data: Données de la commande
            
        Returns:
            Résultat de l'opération
        """
        try:
            # Préparation des données de commande pour CJ Dropshipping
            shipping_address = order_data.get("shipping_address", {})
            
            # Préparation des produits (SKUs et quantités)
            product_items = []
            for item in order_data.get("line_items", []):
                product_items.append({
                    "vid": item.get("variant_id", ""),  # Variant ID chez CJ Dropshipping
                    "quantity": item.get("quantity", 1),
                    "shippingName": item.get("shipping_method", "")
                })
            
            # Construction des données complètes pour la commande
            api_order_data = {
                "orderNumber": order_data.get("id", ""),
                "shippingZip": shipping_address.get("zip", ""),
                "shippingCountryCode": shipping_address.get("country_code", ""),
                "shippingCountry": shipping_address.get("country", ""),
                "shippingProvince": shipping_address.get("province", ""),
                "shippingCity": shipping_address.get("city", ""),
                "shippingAddress": f"{shipping_address.get('address1', '')} {shipping_address.get('address2', '')}",
                "shippingCustomerName": shipping_address.get("name", ""),
                "shippingPhone": shipping_address.get("phone", ""),
                "remark": order_data.get("note", ""),
                "fromCountryCode": "CN",  # Par défaut la Chine comme pays d'expédition
                "logisticName": order_data.get("shipping_method", "CJPacket"),
                "products": product_items
            }
            
            # Ajout de l'email client si disponible
            if "email" in order_data.get("customer", {}):
                api_order_data["buyerEmail"] = order_data["customer"]["email"]
            
            # Appel à l'API CJ Dropshipping
            response = await self._api_request(
                endpoint=self.ENDPOINT_PLACE_ORDER,
                method="POST",
                data=api_order_data
            )
            
            # Traitement de la réponse
            if response.get("code") == 200:
                order_info = response.get("data", {})
                return OrderResult(
                    success=True,
                    supplier_order_id=order_info.get("orderId"),
                    status="pending",
                    details=order_info
                )
            else:
                error_msg = response.get("message", "Erreur inconnue lors de la création de la commande")
                logger.error(f"Erreur CJ Dropshipping lors de la création de commande: {error_msg}")
                return OrderResult(
                    success=False,
                    error_message=error_msg
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de la création de commande CJ Dropshipping: {str(e)}")
            return OrderResult(
                success=False,
                error_message=f"Erreur lors de la création de commande: {str(e)}"
            )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, json.JSONDecodeError))
    )
    async def get_order_status(self, supplier_order_id: str) -> OrderResult:
        """
        Récupère le statut d'une commande CJ Dropshipping.
        
        Args:
            supplier_order_id: Identifiant de la commande chez CJ Dropshipping
            
        Returns:
            Résultat de l'opération avec le statut
        """
        try:
            # Préparation des paramètres pour l'API
            params = {
                "orderId": supplier_order_id
            }
            
            # Appel à l'API CJ Dropshipping
            response = await self._api_request(
                endpoint=self.ENDPOINT_GET_ORDER,
                params=params
            )
            
            # Traitement de la réponse
            if response.get("code") == 200:
                order_info = response.get("data", {})
                
                # Mapping des statuts CJ Dropshipping vers des statuts internes
                cj_status = order_info.get("orderStatus", "").lower()
                status_mapping = {
                    "pending": "processing",
                    "processing": "processing",
                    "shipped": "shipped",
                    "delivered": "delivered",
                    "cancelled": "cancelled",
                    "returned": "returned"
                }
                
                # Détermination du statut interne
                status = status_mapping.get(cj_status, "unknown")
                
                return OrderResult(
                    success=True,
                    supplier_order_id=supplier_order_id,
                    status=status,
                    details=order_info
                )
            else:
                error_msg = response.get("message", "Erreur inconnue lors de la vérification du statut")
                logger.error(f"Erreur CJ Dropshipping lors de la vérification du statut: {error_msg}")
                return OrderResult(
                    success=False,
                    error_message=error_msg
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du statut CJ Dropshipping: {str(e)}")
            return OrderResult(
                success=False,
                error_message=f"Erreur lors de la vérification du statut: {str(e)}"
            )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, json.JSONDecodeError))
    )
    async def get_tracking_info(self, supplier_order_id: str) -> OrderResult:
        """
        Récupère les informations de suivi d'une commande CJ Dropshipping.
        
        Args:
            supplier_order_id: Identifiant de la commande chez CJ Dropshipping
            
        Returns:
            Résultat de l'opération avec les informations de suivi
        """
        try:
            # Préparation des paramètres pour l'API
            params = {
                "orderId": supplier_order_id
            }
            
            # Appel à l'API CJ Dropshipping
            response = await self._api_request(
                endpoint=self.ENDPOINT_TRACKING_INFO,
                params=params
            )
            
            # Traitement de la réponse
            if response.get("code") == 200:
                tracking_info = response.get("data", {})
                
                # Si aucune information de suivi n'est disponible
                if not tracking_info:
                    return OrderResult(
                        success=True,
                        supplier_order_id=supplier_order_id,
                        status="processing",  # Statut par défaut si le suivi n'est pas disponible
                        error_message="Informations de suivi non disponibles"
                    )
                
                # Extraction des données de suivi
                tracking_number = tracking_info.get("trackingNumber", "")
                logistics_company = tracking_info.get("logisticsName", "")
                tracking_url = tracking_info.get("trackingUrl", "")
                
                return OrderResult(
                    success=True,
                    supplier_order_id=supplier_order_id,
                    tracking_number=tracking_number,
                    tracking_url=tracking_url,
                    shipping_company=logistics_company,
                    status="shipped" if tracking_number else "processing",
                    details=tracking_info
                )
            else:
                error_msg = response.get("message", "Erreur inconnue lors de la récupération du suivi")
                logger.error(f"Erreur CJ Dropshipping lors de la récupération du suivi: {error_msg}")
                return OrderResult(
                    success=False,
                    error_message=error_msg
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du suivi CJ Dropshipping: {str(e)}")
            return OrderResult(
                success=False,
                error_message=f"Erreur lors de la récupération du suivi: {str(e)}"
            )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, json.JSONDecodeError))
    )
    async def cancel_order(self, supplier_order_id: str, reason: str) -> OrderResult:
        """
        Annule une commande CJ Dropshipping.
        
        Args:
            supplier_order_id: Identifiant de la commande chez CJ Dropshipping
            reason: Raison de l'annulation
            
        Returns:
            Résultat de l'opération
        """
        try:
            # Préparation des données d'annulation
            cancel_data = {
                "orderId": supplier_order_id,
                "remark": reason
            }
            
            # Appel à l'API CJ Dropshipping
            response = await self._api_request(
                endpoint=self.ENDPOINT_CANCEL_ORDER,
                method="POST",
                data=cancel_data
            )
            
            # Traitement de la réponse
            if response.get("code") == 200:
                return OrderResult(
                    success=True,
                    supplier_order_id=supplier_order_id,
                    status="cancelled",
                    details=response.get("data", {})
                )
            else:
                error_msg = response.get("message", "Erreur inconnue lors de l'annulation de la commande")
                logger.error(f"Erreur CJ Dropshipping lors de l'annulation de commande: {error_msg}")
                return OrderResult(
                    success=False,
                    error_message=error_msg
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de l'annulation de commande CJ Dropshipping: {str(e)}")
            return OrderResult(
                success=False,
                error_message=f"Erreur lors de l'annulation de commande: {str(e)}"
            )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, json.JSONDecodeError))
    )
    async def search_products(self, query: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Recherche des produits sur CJ Dropshipping.
        
        Args:
            query: Termes de recherche
            page: Numéro de page
            limit: Nombre de résultats par page
            
        Returns:
            Résultats de la recherche
        """
        try:
            # Préparation des paramètres de recherche
            search_params = {
                "pageNum": page,
                "pageSize": limit,
                "categoryId": "",  # Optionnel: catégorie spécifique
                "productName": query,
                "productSku": "",  # Optionnel: SKU spécifique
                "entryType": "0"  # 0: Tous les produits
            }
            
            # Appel à l'API CJ Dropshipping
            response = await self._api_request(
                endpoint=self.ENDPOINT_SEARCH_PRODUCTS,
                method="POST",
                data=search_params
            )
            
            # Traitement de la réponse
            if response.get("code") == 200:
                search_results = response.get("data", {})
                products = search_results.get("list", [])
                
                # Transformation des données pour format standard
                formatted_products = []
                for product in products:
                    # Calcul du prix avec la première variante disponible si existante
                    price = 0
                    variants = product.get("variants", [])
                    if variants:
                        price = variants[0].get("sellPrice", 0)
                    
                    formatted_products.append({
                        "id": product.get("pid", ""),
                        "title": product.get("productName", ""),
                        "description": product.get("productName", ""),  # Champ description souvent manquant dans l'API, utilisé le nom comme fallback
                        "price": price,
                        "currency": self.DEFAULT_CURRENCY,
                        "url": product.get("productUrl", ""),
                        "image_url": product.get("productImage", ""),
                        "rating": 0,  # CJ ne fournit pas toujours de notation
                        "orders_count": 0,  # CJ ne fournit pas facilement ce nombre
                        "shipping_info": {
                            "free_shipping": False,  # Par défaut
                            "price": 0,  # A déterminer par requête supplémentaire
                            "currency": self.DEFAULT_CURRENCY
                        }
                    })
                
                return {
                    "success": True,
                    "total": search_results.get("total", 0),
                    "page": page,
                    "limit": limit,
                    "products": formatted_products
                }
            else:
                error_msg = response.get("message", "Erreur inconnue lors de la recherche")
                logger.error(f"Erreur CJ Dropshipping lors de la recherche: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "products": []
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la recherche CJ Dropshipping: {str(e)}")
            return {
                "success": False,
                "error": f"Erreur lors de la recherche: {str(e)}",
                "products": []
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, json.JSONDecodeError))
    )
    async def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """
        Récupère les détails d'un produit spécifique sur CJ Dropshipping.
        
        Args:
            product_id: Identifiant du produit chez CJ Dropshipping
            
        Returns:
            Détails du produit
        """
        try:
            # Préparation des paramètres pour l'API
            detail_params = {
                "pid": product_id
            }
            
            # Appel à l'API CJ Dropshipping
            response = await self._api_request(
                endpoint=self.ENDPOINT_PRODUCT_DETAILS,
                params=detail_params
            )
            
            # Traitement de la réponse
            if response.get("code") == 200:
                product_details = response.get("data", {})
                
                # Extraction des images
                images = []
                if product_details.get("productImage"):
                    images.append(product_details.get("productImage"))
                
                # Ajout d'images supplémentaires si disponibles
                if product_details.get("productImages"):
                    for img in product_details.get("productImages", []):
                        if img not in images:  # Éviter les doublons
                            images.append(img)
                
                # Traitement des variantes
                variants = []
                for variant in product_details.get("variants", []):
                    variant_data = {
                        "id": variant.get("vid", ""),
                        "price": variant.get("sellPrice", 0),
                        "currency": self.DEFAULT_CURRENCY,
                        "stock": variant.get("variantStock", 0),
                        "properties": {}
                    }
                    
                    # Ajout des propriétés (couleur, taille, etc.)
                    if variant.get("variantAttributes"):
                        for attr in variant.get("variantAttributes", []):
                            attr_name = attr.get("name", "").lower()
                            attr_value = attr.get("value", "")
                            variant_data["properties"][attr_name] = attr_value
                    
                    variants.append(variant_data)
                
                # Extraction des méthodes d'expédition
                shipping_methods = []
                for shipping in product_details.get("shippings", []):
                    shipping_methods.append({
                        "name": shipping.get("name", ""),
                        "price": shipping.get("price", 0),
                        "currency": self.DEFAULT_CURRENCY,
                        "delivery_time": shipping.get("deliveryTime", "")
                    })
                
                # Construction du résultat final
                result = {
                    "success": True,
                    "id": product_details.get("pid", ""),
                    "title": product_details.get("productName", ""),
                    "description": product_details.get("description", ""),
                    "price": {
                        "min": min([v.get("price", 0) for v in variants]) if variants else 0,
                        "max": max([v.get("price", 0) for v in variants]) if variants else 0,
                        "currency": self.DEFAULT_CURRENCY
                    },
                    "rating": 0,  # Non fourni par CJ
                    "orders_count": 0,  # Non fourni par CJ
                    "images": images,
                    "shipping_info": {
                        "free_shipping": False,  # CJ n'offre généralement pas d'expédition gratuite
                        "methods": shipping_methods
                    },
                    "variations": variants,
                    "seller": {
                        "name": "CJ Dropshipping",
                        "id": "",
                        "rating": 0,
                        "followers": 0
                    }
                }
                
                return result
            else:
                error_msg = response.get("message", "Erreur inconnue lors de la récupération des détails")
                logger.error(f"Erreur CJ Dropshipping lors de la récupération des détails: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des détails CJ Dropshipping: {str(e)}")
            return {
                "success": False,
                "error": f"Erreur lors de la récupération des détails: {str(e)}"
            }
