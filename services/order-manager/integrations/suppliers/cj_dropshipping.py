import os
import json
import time
import logging
import hashlib
import hmac
import base64
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
import aiohttp
import asyncio

from .base import SupplierBase, OrderDetails, ShippingAddress, OrderItem
from ...models.order import SupplierOrderStatus

logger = logging.getLogger(__name__)

class CJDropshippingSupplier(SupplierBase):
    """
    Classe d'intégration pour le fournisseur CJ Dropshipping
    """
    
    def __init__(self, api_key: str = None, email: str = None):
        """
        Initialisation de l'intégration CJ Dropshipping
        
        Args:
            api_key (str): Clé API CJ Dropshipping
            email (str): Email associé au compte CJ Dropshipping
        """
        self.api_key = api_key or os.getenv("CJ_DROPSHIPPING_API_KEY")
        self.email = email or os.getenv("CJ_DROPSHIPPING_EMAIL")
        self.base_url = "https://developers.cjdropshipping.com/api2.0/"
        self.access_token = None
        self.token_expiry = 0
        
        if not self.api_key or not self.email:
            logger.warning("CJ Dropshipping credentials not set. Set CJ_DROPSHIPPING_API_KEY and CJ_DROPSHIPPING_EMAIL env variables")
    
    async def _ensure_token(self) -> None:
        """
        S'assure que le token d'accès est valide, en en obtenant un nouveau si nécessaire
        """
        current_time = time.time()
        
        # Si le token est expiré ou n'existe pas, en obtenir un nouveau
        if not self.access_token or current_time >= self.token_expiry:
            await self._get_access_token()
    
    async def _get_access_token(self) -> None:
        """
        Obtient un nouveau token d'accès à l'API CJ Dropshipping
        """
        endpoint = "authentication/getAccessToken"
        url = f"{self.base_url}{endpoint}"
        
        payload = {
            "email": self.email,
            "password": self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Failed to get CJ Dropshipping access token: {error_text}")
                        raise Exception(f"CJ Dropshipping authentication failed: {error_text}")
                    
                    data = await response.json()
                    
                    if data.get("result") != "OK":
                        error_msg = data.get("message", "Unknown error")
                        logger.error(f"CJ Dropshipping authentication error: {error_msg}")
                        raise Exception(f"CJ Dropshipping authentication error: {error_msg}")
                    
                    self.access_token = data.get("data", {}).get("accessToken")
                    # Token expires after 12 hours (43200 seconds), setting to 12h - 5min for safety
                    self.token_expiry = time.time() + 43200 - 300
                    
                    logger.info("Successfully obtained CJ Dropshipping access token")
        
        except aiohttp.ClientError as e:
            logger.error(f"Network error while obtaining CJ Dropshipping token: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Error obtaining CJ Dropshipping token: {str(e)}")
            raise
    
    async def _api_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                          data: Optional[Dict] = None) -> Dict:
        """
        Effectue une requête vers l'API CJ Dropshipping
        
        Args:
            method (str): Méthode HTTP (GET, POST, etc.)
            endpoint (str): Point d'API à appeler
            params (Dict, optional): Paramètres de requête
            data (Dict, optional): Données pour les requêtes POST/PUT
        
        Returns:
            Dict: Réponse de l'API
        """
        await self._ensure_token()
        
        url = f"{self.base_url}{endpoint}"
        headers = {"CJ-Access-Token": self.access_token}
        
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url, params=params, headers=headers) as response:
                        response_text = await response.text()
                        if response.status != 200:
                            logger.error(f"CJ Dropshipping API error: {response.status} - {response_text}")
                            raise Exception(f"CJ Dropshipping API error: {response.status} - {response_text}")
                        
                        return json.loads(response_text)
                
                elif method.upper() == "POST":
                    async with session.post(url, json=data, headers=headers) as response:
                        response_text = await response.text()
                        if response.status != 200:
                            logger.error(f"CJ Dropshipping API error: {response.status} - {response_text}")
                            raise Exception(f"CJ Dropshipping API error: {response.status} - {response_text}")
                        
                        return json.loads(response_text)
                
                else:
                    raise NotImplementedError(f"HTTP method {method} not implemented")
        
        except aiohttp.ClientError as e:
            logger.error(f"Network error in CJ Dropshipping API request: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in CJ Dropshipping API response: {str(e)}")
            raise Exception(f"Invalid API response: {str(e)}")
        except Exception as e:
            logger.error(f"Error in CJ Dropshipping API request: {str(e)}")
            raise
    
    async def search_products(self, query: str, page: int = 1, page_size: int = 20) -> Dict:
        """
        Recherche des produits sur CJ Dropshipping
        
        Args:
            query (str): Terme de recherche
            page (int): Numéro de page
            page_size (int): Nombre de résultats par page
        
        Returns:
            Dict: Résultats de la recherche
        """
        endpoint = "product/list"
        
        params = {
            "categoryId": "",
            "pageNum": page,
            "pageSize": page_size,
            "productName": query,
            "productSku": "",
            "categoryNameCn": ""
        }
        
        response = await self._api_request("POST", endpoint, data=params)
        
        if response.get("result") != "OK":
            error_msg = response.get("message", "Unknown error")
            logger.error(f"CJ Dropshipping product search error: {error_msg}")
            raise Exception(f"Product search error: {error_msg}")
        
        products = []
        for item in response.get("data", {}).get("list", []):
            product = {
                "id": item.get("pid"),
                "title": item.get("productName"),
                "description": item.get("productNameCn"),
                "sku": item.get("productSku"),
                "price": item.get("sellPrice"),
                "shipping_price": item.get("logisticInfoList", [{}])[0].get("logisticPrice") if item.get("logisticInfoList") else None,
                "variants": [],
                "image_url": item.get("productImage"),
                "category": item.get("categoryName")
            }
            
            # Ajouter les variantes si disponibles
            for variant in item.get("variants", []):
                product["variants"].append({
                    "id": variant.get("vid"),
                    "sku": variant.get("variantSku"),
                    "name": variant.get("variantName"),
                    "price": variant.get("variantSellPrice"),
                    "properties": variant.get("propertyList", [])
                })
            
            products.append(product)
        
        return {
            "products": products,
            "total": response.get("data", {}).get("total", 0),
            "page": page,
            "page_size": page_size
        }
    
    async def get_product_details(self, product_id: str) -> Dict:
        """
        Obtient les détails d'un produit spécifique
        
        Args:
            product_id (str): ID du produit CJ Dropshipping
        
        Returns:
            Dict: Détails du produit
        """
        endpoint = "product/query"
        
        params = {
            "pid": product_id
        }
        
        response = await self._api_request("POST", endpoint, data=params)
        
        if response.get("result") != "OK":
            error_msg = response.get("message", "Unknown error")
            logger.error(f"CJ Dropshipping product details error: {error_msg}")
            raise Exception(f"Product details error: {error_msg}")
        
        product_data = response.get("data", {})
        
        product = {
            "id": product_data.get("pid"),
            "title": product_data.get("productName"),
            "description": product_data.get("description"),
            "sku": product_data.get("productSku"),
            "price": product_data.get("sellPrice"),
            "shipping_options": [],
            "variants": [],
            "images": [img.get("imageUrl") for img in product_data.get("productImageList", [])],
            "category": product_data.get("categoryName"),
            "supplier": "CJ Dropshipping"
        }
        
        # Ajouter les options d'expédition
        for shipping in product_data.get("logisticInfoList", []):
            product["shipping_options"].append({
                "name": shipping.get("logisticName"),
                "price": shipping.get("logisticPrice"),
                "estimated_days": shipping.get("logisticTime")
            })
        
        # Ajouter les variantes
        for variant in product_data.get("variants", []):
            product["variants"].append({
                "id": variant.get("vid"),
                "sku": variant.get("variantSku"),
                "name": variant.get("variantName"),
                "price": variant.get("variantSellPrice"),
                "stock": variant.get("variantStock"),
                "properties": variant.get("propertyList", [])
            })
        
        return product
    
    async def create_order(self, order_details: OrderDetails) -> Dict:
        """
        Crée une commande chez CJ Dropshipping
        
        Args:
            order_details (OrderDetails): Détails de la commande
        
        Returns:
            Dict: Informations sur la commande créée
        """
        endpoint = "shopping/order/createOrder"
        
        # Construire l'adresse de livraison
        shipping_address = order_details.shipping_address
        address = {
            "name": f"{shipping_address.first_name} {shipping_address.last_name}",
            "phone": shipping_address.phone,
            "email": shipping_address.email,
            "country": shipping_address.country,
            "province": shipping_address.state,
            "city": shipping_address.city,
            "address": shipping_address.address1,
            "addressCode": shipping_address.zip
        }
        
        if shipping_address.address2:
            address["houseNumber"] = shipping_address.address2
        
        # Construire les articles
        products = []
        for item in order_details.items:
            product = {
                "vid": item.supplier_product_id,
                "quantity": item.quantity,
                "shippingName": "CJPacket" if not item.shipping_method else item.shipping_method
            }
            products.append(product)
        
        # Construire la charge utile de la commande
        payload = {
            "orderNumber": order_details.order_id,
            "shippingAddress": address,
            "products": products,
            "remark": order_details.note if order_details.note else ""
        }
        
        response = await self._api_request("POST", endpoint, data=payload)
        
        if response.get("result") != "OK":
            error_msg = response.get("message", "Unknown error")
            logger.error(f"CJ Dropshipping order creation error: {error_msg}")
            raise Exception(f"Order creation error: {error_msg}")
        
        order_data = response.get("data", {})
        
        return {
            "supplier_order_id": order_data.get("orderId"),
            "status": SupplierOrderStatus.PENDING,
            "tracking_number": None,
            "tracking_url": None,
            "order_date": datetime.now().isoformat(),
            "items": [{"sku": item.sku, "quantity": item.quantity, "supplier_product_id": item.supplier_product_id} for item in order_details.items],
            "total_amount": order_data.get("orderAmount"),
            "currency": "USD",
            "raw_response": order_data
        }
    
    async def get_order_status(self, supplier_order_id: str) -> Dict:
        """
        Récupère le statut d'une commande chez CJ Dropshipping
        
        Args:
            supplier_order_id (str): ID de la commande chez CJ Dropshipping
        
        Returns:
            Dict: Informations sur le statut de la commande
        """
        endpoint = "shopping/order/getOrderDetail"
        
        params = {
            "orderId": supplier_order_id
        }
        
        response = await self._api_request("POST", endpoint, data=params)
        
        if response.get("result") != "OK":
            error_msg = response.get("message", "Unknown error")
            logger.error(f"CJ Dropshipping order status error: {error_msg}")
            raise Exception(f"Order status error: {error_msg}")
        
        order_data = response.get("data", {})
        
        # Mapper les statuts CJ Dropshipping vers nos propres statuts
        status_mapping = {
            "CREATED": SupplierOrderStatus.PENDING,
            "PROCESSING": SupplierOrderStatus.PROCESSING,
            "SHIPPED": SupplierOrderStatus.SHIPPED,
            "DELIVERED": SupplierOrderStatus.DELIVERED,
            "CANCELLED": SupplierOrderStatus.CANCELLED
        }
        
        cj_status = order_data.get("orderStatus")
        status = status_mapping.get(cj_status, SupplierOrderStatus.UNKNOWN)
        
        result = {
            "supplier_order_id": supplier_order_id,
            "status": status,
            "tracking_number": order_data.get("trackingNumber"),
            "tracking_url": order_data.get("trackingUrl"),
            "last_update": datetime.now().isoformat(),
            "raw_response": order_data
        }
        
        # Ajouter les détails de livraison si disponibles
        shipping_info = order_data.get("shipping", {})
        if shipping_info:
            result["shipping"] = {
                "carrier": shipping_info.get("carrier"),
                "method": shipping_info.get("shippingMethod"),
                "estimated_delivery": shipping_info.get("estimatedDeliveryTime")
            }
        
        return result
    
    async def cancel_order(self, supplier_order_id: str, reason: str = "Cancelled by customer") -> Dict:
        """
        Annule une commande chez CJ Dropshipping
        
        Args:
            supplier_order_id (str): ID de la commande chez CJ Dropshipping
            reason (str): Raison de l'annulation
        
        Returns:
            Dict: Résultat de l'opération d'annulation
        """
        endpoint = "shopping/order/cancelOrder"
        
        payload = {
            "orderId": supplier_order_id,
            "remark": reason
        }
        
        response = await self._api_request("POST", endpoint, data=payload)
        
        if response.get("result") != "OK":
            error_msg = response.get("message", "Unknown error")
            logger.error(f"CJ Dropshipping order cancellation error: {error_msg}")
            raise Exception(f"Order cancellation error: {error_msg}")
        
        return {
            "supplier_order_id": supplier_order_id,
            "status": SupplierOrderStatus.CANCELLED,
            "cancellation_date": datetime.now().isoformat(),
            "reason": reason,
            "success": True
        }
    
    async def get_shipping_methods(self, product_id: str, country_code: str) -> List[Dict]:
        """
        Récupère les méthodes d'expédition disponibles pour un produit vers un pays
        
        Args:
            product_id (str): ID du produit CJ Dropshipping
            country_code (str): Code pays de destination
        
        Returns:
            List[Dict]: Liste des méthodes d'expédition disponibles
        """
        endpoint = "logistics/getLogisticsChannel"
        
        payload = {
            "pid": product_id,
            "countryCode": country_code
        }
        
        response = await self._api_request("POST", endpoint, data=payload)
        
        if response.get("result") != "OK":
            error_msg = response.get("message", "Unknown error")
            logger.error(f"CJ Dropshipping shipping methods error: {error_msg}")
            raise Exception(f"Shipping methods error: {error_msg}")
        
        shipping_methods = []
        for method in response.get("data", []):
            shipping_methods.append({
                "id": method.get("logisticName"),
                "name": method.get("logisticName"),
                "price": method.get("logisticPrice"),
                "estimated_days": method.get("logisticTime"),
                "tracking_available": method.get("isTracking", False)
            })
        
        return shipping_methods
    
    async def get_product_variants(self, product_id: str) -> List[Dict]:
        """
        Récupère les variantes disponibles pour un produit
        
        Args:
            product_id (str): ID du produit CJ Dropshipping
        
        Returns:
            List[Dict]: Liste des variantes disponibles
        """
        endpoint = "product/getVariants"
        
        payload = {
            "pid": product_id
        }
        
        response = await self._api_request("POST", endpoint, data=payload)
        
        if response.get("result") != "OK":
            error_msg = response.get("message", "Unknown error")
            logger.error(f"CJ Dropshipping product variants error: {error_msg}")
            raise Exception(f"Product variants error: {error_msg}")
        
        variants = []
        for variant in response.get("data", []):
            variants.append({
                "id": variant.get("vid"),
                "sku": variant.get("variantSku"),
                "name": variant.get("variantName"),
                "price": variant.get("variantSellPrice"),
                "stock": variant.get("variantStock"),
                "properties": variant.get("propertyList", [])
            })
        
        return variants