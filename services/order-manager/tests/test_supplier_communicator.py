import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import sys
import os
from datetime import datetime

# Ajouter le dossier parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.supplier_communicator import SupplierCommunicator
from utils.config_manager import ConfigManager

class TestSupplierCommunicator(unittest.TestCase):
    """Tests unitaires pour le communicateur avec les fournisseurs"""
    
    def setUp(self):
        """Configuration des tests"""
        # Mock des dépendances
        self.config_manager = MagicMock(spec=ConfigManager)
        self.config_manager.get_all_suppliers = MagicMock()
        self.config_manager.get_supplier_config = MagicMock()
        
        # Initialisation de l'objet à tester
        self.supplier_communicator = SupplierCommunicator(self.config_manager)
        
        # Données de test
        self.sample_suppliers = {
            "aliexpress": {
                "name": "AliExpress Dropshipping",
                "api_url": "https://api.aliexpress.com",
                "api_key": "test_key_123",
                "order_endpoint": "/api/orders",
                "tracking_endpoint": "/api/tracking"
            },
            "cjdropshipping": {
                "name": "CJ Dropshipping",
                "api_url": "https://api.cjdropshipping.com",
                "api_key": "test_key_456",
                "order_endpoint": "/api/orders",
                "tracking_endpoint": "/api/tracking"
            }
        }
        
        self.sample_order = {
            "id": 12345,
            "email": "client@example.com",
            "line_items": [
                {
                    "id": 67890,
                    "title": "Produit Test",
                    "quantity": 2,
                    "price": "49.99",
                    "sku": "SKU123"
                }
            ],
            "shipping_address": {
                "first_name": "Jean",
                "last_name": "Dupont",
                "address1": "123 Rue Principale",
                "city": "Paris",
                "province": "\u00cele-de-France",
                "country": "France",
                "zip": "75001",
                "phone": "+33123456789"
            }
        }
    
    @patch('managers.supplier_communicator.SupplierCommunicator._check_supplier_status')
    async def test_get_suppliers(self, mock_check_supplier_status):
        """Test de récupération de la liste des fournisseurs"""
        # Configuration des mocks
        self.config_manager.get_all_suppliers.return_value = self.sample_suppliers
        mock_check_supplier_status.return_value = "active"
        
        # Exécution de la méthode à tester
        result = await self.supplier_communicator.get_suppliers()
        
        # Vérifications
        self.config_manager.get_all_suppliers.assert_called_once()
        self.assertEqual(mock_check_supplier_status.call_count, 2)  # Appelé pour chaque fournisseur
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "aliexpress")
        self.assertEqual(result[0]["name"], "AliExpress Dropshipping")
        self.assertEqual(result[0]["status"], "active")
    
    @patch('managers.supplier_communicator.SupplierCommunicator._format_order_for_supplier')
    async def test_place_order(self, mock_format_order):
        """Test de placement d'une commande auprès d'un fournisseur"""
        # Configuration des mocks
        self.config_manager.get_supplier_config.return_value = self.sample_suppliers["aliexpress"]
        formatted_order = {
            "reference": "12345",
            "products": [
                {
                    "product_id": "SKU123",
                    "quantity": 2,
                    "price": "49.99"
                }
            ]
        }
        mock_format_order.return_value = formatted_order
        
        # Exécution de la méthode à tester
        result = await self.supplier_communicator.place_order("aliexpress", self.sample_order)
        
        # Vérifications
        self.config_manager.get_supplier_config.assert_called_once_with("aliexpress")
        mock_format_order.assert_called_once_with("aliexpress", self.sample_order)
        self.assertTrue(result["success"])
        self.assertIn("supplier_order_id", result)
        self.assertEqual(result["status"], "processing")
    
    async def test_get_order_status(self):
        """Test de récupération du statut d'une commande auprès d'un fournisseur"""
        # Configuration des mocks
        self.config_manager.get_supplier_config.return_value = self.sample_suppliers["aliexpress"]
        
        # Exécution de la méthode à tester
        result = await self.supplier_communicator.get_order_status("aliexpress", "SUP-12345")
        
        # Vérifications
        self.config_manager.get_supplier_config.assert_called_once_with("aliexpress")
        self.assertEqual(result["supplier_order_id"], "SUP-12345")
        self.assertIn(result["status"], ["pending", "processing", "shipped", "delivered"])
        
        # Vérifier si le suivi est présent pour les statuts appropriés
        if result["status"] in ["shipped", "delivered"]:
            self.assertIsNotNone(result["tracking_info"])
            self.assertIn("tracking_number", result["tracking_info"])
            self.assertIn("carrier", result["tracking_info"])
    
    @patch('managers.supplier_communicator.SupplierCommunicator.get_order_status')
    async def test_cancel_order_success(self, mock_get_order_status):
        """Test d'annulation réussie d'une commande"""
        # Configuration des mocks
        self.config_manager.get_supplier_config.return_value = self.sample_suppliers["aliexpress"]
        mock_get_order_status.return_value = {
            "status": "processing",
            "status_text": "En cours de traitement"
        }
        
        # Exécution de la méthode à tester
        result = await self.supplier_communicator.cancel_order("aliexpress", "SUP-12345", "Customer changed mind")
        
        # Vérifications
        self.config_manager.get_supplier_config.assert_called_once_with("aliexpress")
        mock_get_order_status.assert_called_once_with("aliexpress", "SUP-12345")
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "cancelled")
    
    @patch('managers.supplier_communicator.SupplierCommunicator.get_order_status')
    async def test_cancel_order_failure(self, mock_get_order_status):
        """Test d'annulation échouée d'une commande déjà expédiée"""
        # Configuration des mocks
        self.config_manager.get_supplier_config.return_value = self.sample_suppliers["aliexpress"]
        mock_get_order_status.return_value = {
            "status": "shipped",
            "status_text": "Expédié"
        }
        
        # Exécution de la méthode à tester
        result = await self.supplier_communicator.cancel_order("aliexpress", "SUP-12345")
        
        # Vérifications
        self.config_manager.get_supplier_config.assert_called_once_with("aliexpress")
        mock_get_order_status.assert_called_once_with("aliexpress", "SUP-12345")
        self.assertFalse(result["success"])
        self.assertIn("impossible", result["message"].lower())
    
    async def test_get_product_info(self):
        """Test de récupération d'informations sur un produit"""
        # Configuration des mocks
        self.config_manager.get_supplier_config.return_value = self.sample_suppliers["aliexpress"]
        
        # Exécution de la méthode à tester
        result = await self.supplier_communicator.get_product_info("aliexpress", "SKU123")
        
        # Vérifications
        self.config_manager.get_supplier_config.assert_called_once_with("aliexpress")
        self.assertEqual(result["product_id"], "SKU123")
        self.assertIn("price", result)
        self.assertIn("stock", result)
        self.assertIn("shipping_time", result)
    
    def test_format_for_aliexpress(self):
        """Test du formatage des données pour AliExpress"""
        # Exécution de la méthode à tester
        result = self.supplier_communicator._format_for_aliexpress(self.sample_order)
        
        # Vérifications
        self.assertEqual(result["reference"], "12345")
        self.assertEqual(len(result["products"]), 1)
        self.assertEqual(result["products"][0]["product_id"], "SKU123")
        self.assertEqual(result["products"][0]["quantity"], 2)
        self.assertEqual(result["shipping"]["country"], self.sample_order["shipping_address"]["country"])
        self.assertEqual(result["shipping"]["city"], self.sample_order["shipping_address"]["city"])
    
    def test_format_for_cjdropshipping(self):
        """Test du formatage des données pour CJ Dropshipping"""
        # Exécution de la méthode à tester
        result = self.supplier_communicator._format_for_cjdropshipping(self.sample_order)
        
        # Vérifications
        self.assertEqual(result["orderNumber"], "12345")
        self.assertEqual(len(result["products"]), 1)
        self.assertEqual(result["products"][0]["vid"], "SKU123")
        self.assertEqual(result["products"][0]["quantity"], 2)
        self.assertEqual(result["address"]["country"], self.sample_order["shipping_address"]["country"])
        self.assertEqual(result["address"]["city"], self.sample_order["shipping_address"]["city"])
    
    def test_get_tracking_url(self):
        """Test de génération d'URL de suivi"""
        # Test avec un transporteur connu
        dhl_url = self.supplier_communicator._get_tracking_url("TRK123", "dhl")
        self.assertIn("TRK123", dhl_url)
        self.assertIn("dhl.com", dhl_url)
        
        # Test avec un transporteur inconnu
        generic_url = self.supplier_communicator._get_tracking_url("TRK123", "unknown_carrier")
        self.assertIn("TRK123", generic_url)
        self.assertIn("trackingmore.com", generic_url)

if __name__ == '__main__':
    unittest.main()