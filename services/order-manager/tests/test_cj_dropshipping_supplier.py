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
    
    @patch('aiohttp.ClientSession.post')
    async def test_create_order(self, mock_post):
        """Test de la création d'une commande"""
        # Configurer le mock
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=[self.mock_token_response, self.mock_create_order_response])
        mock_response.text = AsyncMock(return_value=json.dumps(self.mock_create_order_response))
        mock_response.__aenter__.return_value = mock_response
        mock_post.return_value = mock_response
        
        # Créer les données de la commande
        shipping_address = ShippingAddress(
            first_name="John",
            last_name="Doe",
            address1="123 Main St",
            address2="Apt 4B",
            city="New York",
            state="NY",
            zip="10001",
            country="US",
            phone="+1234567890",
            email="john.doe@example.com"
        )
        
        items = [
            OrderItem(
                sku="SKU123-1",
                supplier_product_id=self.mock_variant_id,
                quantity=2,
                price=10.99,
                title="Test Variant",
                shipping_method="CJPacket"
            )
        ]
        
        order_details = OrderDetails(
            order_id=self.mock_order_id,
            shipping_address=shipping_address,
            items=items,
            note="Test order"
        )
        
        # Appeler la méthode
        result = await self.supplier.create_order(order_details)
        
        # Vérifier les résultats
        self.assertEqual(result["supplier_order_id"], self.mock_supplier_order_id)
        self.assertEqual(result["status"], SupplierOrderStatus.PENDING)
        self.assertEqual(result["total_amount"], 12.98)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["sku"], "SKU123-1")
        self.assertEqual(result["items"][0]["quantity"], 2)
        
        # Vérifier que les appels API ont été effectués correctement
        self.assertEqual(mock_post.call_count, 2)
        
        # Vérifier les données envoyées à l'API
        args, kwargs = mock_post.call_args
        self.assertIn("shopping/order/createOrder", args[0])
        self.assertEqual(kwargs["json"]["orderNumber"], self.mock_order_id)
        self.assertEqual(kwargs["json"]["shippingAddress"]["name"], "John Doe")
        self.assertEqual(kwargs["json"]["shippingAddress"]["address"], "123 Main St")
        self.assertEqual(kwargs["json"]["shippingAddress"]["houseNumber"], "Apt 4B")
        self.assertEqual(kwargs["json"]["products"][0]["vid"], self.mock_variant_id)
        self.assertEqual(kwargs["json"]["products"][0]["quantity"], 2)
        self.assertEqual(kwargs["json"]["products"][0]["shippingName"], "CJPacket")
    
    @patch('aiohttp.ClientSession.post')
    async def test_get_order_status(self, mock_post):
        """Test de la récupération du statut d'une commande"""
        # Configurer le mock
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=[self.mock_token_response, self.mock_order_status_response])
        mock_response.text = AsyncMock(return_value=json.dumps(self.mock_order_status_response))
        mock_response.__aenter__.return_value = mock_response
        mock_post.return_value = mock_response
        
        # Appeler la méthode
        result = await self.supplier.get_order_status(self.mock_supplier_order_id)
        
        # Vérifier les résultats
        self.assertEqual(result["supplier_order_id"], self.mock_supplier_order_id)
        self.assertEqual(result["status"], SupplierOrderStatus.PROCESSING)
        self.assertEqual(result["tracking_number"], "TRACK123456")
        self.assertEqual(result["tracking_url"], "https://tracking.example.com/TRACK123456")
        self.assertTrue("shipping" in result)
        self.assertEqual(result["shipping"]["carrier"], "CJ Dropshipping")
        self.assertEqual(result["shipping"]["method"], "CJPacket")
        
        # Vérifier que les appels API ont été effectués correctement
        self.assertEqual(mock_post.call_count, 2)
        
        # Vérifier les données envoyées à l'API
        args, kwargs = mock_post.call_args
        self.assertIn("shopping/order/getOrderDetail", args[0])
        self.assertEqual(kwargs["json"]["orderId"], self.mock_supplier_order_id)
    
    @patch('aiohttp.ClientSession.post')
    async def test_cancel_order(self, mock_post):
        """Test de l'annulation d'une commande"""
        # Configurer le mock
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=[self.mock_token_response, self.mock_cancel_order_response])
        mock_response.text = AsyncMock(return_value=json.dumps(self.mock_cancel_order_response))
        mock_response.__aenter__.return_value = mock_response
        mock_post.return_value = mock_response
        
        # Appeler la méthode
        result = await self.supplier.cancel_order(self.mock_supplier_order_id, "Customer cancelled")
        
        # Vérifier les résultats
        self.assertEqual(result["supplier_order_id"], self.mock_supplier_order_id)
        self.assertEqual(result["status"], SupplierOrderStatus.CANCELLED)
        self.assertEqual(result["reason"], "Customer cancelled")
        self.assertTrue(result["success"])
        
        # Vérifier que les appels API ont été effectués correctement
        self.assertEqual(mock_post.call_count, 2)
        
        # Vérifier les données envoyées à l'API
        args, kwargs = mock_post.call_args
        self.assertIn("shopping/order/cancelOrder", args[0])
        self.assertEqual(kwargs["json"]["orderId"], self.mock_supplier_order_id)
        self.assertEqual(kwargs["json"]["remark"], "Customer cancelled")
    
    @patch('aiohttp.ClientSession.post')
    async def test_get_shipping_methods(self, mock_post):
        """Test de la récupération des méthodes d'expédition"""
        # Configurer le mock
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=[self.mock_token_response, self.mock_shipping_methods_response])
        mock_response.text = AsyncMock(return_value=json.dumps(self.mock_shipping_methods_response))
        mock_response.__aenter__.return_value = mock_response
        mock_post.return_value = mock_response
        
        # Appeler la méthode
        methods = await self.supplier.get_shipping_methods(self.mock_product_id, "US")
        
        # Vérifier les résultats
        self.assertEqual(len(methods), 2)
        self.assertEqual(methods[0]["name"], "CJPacket")
        self.assertEqual(methods[0]["price"], 2.99)
        self.assertEqual(methods[0]["estimated_days"], "10-15")
        self.assertTrue(methods[0]["tracking_available"])
        
        self.assertEqual(methods[1]["name"], "ePacket")
        self.assertEqual(methods[1]["price"], 3.99)
        
        # Vérifier que les appels API ont été effectués correctement
        self.assertEqual(mock_post.call_count, 2)
        
        # Vérifier les données envoyées à l'API
        args, kwargs = mock_post.call_args
        self.assertIn("logistics/getLogisticsChannel", args[0])
        self.assertEqual(kwargs["json"]["pid"], self.mock_product_id)
        self.assertEqual(kwargs["json"]["countryCode"], "US")
    
    @patch('aiohttp.ClientSession.post')
    async def test_get_product_variants(self, mock_post):
        """Test de la récupération des variantes d'un produit"""
        # Configurer le mock
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=[self.mock_token_response, self.mock_variants_response])
        mock_response.text = AsyncMock(return_value=json.dumps(self.mock_variants_response))
        mock_response.__aenter__.return_value = mock_response
        mock_post.return_value = mock_response
        
        # Appeler la méthode
        variants = await self.supplier.get_product_variants(self.mock_product_id)
        
        # Vérifier les résultats
        self.assertEqual(len(variants), 2)
        self.assertEqual(variants[0]["id"], "var_789")
        self.assertEqual(variants[0]["sku"], "SKU123-1")
        self.assertEqual(variants[0]["name"], "Test Variant")
        self.assertEqual(variants[0]["price"], 10.99)
        self.assertEqual(variants[0]["stock"], 100)
        
        self.assertEqual(variants[1]["id"], "var_790")
        self.assertEqual(variants[1]["sku"], "SKU123-2")
        self.assertEqual(variants[1]["name"], "Test Variant 2")
        self.assertEqual(variants[1]["price"], 11.99)
        self.assertEqual(variants[1]["stock"], 50)
        
        # Vérifier que les appels API ont été effectués correctement
        self.assertEqual(mock_post.call_count, 2)
        
        # Vérifier les données envoyées à l'API
        args, kwargs = mock_post.call_args
        self.assertIn("product/getVariants", args[0])
        self.assertEqual(kwargs["json"]["pid"], self.mock_product_id)
    
    @patch('aiohttp.ClientSession.post')
    async def test_api_error_handling(self, mock_post):
        """Test de la gestion des erreurs API"""
        # Configurer le mock pour une erreur
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value=json.dumps({
            "result": "Error",
            "message": "Invalid product ID",
            "data": None
        }))
        mock_response.__aenter__.return_value = mock_response
        mock_post.return_value = mock_response
        
        # Tester qu'une exception est levée
        with self.assertRaises(Exception) as context:
            await self.supplier.get_product_details("invalid_id")
        
        # Vérifier que le message d'erreur est correct
        self.assertIn("CJ Dropshipping API error: 400", str(context.exception))
    
    @patch('aiohttp.ClientSession.post')
    async def test_token_expiry_renewal(self, mock_post):
        """Test du renouvellement du token expiré"""
        # Configurer le token comme expiré
        self.supplier.access_token = "expired_token"
        self.supplier.token_expiry = 0
        
        # Configurer les mocks pour le renouvellement du token et l'appel API
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=[self.mock_token_response, self.mock_product_details])
        mock_response.text = AsyncMock(return_value=json.dumps(self.mock_product_details))
        mock_response.__aenter__.return_value = mock_response
        mock_post.return_value = mock_response
        
        # Appeler une méthode qui nécessite un token
        await self.supplier.get_product_details(self.mock_product_id)
        
        # Vérifier que le token a été renouvelé
        self.assertEqual(self.supplier.access_token, "fake_access_token")
        self.assertTrue(self.supplier.token_expiry > 0)
        
        # Vérifier que les appels API ont été effectués correctement
        self.assertEqual(mock_post.call_count, 2)
        
        # Vérifier que le premier appel était pour le renouvellement du token
        first_call_args, first_call_kwargs = mock_post.call_args_list[0]
        self.assertIn("authentication/getAccessToken", first_call_args[0])
        
        # Vérifier que le deuxième appel était pour la récupération du produit
        second_call_args, second_call_kwargs = mock_post.call_args_list[1]
        self.assertIn("product/query", second_call_args[0])

# Fonction pour exécuter les tests asynchrones
def run_async_test(test_case):
    """Fonction utilitaire pour exécuter des tests asynchrones"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_case())

# Boucle pour exécuter tous les tests
if __name__ == "__main__":
    unittest.main()
