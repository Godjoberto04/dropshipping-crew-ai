#!/usr/bin/env python3
"""
Tests unitaires pour l'intégration avec AliExpress
Fait partie du projet Dropshipping Crew AI
"""

import os
import json
import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp
from aiohttp.client_reqrep import ClientResponse

# Import du module à tester
from integrations.suppliers.aliexpress import AliExpressSupplier
from integrations.suppliers.base import OrderResult


class TestAliExpressSupplier(unittest.TestCase):
    """
    Tests pour la classe AliExpressSupplier.
    """
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        self.api_key = "test_api_key"
        self.api_url = "https://api.test.aliexpress.com"
        self.supplier = AliExpressSupplier(self.api_key, self.api_url)
        
        # Données de test
        self.test_order_data = {
            "id": "123456789",
            "shipping_address": {
                "name": "John Doe",
                "phone_country": "1",
                "phone": "5551234567",
                "address1": "123 Main St",
                "address2": "Apt 4B",
                "city": "New York",
                "province": "NY",
                "zip": "10001",
                "country_code": "US"
            },
            "line_items": [
                {
                    "sku": "PROD123",
                    "quantity": 2,
                    "variant_id": "VAR456",
                    "shipping_method": "AliExpress Standard Shipping"
                }
            ]
        }
        
        self.test_supplier_order_id = "AE12345678"
    
    @patch('aiohttp.ClientSession.request')
    def test_place_order_success(self, mock_request):
        """Test de placement de commande réussi."""
        # Configuration de la réponse simulée
        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "success": True,
            "data": {
                "order_id": self.test_supplier_order_id,
                "status": "pending"
            }
        }))
        mock_response.raise_for_status = AsyncMock()
        
        # Configuration du mock pour la requête HTTP
        mock_request.return_value.__aenter__.return_value = mock_response
        
        # Exécution du test
        result = asyncio.run(self.supplier.place_order(self.test_order_data))
        
        # Vérifications
        self.assertTrue(result.success)
        self.assertEqual(result.supplier_order_id, self.test_supplier_order_id)
        self.assertEqual(result.status, "pending")
        
        # Vérification que la requête a été effectuée correctement
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        self.assertEqual(call_args['method'], 'POST')
        self.assertIn(self.supplier.ENDPOINT_PLACE_ORDER, call_args['url'])
    
    @patch('aiohttp.ClientSession.request')
    def test_place_order_failure(self, mock_request):
        """Test de placement de commande échoué."""
        # Configuration de la réponse simulée
        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "success": False,
            "message": "Invalid product ID"
        }))
        mock_response.raise_for_status = AsyncMock()
        
        # Configuration du mock pour la requête HTTP
        mock_request.return_value.__aenter__.return_value = mock_response
        
        # Exécution du test
        result = asyncio.run(self.supplier.place_order(self.test_order_data))
        
        # Vérifications
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Invalid product ID")
    
    @patch('aiohttp.ClientSession.request')
    def test_get_order_status_success(self, mock_request):
        """Test de récupération du statut de commande réussi."""
        # Configuration de la réponse simulée
        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "success": True,
            "data": {
                "order_id": self.test_supplier_order_id,
                "order_status": "WAIT_BUYER_RECEIVE_GOODS"
            }
        }))
        mock_response.raise_for_status = AsyncMock()
        
        # Configuration du mock pour la requête HTTP
        mock_request.return_value.__aenter__.return_value = mock_response
        
        # Exécution du test
        result = asyncio.run(self.supplier.get_order_status(self.test_supplier_order_id))
        
        # Vérifications
        self.assertTrue(result.success)
        self.assertEqual(result.supplier_order_id, self.test_supplier_order_id)
        self.assertEqual(result.status, "shipped")  # Mappé depuis WAIT_BUYER_RECEIVE_GOODS
        
        # Vérification que la requête a été effectuée correctement
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        self.assertEqual(call_args['method'], 'GET')
        self.assertIn(self.supplier.ENDPOINT_GET_ORDER, call_args['url'])
        self.assertIn(self.test_supplier_order_id, call_args['url'])
    
    @patch('aiohttp.ClientSession.request')
    def test_get_tracking_info_success(self, mock_request):
        """Test de récupération des informations de suivi réussi."""
        # Configuration de la réponse simulée
        tracking_number = "LX123456789CN"
        tracking_url = "https://global.cainiao.com/detail.htm?mailNo=LX123456789CN"
        logistics_company = "China Post"
        
        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "success": True,
            "data": {
                "tracking_number": tracking_number,
                "tracking_url": tracking_url,
                "logistics_company": logistics_company
            }
        }))
        mock_response.raise_for_status = AsyncMock()
        
        # Configuration du mock pour la requête HTTP
        mock_request.return_value.__aenter__.return_value = mock_response
        
        # Exécution du test
        result = asyncio.run(self.supplier.get_tracking_info(self.test_supplier_order_id))
        
        # Vérifications
        self.assertTrue(result.success)
        self.assertEqual(result.supplier_order_id, self.test_supplier_order_id)
        self.assertEqual(result.tracking_number, tracking_number)
        self.assertEqual(result.tracking_url, tracking_url)
        self.assertEqual(result.shipping_company, logistics_company)
        self.assertEqual(result.status, "shipped")
        
        # Vérification que la requête a été effectuée correctement
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        self.assertEqual(call_args['method'], 'GET')
        self.assertIn(self.supplier.ENDPOINT_TRACKING_INFO, call_args['url'])
        self.assertIn(self.test_supplier_order_id, call_args['url'])
    
    @patch('aiohttp.ClientSession.request')
    def test_cancel_order_success(self, mock_request):
        """Test d'annulation de commande réussi."""
        # Configuration de la réponse simulée
        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "success": True,
            "data": {
                "order_id": self.test_supplier_order_id,
                "status": "cancelled"
            }
        }))
        mock_response.raise_for_status = AsyncMock()
        
        # Configuration du mock pour la requête HTTP
        mock_request.return_value.__aenter__.return_value = mock_response
        
        # Exécution du test
        result = asyncio.run(self.supplier.cancel_order(self.test_supplier_order_id, "Changed my mind"))
        
        # Vérifications
        self.assertTrue(result.success)
        self.assertEqual(result.supplier_order_id, self.test_supplier_order_id)
        self.assertEqual(result.status, "cancelled")
        
        # Vérification que la requête a été effectuée correctement
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        self.assertEqual(call_args['method'], 'POST')
        self.assertIn(self.supplier.ENDPOINT_CANCEL_ORDER, call_args['url'])
        self.assertEqual(call_args['data']['cancel_reason'], "Changed my mind")
    
    @patch('aiohttp.ClientSession.request')
    def test_search_products_success(self, mock_request):
        """Test de recherche de produits réussi."""
        # Configuration de la réponse simulée
        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "success": True,
            "data": {
                "total_count": 100,
                "products": [
                    {
                        "product_id": "12345",
                        "product_title": "Test Product",
                        "product_description": "This is a test product",
                        "product_price": {"amount": 19.99, "currency_code": "USD"},
                        "product_detail_url": "https://aliexpress.com/item/12345.html",
                        "product_main_image_url": "https://ae01.alicdn.com/image.jpg",
                        "evaluation": {"star_rating": 4.8},
                        "trade": {"trade_count": 1000},
                        "shipping": {
                            "is_free_shipping": True,
                            "shipping_price": {"amount": 0, "currency_code": "USD"}
                        }
                    }
                ]
            }
        }))
        mock_response.raise_for_status = AsyncMock()
        
        # Configuration du mock pour la requête HTTP
        mock_request.return_value.__aenter__.return_value = mock_response
        
        # Exécution du test
        result = asyncio.run(self.supplier.search_products("test query", page=1, limit=20))
        
        # Vérifications
        self.assertTrue(result["success"])
        self.assertEqual(result["total"], 100)
        self.assertEqual(len(result["products"]), 1)
        self.assertEqual(result["products"][0]["id"], "12345")
        self.assertEqual(result["products"][0]["title"], "Test Product")
        self.assertEqual(result["products"][0]["price"], 19.99)
        
        # Vérification que la requête a été effectuée correctement
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        self.assertEqual(call_args['method'], 'GET')
        self.assertIn(self.supplier.ENDPOINT_SEARCH_PRODUCTS, call_args['url'])
        self.assertIn("keywords=test+query", call_args['url'])
    
    @patch('aiohttp.ClientSession.request')
    def test_get_product_details_success(self, mock_request):
        """Test de récupération des détails d'un produit réussi."""
        # Configuration de la réponse simulée
        product_id = "12345"
        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "success": True,
            "data": {
                "product_id": product_id,
                "product_title": "Detailed Test Product",
                "product_description": "This is a detailed test product",
                "price_module": {
                    "min_amount": {"amount": 19.99, "currency_code": "USD"},
                    "max_amount": {"amount": 29.99, "currency_code": "USD"}
                },
                "evaluation_module": {"star_rating": 4.8},
                "trade_module": {"trade_count": 1000},
                "image_module": {
                    "image_list": [
                        {"image_url": "https://ae01.alicdn.com/image1.jpg"},
                        {"image_url": "https://ae01.alicdn.com/image2.jpg"}
                    ]
                },
                "shipping_module": {
                    "is_free_shipping": True,
                    "shipping_list": [
                        {
                            "service_name": "AliExpress Standard Shipping",
                            "shipping_amount": {"amount": 0, "currency_code": "USD"},
                            "delivery_time": "15-30 days"
                        }
                    ]
                },
                "sku_module": {
                    "skus": [
                        {
                            "sku_id": "SKU123",
                            "sku_property_list": [
                                {
                                    "sku_property_name": "color",
                                    "property_value_definition_name": "Red"
                                }
                            ],
                            "sku_price": {"amount": 19.99, "currency_code": "USD"},
                            "available_quantity": 100
                        }
                    ]
                },
                "store_module": {
                    "store_name": "Test Store",
                    "seller_id": "SELLER123",
                    "store_rating": 4.9,
                    "followers_count": 5000
                }
            }
        }))
        mock_response.raise_for_status = AsyncMock()
        
        # Configuration du mock pour la requête HTTP
        mock_request.return_value.__aenter__.return_value = mock_response
        
        # Exécution du test
        result = asyncio.run(self.supplier.get_product_details(product_id))
        
        # Vérifications
        self.assertTrue(result["success"])
        self.assertEqual(result["id"], product_id)
        self.assertEqual(result["title"], "Detailed Test Product")
        self.assertEqual(result["price"]["min"], 19.99)
        self.assertEqual(result["price"]["max"], 29.99)
        self.assertEqual(len(result["images"]), 2)
        self.assertEqual(len(result["variations"]), 1)
        self.assertEqual(result["variations"][0]["id"], "SKU123")
        self.assertEqual(result["variations"][0]["properties"]["color"], "Red")
        
        # Vérification que la requête a été effectuée correctement
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        self.assertEqual(call_args['method'], 'GET')
        self.assertIn(self.supplier.ENDPOINT_PRODUCT_DETAILS, call_args['url'])
        self.assertIn(f"product_id={product_id}", call_args['url'])


if __name__ == '__main__':
    unittest.main()
