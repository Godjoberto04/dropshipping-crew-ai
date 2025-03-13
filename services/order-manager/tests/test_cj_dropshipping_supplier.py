import unittest
import os
import json
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio
from datetime import datetime

from integrations.suppliers.cj_dropshipping import CJDropshippingSupplier
from models.order import SupplierOrderStatus
from integrations.suppliers.base import OrderDetails, ShippingAddress, OrderItem

class TestCJDropshippingSupplier(unittest.TestCase):
    """Tests pour l'intégration avec CJ Dropshipping"""
    
    def setUp(self):
        """Configuration des tests"""
        # Configurer les variables d'environnement simulées
        os.environ["CJ_DROPSHIPPING_API_KEY"] = "fake_api_key"
        os.environ["CJ_DROPSHIPPING_EMAIL"] = "test@example.com"
        
        # Créer une instance du fournisseur
        self.supplier = CJDropshippingSupplier()
        
        # Données de test
        self.mock_product_id = "123456"
        self.mock_variant_id = "var_789"
        self.mock_order_id = "ord_12345"
        self.mock_supplier_order_id = "cj_78901"
        
        # Mock des réponses API
        self.mock_token_response = {
            "result": "OK",
            "message": None,
            "data": {
                "accessToken": "fake_access_token",
                "expirationTime": "2025-03-14 18:48:32"
            }
        }
        
        self.mock_search_response = {
            "result": "OK",
            "message": None,
            "data": {
                "list": [
                    {
                        "pid": "123456",
                        "productName": "Test Product",
                        "productNameCn": "Test Product Description",
                        "productSku": "SKU123",
                        "sellPrice": 9.99,
                        "logisticInfoList": [{"logisticPrice": 2.99}],
                        "productImage": "https://example.com/image.jpg",
                        "categoryName": "Test Category",
                        "variants": [
                            {
                                "vid": "var_789",
                                "variantSku": "SKU123-1",
                                "variantName": "Test Variant",
                                "variantSellPrice": 10.99,
                                "propertyList": []
                            }
                        ]
                    }
                ],
                "total": 1
            }
        }
        
        self.mock_product_details = {
            "result": "OK",
            "message": None,
            "data": {
                "pid": "123456",
                "productName": "Test Product",
                "description": "Detailed description",
                "productSku": "SKU123",
                "sellPrice": 9.99,
                "logisticInfoList": [
                    {
                        "logisticName": "CJPacket",
                        "logisticPrice": 2.99,
                        "logisticTime": "10-15"
                    }
                ],
                "productImageList": [{"imageUrl": "https://example.com/image.jpg"}],
                "categoryName": "Test Category",
                "variants": [
                    {
                        "vid": "var_789",
                        "variantSku": "SKU123-1",
                        "variantName": "Test Variant",
                        "variantSellPrice": 10.99,
                        "variantStock": 100,
                        "propertyList": []
                    }
                ]
            }
        }
        
        self.mock_create_order_response = {
            "result": "OK",
            "message": None,
            "data": {
                "orderId": "cj_78901",
                "orderAmount": 12.98
            }
        }
        
        self.mock_order_status_response = {
            "result": "OK",
            "message": None,
            "data": {
                "orderId": "cj_78901",
                "orderStatus": "PROCESSING",
                "trackingNumber": "TRACK123456",
                "trackingUrl": "https://tracking.example.com/TRACK123456",
                "shipping": {
                    "carrier": "CJ Dropshipping",
                    "shippingMethod": "CJPacket",
                    "estimatedDeliveryTime": "2025-03-25"
                }
            }
        }
        
        self.mock_cancel_order_response = {
            "result": "OK",
            "message": None,
            "data": {}
        }
        
        self.mock_shipping_methods_response = {
            "result": "OK",
            "message": None,
            "data": [
                {
                    "logisticName": "CJPacket",
                    "logisticPrice": 2.99,
                    "logisticTime": "10-15",
                    "isTracking": True
                },
                {
                    "logisticName": "ePacket",
                    "logisticPrice": 3.99,
                    "logisticTime": "7-12",
                    "isTracking": True
                }
            ]
        }
        
        self.mock_variants_response = {
            "result": "OK",
            "message": None,
            "data": [
                {
                    "vid": "var_789",
                    "variantSku": "SKU123-1",
                    "variantName": "Test Variant",
                    "variantSellPrice": 10.99,
                    "variantStock": 100,
                    "propertyList": []
                },
                {
                    "vid": "var_790",
                    "variantSku": "SKU123-2",
                    "variantName": "Test Variant 2",
                    "variantSellPrice": 11.99,
                    "variantStock": 50,
                    "propertyList": []
                }
            ]
        }
    
    @patch('aiohttp.ClientSession.post')
    async def test_get_access_token(self, mock_post):
        """Test de la récupération du token d'accès"""
        # Configurer le mock
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=self.mock_token_response)
        mock_response.__aenter__.return_value = mock_response
        mock_post.return_value = mock_response
        
        # Appeler la méthode
        await self.supplier._get_access_token()
        
        # Vérifier que le token a été correctement enregistré
        self.assertEqual(self.supplier.access_token, "fake_access_token")
        self.assertTrue(self.supplier.token_expiry > 0)
        
        # Vérifier que la requête a été faite correctement
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("authentication/getAccessToken", args[0])
        self.assertEqual(kwargs["json"]["email"], "test@example.com")
        self.assertEqual(kwargs["json"]["password"], "fake_api_key")
    
    @patch('aiohttp.ClientSession.post')
    async def test_search_products(self, mock_post):
        """Test de la recherche de produits"""
        # Configurer le mock pour la récupération du token et la recherche
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=[self.mock_token_response, self.mock_search_response])
        mock_response.text = AsyncMock(return_value=json.dumps(self.mock_search_response))
        mock_response.__aenter__.return_value = mock_response
        mock_post.return_value = mock_response
        
        # Appeler la méthode
        results = await self.supplier.search_products("test product")
        
        # Vérifier les résultats
        self.assertEqual(len(results["products"]), 1)
        self.assertEqual(results["products"][0]["id"], self.mock_product_id)
        self.assertEqual(results["products"][0]["title"], "Test Product")
        self.assertEqual(results["products"][0]["price"], 9.99)
        self.assertEqual(results["products"][0]["image_url"], "https://example.com/image.jpg")
        self.assertEqual(len(results["products"][0]["variants"]), 1)
        self.assertEqual(results["products"][0]["variants"][0]["id"], self.mock_variant_id)
        
        # Vérifier que les appels API ont été effectués correctement
        self.assertEqual(mock_post.call_count, 2)
        
    @patch('aiohttp.ClientSession.post')
    async def test_get_product_details(self, mock_post):
        """Test de la récupération des détails d'un produit"""
        # Configurer le mock
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=[self.mock_token_response, self.mock_product_details])
        mock_response.text = AsyncMock(return_value=json.dumps(self.mock_product_details))
        mock_response.__aenter__.return_value = mock_response
        mock_post.return_value = mock_response
        
        # Appeler la méthode
        product = await self.supplier.get_product_details(self.mock_product_id)
        
        # Vérifier les résultats
        self.assertEqual(product["id"], self.mock_product_id)
        self.assertEqual(product["title"], "Test Product")
        self.assertEqual(product["description"], "Detailed description")
        self.assertEqual(product["price"], 9.99)
        self.assertEqual(len(product["shipping_options"]), 1)
        self.assertEqual(product["shipping_options"][0]["name"], "CJPacket")
        self.assertEqual(len(product["variants"]), 1)
        self.assertEqual(product["variants"][0]["id"], self.mock_variant_id)
        self.assertEqual(product["variants"][0]["stock"], 100)
        self.assertEqual(len(product["images"]), 1)
        self.assertEqual(product["images"][0], "https://example.com/image.jpg")
        
        # Vérifier que les appels API ont été effectués correctement
        self.assertEqual(mock_post.call_count, 2)
