#!/usr/bin/env python3
"""
Tests unitaires pour l'intégration avec CJ Dropshipping
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
from integrations.suppliers.cjdropshipping import CJDropshippingSupplier
from integrations.suppliers.base import OrderResult


class TestCJDropshippingSupplier(unittest.TestCase):
    """
    Tests pour la classe CJDropshippingSupplier.
    """
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        self.api_key = "test_api_key"
        self.api_url = "https://api.test.cjdropshipping.com"
        self.supplier = CJDropshippingSupplier(self.api_key, self.api_url)
        
        # Données de test
        self.test_order_data = {
            "id": "123456789",
            "shipping_address": {
                "name": "John Doe",
                "phone": "5551234567",
                "address1": "123 Main St",
                "address2": "Apt 4B",
                "city": "New York",
                "province": "NY",
                "zip": "10001",
                "country_code": "US",
                "country": "United States"
            },
            "customer": {
                "email": "customer@example.com"
            },
            "line_items": [
                {
                    "variant_id": "VAR456",
                    "quantity": 2,
                    "shipping_method": "CJPacket"
                }
            ],
            "shipping_method": "CJPacket",
            "note": "Test order"
        }
        
        self.test_supplier_order_id = "CJ12345678"
        self.test_product_id = "P12345"
    
    @patch('aiohttp.ClientSession.request')
    def test_place_order_success(self, mock_request):
        """Test de placement de commande réussi."""
        # Configuration de la réponse simulée
        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "code": 200,
            "message": "success",
            "data": {
                "orderId": self.test_supplier_order_id,
                "orderStatus": "pending"
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
            "code": 400,
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
            "code": 200,
            "message": "success",
            "data": {
                "orderId": self.test_supplier_order_id,
                "orderStatus": "shipped"
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
        self.assertEqual(result.status, "shipped")
        
        # Vérification que la requête a été effectuée correctement
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        self.assertEqual(call_args['method'], 'GET')
        self.assertIn(self.supplier.ENDPOINT_GET_ORDER, call_args['url'])
        self.assertIn("orderId="+self.test_supplier_order_id, str(call_args))

    @patch('aiohttp.ClientSession.request')
    def test_get_tracking_info_success(self, mock_request):
        """Test de récupération des informations de suivi réussi."""
        # Configuration de la réponse simulée
        tracking_number = "CJ12345678CN"
        tracking_url = "https://global.cainiao.com/detail.htm?mailNo=CJ12345678CN"
        logistics_name = "CJPacket"
        
        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "code": 200,
            "message": "success",
            "data": {
                "trackingNumber": tracking_number,
                "trackingUrl": tracking_url,
                "logisticsName": logistics_name
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
        self.assertEqual(result.shipping_company, logistics_name)
        self.assertEqual(result.status, "shipped")
        
        # Vérification que la requête a été effectuée correctement
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        self.assertEqual(call_args['method'], 'GET')
        self.assertIn(self.supplier.ENDPOINT_TRACKING_INFO, call_args['url'])
        self.assertIn("orderId="+self.test_supplier_order_id, str(call_args))
    
    @patch('aiohttp.ClientSession.request')
    def test_cancel_order_success(self, mock_request):
        """Test d'annulation de commande réussi."""
        # Configuration de la réponse simulée
        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "code": 200,
            "message": "success",
            "data": {
                "orderId": self.test_supplier_order_id,
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
        self.assertEqual(call_args['json']['remark'], "Changed my mind")
    
    @patch('aiohttp.ClientSession.request')
    def test_search_products_success(self, mock_request):
        """Test de recherche de produits réussi."""
        # Configuration de la réponse simulée
        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "code": 200,
            "message": "success",
            "data": {
                "total": 100,
                "list": [
                    {
                        "pid": "12345",
                        "productName": "Test Product",
                        "productImage": "https://cjdropshipping.com/image.jpg",
                        "productUrl": "https://cjdropshipping.com/product/12345",
                        "variants": [
                            {
                                "vid": "V12345",
                                "sellPrice": 19.99,
                                "variantStock": 100
                            }
                        ]
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
        self.assertEqual(call_args['method'], 'POST')
        self.assertIn(self.supplier.ENDPOINT_SEARCH_PRODUCTS, call_args['url'])
        self.assertEqual(call_args['json']['productName'], "test query")
    
    @patch('aiohttp.ClientSession.request')
    def test_get_product_details_success(self, mock_request):
        """Test de récupération des détails d'un produit réussi."""
        # Configuration de la réponse simulée
        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "code": 200,
            "message": "success",
            "data": {
                "pid": self.test_product_id,
                "productName": "Test Product Detail",
                "description": "This is a test product description",
                "productImage": "https://cjdropshipping.com/image1.jpg",
                "productImages": [
                    "https://cjdropshipping.com/image1.jpg",
                    "https://cjdropshipping.com/image2.jpg"
                ],
                "variants": [
                    {
                        "vid": "V12345",
                        "sellPrice": 19.99,
                        "variantStock": 100,
                        "variantAttributes": [
                            {"name": "color", "value": "red"},
                            {"name": "size", "value": "medium"}
                        ]
                    },
                    {
                        "vid": "V12346",
                        "sellPrice": 21.99,
                        "variantStock": 50,
                        "variantAttributes": [
                            {"name": "color", "value": "blue"},
                            {"name": "size", "value": "large"}
                        ]
                    }
                ],
                "shippings": [
                    {
                        "name": "CJPacket",
                        "price": 5.99,
                        "deliveryTime": "7-15 days"
                    }
                ]
            }
        }))
        mock_response.raise_for_status = AsyncMock()
        
        # Configuration du mock pour la requête HTTP
        mock_request.return_value.__aenter__.return_value = mock_response
        
        # Exécution du test
        result = asyncio.run(self.supplier.get_product_details(self.test_product_id))
        
        # Vérifications
        self.assertTrue(result["success"])
        self.assertEqual(result["id"], self.test_product_id)
        self.assertEqual(result["title"], "Test Product Detail")
        self.assertEqual(result["description"], "This is a test product description")
        self.assertEqual(len(result["images"]), 2)
        self.assertEqual(len(result["variations"]), 2)
        self.assertEqual(result["variations"][0]["properties"]["color"], "red")
        self.assertEqual(result["variations"][1]["properties"]["color"], "blue")
        self.assertEqual(result["shipping_info"]["methods"][0]["name"], "CJPacket")
        
        # Vérification que la requête a été effectuée correctement
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        self.assertEqual(call_args['method'], 'GET')
        self.assertIn(self.supplier.ENDPOINT_PRODUCT_DETAILS, call_args['url'])
        self.assertIn("pid="+self.test_product_id, str(call_args))

    @patch('aiohttp.ClientSession.request')
    def test_get_product_details_failure(self, mock_request):
        """Test de récupération des détails d'un produit échoué."""
        # Configuration de la réponse simulée
        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps({
            "code": 404,
            "message": "Product not found"
        }))
        mock_response.raise_for_status = AsyncMock()
        
        # Configuration du mock pour la requête HTTP
        mock_request.return_value.__aenter__.return_value = mock_response
        
        # Exécution du test
        result = asyncio.run(self.supplier.get_product_details(self.test_product_id))
        
        # Vérifications
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Product not found")
        
        # Vérification que la requête a été effectuée correctement
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        self.assertEqual(call_args['method'], 'GET')
        self.assertIn(self.supplier.ENDPOINT_PRODUCT_DETAILS, call_args['url'])

if __name__ == '__main__':
    unittest.main()
