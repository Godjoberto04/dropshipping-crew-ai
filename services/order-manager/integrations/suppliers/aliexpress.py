#!/usr/bin/env python3
"""
Intégration avec l'API AliExpress pour le dropshipping
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


class AliExpressSupplier(SupplierInterface):
    """
    Implémentation de l'interface fournisseur pour AliExpress.
    
    Cette classe utilise l'API AliExpress Dropshipping pour gérer les commandes,
    le suivi, et la recherche de produits.
    """
    
    # Constantes API
    API_VERSION = "2.0"
    API_TIMEOUT = 30
    
    # Endpoints
    ENDPOINT_PLACE_ORDER = "/api/ds/order/place"
    ENDPOINT_GET_ORDER = "/api/ds/order/get"
    ENDPOINT_CANCEL_ORDER = "/api/ds/order/cancel"
    ENDPOINT_TRACKING_INFO = "/api/ds/logistics/tracking"
    ENDPOINT_SEARCH_PRODUCTS = "/api/ds/product/search"
    ENDPOINT_PRODUCT_DETAILS = "/api/ds/product/details"
    
    # Valeurs par défaut
    DEFAULT_CURRENCY = "USD"
    DEFAULT_LANGUAGE = "en"
    
    def __init__(self, api_key: str, api_url: str = "https://api.aliexpress.com"):
        """
        Initialise le fournisseur AliExpress.
        
        Args:
            api_key: Clé API AliExpress
            api_url: URL de base de l'API AliExpress
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip("/")
        self.app_secret = os.getenv("ALIEXPRESS_APP_SECRET", "")
        self.seller_id = os.getenv("ALIEXPRESS_SELLER_ID", "")
        
        # Configuration des en-têtes HTTP
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Si aucun secret d'application n'est fourni, utiliser la clé API comme secret
        if not self.app_secret:
            logger.warning("Aucun secret d'application AliExpress fourni. Utilisation de la clé API comme secret.")
            self.app_secret = self.api_key
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        Génère une signature pour les requêtes API.
        
        La signature est créée en concaténant tous les paramètres triés par nom
        puis en appliquant HMAC-SHA256 avec le secret d'application.
        
        Args:
            params: Paramètres de la requête
            
        Returns:
            Signature encodée en base64
        """
        # Triez les paramètres par nom
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        
        # Concaténez les paramètres
        param_string = ""
        for key, value in sorted_params:
            param_string += f"{key}{value}"
        
        # Créez la signature HMAC-SHA256
        signature = hmac.new(
            self.app_secret.encode(),
            param_string.encode(),
            hashlib.sha256
        ).digest()
        
        # Encodez la signature en base64
        return base64.b64encode(signature).decode()
    
    async def _api_request(self, endpoint: str, method: str = "GET", params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Effectue une requête à l'API AliExpress.
        
        Args:
            endpoint: Point de terminaison API (ex: /api/order/place)
            method: Méthode HTTP (GET, POST, etc.)
            params: Paramètres de requête pour l'URL
            data: Données à envoyer dans le corps de la requête
            
        Returns:
            Réponse de l'API
            
        Raises:
            Exception: En cas d'erreur de requête ou de réponse
        """
        # Préparation des paramètres de base
        request_params = {
            "app_key": self.api_key,
            "timestamp": str(int(time.time())),
            "format": "json",
            "v": self.API_VERSION,
            "sign_method": "hmac-sha256"
        }
        
        # Ajout des paramètres supplémentaires
        if params:
            request_params.update(params)
        
        # Génération de la signature
        request_params["sign"] = self._generate_signature(request_params)
        
        # Construction de l'URL complète
        url = f"{self.api_url}{endpoint}"
        if method == "GET":
            url += f"?{urlencode(request_params)}"
        
        try:
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, headers=self.headers, timeout=self.API_TIMEOUT) as response:
                        response_text = await response.text()
                        response.raise_for_status()
                        return json.loads(response_text)
                else:  # POST, PUT, etc.
                    async with session.request(
                        method, 
                        url, 
                        headers=self.headers, 
                        params=request_params if method != "GET" else None,
                        json=data, 
                        timeout=self.API_TIMEOUT
                    ) as response:
                        response_text = await response.text()
                        response.raise_for_status()
                        return json.loads(response_text)
        
        except aiohttp.ClientResponseError as e:
            logger.error(f"Erreur API AliExpress ({e.status}): {e.message}")
            raise Exception(f"Erreur de réponse API ({e.status}): {e.message}")
        
        except aiohttp.ClientError as e:
            logger.error(f"Erreur de connexion à l'API AliExpress: {str(e)}")
            raise Exception(f"Erreur de connexion: {str(e)}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {response_text}")
            raise Exception(f"Réponse non valide: {str(e)}")
        
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'appel à l'API AliExpress: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, json.JSONDecodeError))
    )
    async def place_order(self, order_data: Dict[str, Any]) -> OrderResult:
        """
        Place une commande auprès d'AliExpress.
        
        Args:
            order_data: Données de la commande
            
        Returns:
            Résultat de l'opération
        """
        try:
            # Préparation des données de commande pour AliExpress
            api_order_data = {
                "logistics_address": {
                    "contact_person": order_data.get("shipping_address", {}).get("name", ""),
                    "phone_country": order_data.get("shipping_address", {}).get("phone_country", "1"),
                    "mobile_no": order_data.get("shipping_address", {}).get("phone", ""),
                    "address": order_data.get("shipping_address", {}).get("address1", ""),
                    "address2": order_data.get("shipping_address", {}).get("address2", ""),
                    "city": order_data.get("shipping_address", {}).get("city", ""),
                    "province": order_data.get("shipping_address", {}).get("province", ""),
                    "zip": order_data.get("shipping_address", {}).get("zip", ""),
                    "country": order_data.get("shipping_address", {}).get("country_code", "")
                },
                "product_items": [
                    {
                        "product_id": item.get("sku", ""),
                        "product_count": item.get("quantity", 1),
                        "sku_attr": item.get("variant_id", ""),
                        "logistics_service_name": item.get("shipping_method", "AliExpress Standard Shipping")
                    }
                    for item in order_data.get("line_items", [])
                ],
                "client_order_id": order_data.get("id", ""),
                "create_source": "API"
            }
            
            # Appel à l'API AliExpress
            response = await self._api_request(
                endpoint=self.ENDPOINT_PLACE_ORDER,
                method="POST",
                data=api_order_data
            )
            
            # Traitement de la réponse
            if response.get("success", False):
                order_info = response.get("data", {})
                return OrderResult(
                    success=True,
                    supplier_order_id=order_info.get("order_id"),
                    status="pending",
                    details=order_info
                )
            else:
                error_msg = response.get("message", "Erreur inconnue lors de la création de la commande")
                logger.error(f"Erreur AliExpress lors de la création de commande: {error_msg}")
                return OrderResult(
                    success=False,
                    error_message=error_msg
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de la création de commande AliExpress: {str(e)}")
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
        Récupère le statut d'une commande AliExpress.
        
        Args:
            supplier_order_id: Identifiant de la commande chez AliExpress
            
        Returns:
            Résultat de l'opération avec le statut
        """
        try:
            # Appel à l'API AliExpress
            response = await self._api_request(
                endpoint=self.ENDPOINT_GET_ORDER,
                params={"order_id": supplier_order_id}
            )
            
            # Traitement de la réponse
            if response.get("success", False):
                order_info = response.get("data", {})
                
                # Mapping des statuts AliExpress vers des statuts internes
                status_mapping = {
                    "PLACE_ORDER_SUCCESS": "processing",
                    "IN_CANCEL": "cancelling",
                    "WAIT_SELLER_SEND_GOODS": "processing",
                    "SELLER_SEND_GOODS": "shipped",
                    "WAIT_BUYER_RECEIVE_GOODS": "shipped",
                    "FUND_PROCESSING": "processing",
                    "FINISH": "delivered",
                    "IN_ISSUE": "issue",
                    "IN_FROZEN": "frozen",
                    "WAIT_SELLER_EXAMINE_MONEY": "processing",
                    "RISK_CONTROL": "risk_control"
                }
                
                aliexpress_status = order_info.get("order_status", "")
                status = status_mapping.get(aliexpress_status, "unknown")
                
                return OrderResult(
                    success=True,
                    supplier_order_id=supplier_order_id,
                    status=status,
                    details=order_info
                )
            else:
                error_msg = response.get("message", "Erreur inconnue lors de la vérification du statut")
                logger.error(f"Erreur AliExpress lors de la vérification du statut: {error_msg}")
                return OrderResult(
                    success=False,
                    error_message=error_msg
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du statut AliExpress: {str(e)}")
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
        Récupère les informations de suivi d'une commande AliExpress.
        
        Args:
            supplier_order_id: Identifiant de la commande chez AliExpress
            
        Returns:
            Résultat de l'opération avec les informations de suivi
        """
        try:
            # Appel à l'API AliExpress
            response = await self._api_request(
                endpoint=self.ENDPOINT_TRACKING_INFO,
                params={"order_id": supplier_order_id}
            )
            
            # Traitement de la réponse
            if response.get("success", False):
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
                tracking_number = tracking_info.get("tracking_number", "")
                logistics_company = tracking_info.get("logistics_company", "")
                tracking_url = tracking_info.get("tracking_url", "")
                
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
                logger.error(f"Erreur AliExpress lors de la récupération du suivi: {error_msg}")
                return OrderResult(
                    success=False,
                    error_message=error_msg
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du suivi AliExpress: {str(e)}")
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
        Annule une commande AliExpress.
        
        Args:
            supplier_order_id: Identifiant de la commande chez AliExpress
            reason: Raison de l'annulation
            
        Returns:
            Résultat de l'opération
        """
        try:
            # Préparation des données d'annulation
            cancel_data = {
                "order_id": supplier_order_id,
                "cancel_reason": reason
            }
            
            # Appel à l'API AliExpress
            response = await self._api_request(
                endpoint=self.ENDPOINT_CANCEL_ORDER,
                method="POST",
                data=cancel_data
            )
            
            # Traitement de la réponse
            if response.get("success", False):
                return OrderResult(
                    success=True,
                    supplier_order_id=supplier_order_id,
                    status="cancelled",
                    details=response.get("data", {})
                )
            else:
                error_msg = response.get("message", "Erreur inconnue lors de l'annulation de la commande")
                logger.error(f"Erreur AliExpress lors de l'annulation de commande: {error_msg}")
                return OrderResult(
                    success=False,
                    error_message=error_msg
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de l'annulation de commande AliExpress: {str(e)}")
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
        Recherche des produits sur AliExpress.
        
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
                "keywords": query,
                "page": str(page),
                "page_size": str(limit),
                "sort": "orders_desc",  # Tri par nombre de commandes
                "language": self.DEFAULT_LANGUAGE,
                "currency": self.DEFAULT_CURRENCY
            }
            
            # Appel à l'API AliExpress
            response = await self._api_request(
                endpoint=self.ENDPOINT_SEARCH_PRODUCTS,
                params=search_params
            )
            
            # Traitement de la réponse
            if response.get("success", False):
                search_results = response.get("data", {})
                products = search_results.get("products", [])
                
                # Transformation des données pour format standard
                formatted_products = []
                for product in products:
                    formatted_products.append({
                        "id": product.get("product_id", ""),
                        "title": product.get("product_title", ""),
                        "description": product.get("product_description", ""),
                        "price": product.get("product_price", {}).get("amount", 0),
                        "currency": product.get("product_price", {}).get("currency_code", self.DEFAULT_CURRENCY),
                        "url": product.get("product_detail_url", ""),
                        "image_url": product.get("product_main_image_url", ""),
                        "rating": product.get("evaluation", {}).get("star_rating", 0),
                        "orders_count": product.get("trade", {}).get("trade_count", 0),
                        "shipping_info": {
                            "free_shipping": product.get("shipping", {}).get("is_free_shipping", False),
                            "price": product.get("shipping", {}).get("shipping_price", {}).get("amount", 0),
                            "currency": product.get("shipping", {}).get("shipping_price", {}).get("currency_code", self.DEFAULT_CURRENCY)
                        }
                    })
                
                return {
                    "success": True,
                    "total": search_results.get("total_count", 0),
                    "page": page,
                    "limit": limit,
                    "products": formatted_products
                }
            else:
                error_msg = response.get("message", "Erreur inconnue lors de la recherche")
                logger.error(f"Erreur AliExpress lors de la recherche: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "products": []
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la recherche AliExpress: {str(e)}")
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
        Récupère les détails d'un produit spécifique sur AliExpress.
        
        Args:
            product_id: Identifiant du produit chez AliExpress
            
        Returns:
            Détails du produit
        """
        try:
            # Préparation des paramètres de recherche
            detail_params = {
                "product_id": product_id,
                "language": self.DEFAULT_LANGUAGE,
                "currency": self.DEFAULT_CURRENCY
            }
            
            # Appel à l'API AliExpress
            response = await self._api_request(
                endpoint=self.ENDPOINT_PRODUCT_DETAILS,
                params=detail_params
            )
            
            # Traitement de la réponse
            if response.get("success", False):
                product_details = response.get("data", {})
                
                # Transformation des variations en format standard
                variations = []
                sku_modules = product_details.get("sku_module", {}).get("skus", [])
                for sku in sku_modules:
                    variation = {
                        "id": sku.get("sku_id", ""),
                        "properties": {}
                    }
                    
                    # Ajout des propriétés (couleur, taille, etc.)
                    for prop in sku.get("sku_property_list", []):
                        prop_name = prop.get("sku_property_name", "").lower()
                        prop_value = prop.get("property_value_definition_name", "")
                        variation["properties"][prop_name] = prop_value
                    
                    # Ajout du prix et du stock
                    variation["price"] = sku.get("sku_price", {}).get("amount", 0)
                    variation["currency"] = sku.get("sku_price", {}).get("currency_code", self.DEFAULT_CURRENCY)
                    variation["stock"] = sku.get("available_quantity", 0)
                    
                    variations.append(variation)
                
                # Construction du résultat
                result = {
                    "success": True,
                    "id": product_details.get("product_id", ""),
                    "title": product_details.get("product_title", ""),
                    "description": product_details.get("product_description", ""),
                    "price": {
                        "min": product_details.get("price_module", {}).get("min_amount", {}).get("amount", 0),
                        "max": product_details.get("price_module", {}).get("max_amount", {}).get("amount", 0),
                        "currency": product_details.get("price_module", {}).get("min_amount", {}).get("currency_code", self.DEFAULT_CURRENCY)
                    },
                    "rating": product_details.get("evaluation_module", {}).get("star_rating", 0),
                    "orders_count": product_details.get("trade_module", {}).get("trade_count", 0),
                    "images": [
                        img.get("image_url", "")
                        for img in product_details.get("image_module", {}).get("image_list", [])
                    ],
                    "shipping_info": {
                        "free_shipping": product_details.get("shipping_module", {}).get("is_free_shipping", False),
                        "methods": [
                            {
                                "name": shipping.get("service_name", ""),
                                "price": shipping.get("shipping_amount", {}).get("amount", 0),
                                "currency": shipping.get("shipping_amount", {}).get("currency_code", self.DEFAULT_CURRENCY),
                                "delivery_time": shipping.get("delivery_time", "")
                            }
                            for shipping in product_details.get("shipping_module", {}).get("shipping_list", [])
                        ]
                    },
                    "variations": variations,
                    "seller": {
                        "name": product_details.get("store_module", {}).get("store_name", ""),
                        "id": product_details.get("store_module", {}).get("seller_id", ""),
                        "rating": product_details.get("store_module", {}).get("store_rating", 0),
                        "followers": product_details.get("store_module", {}).get("followers_count", 0)
                    }
                }
                
                return result
            else:
                error_msg = response.get("message", "Erreur inconnue lors de la récupération des détails")
                logger.error(f"Erreur AliExpress lors de la récupération des détails: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des détails AliExpress: {str(e)}")
            return {
                "success": False,
                "error": f"Erreur lors de la récupération des détails: {str(e)}"
            }
