import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import sys
import os
from datetime import datetime

# Ajouter le dossier parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.order_processor import OrderProcessor
from utils.config_manager import ConfigManager

class TestOrderProcessor(unittest.TestCase):
    """Tests unitaires pour le processeur de commandes"""
    
    def setUp(self):
        """Configuration des tests"""
        # Mock des dépendances
        self.shopify_client = MagicMock()
        self.shopify_client.get_order = AsyncMock()
        self.shopify_client.update_order_status = AsyncMock()
        self.shopify_client.create_fulfillment = AsyncMock()
        self.shopify_client.cancel_order = AsyncMock()
        self.shopify_client.refund_order = AsyncMock()
        
        self.config_manager = MagicMock(spec=ConfigManager)
        self.config_manager.get = MagicMock()
        self.config_manager.get_supplier_config = MagicMock()
        
        # Initialisation de l'objet à tester
        self.order_processor = OrderProcessor(self.shopify_client, self.config_manager)
        
        # Données de test
        self.sample_order = {
            "id": 12345,
            "email": "client@example.com",
            "total_price": "99.99",
            "financial_status": "paid",
            "fulfillment_status": None,
            "customer": {
                "first_name": "Jean",
                "last_name": "Dupont",
                "email": "client@example.com"
            },
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
            },
            "created_at": datetime.now().isoformat()
        }
    
    @patch('managers.order_processor.OrderProcessor._requires_manual_review')
    @patch('managers.order_processor.OrderProcessor.process_order')
    async def test_process_new_order_auto_process(self, mock_process_order, mock_requires_review):
        """Test du traitement automatique d'une nouvelle commande"""
        # Configuration des mocks
        mock_requires_review.return_value = False
        self.config_manager.get.return_value = True  # auto_process activé
        mock_process_order.return_value = {"status": "processed", "order_id": 12345}
        
        # Exécution de la méthode à tester
        result = await self.order_processor.process_new_order(self.sample_order)
        
        # Vérifications
        mock_requires_review.assert_called_once_with(self.sample_order)
        mock_process_order.assert_called_once_with(12345, "process", False)
        self.assertEqual(result["status"], "processed")
    
    @patch('managers.order_processor.OrderProcessor._requires_manual_review')
    async def test_process_new_order_manual_review(self, mock_requires_review):
        """Test d'une commande nécessitant une revue manuelle"""
        # Configuration des mocks
        mock_requires_review.return_value = True
        self.shopify_client.update_order_status.return_value = {}
        
        # Exécution de la méthode à tester
        result = await self.order_processor.process_new_order(self.sample_order)
        
        # Vérifications
        mock_requires_review.assert_called_once_with(self.sample_order)
        self.shopify_client.update_order_status.assert_called_once_with(12345, "pending", "on_hold")
        self.assertEqual(result["status"], "pending_review")
    
    @patch('managers.order_processor.OrderProcessor._determine_supplier')
    @patch('managers.order_processor.OrderProcessor._forward_to_supplier')
    async def test_process_order_success(self, mock_forward_to_supplier, mock_determine_supplier):
        """Test du traitement d'une commande avec succès"""
        # Configuration des mocks
        self.shopify_client.get_order.return_value = self.sample_order
        mock_determine_supplier.return_value = {"id": "aliexpress", "name": "AliExpress"}
        mock_forward_to_supplier.return_value = {
            "success": True,
            "supplier_order_id": "SUP-12345",
            "tracking_number": "TRK123456",
            "carrier": "dhl"
        }
        
        # Exécution de la méthode à tester
        result = await self.order_processor.process_order(12345, "process")
        
        # Vérifications
        self.shopify_client.get_order.assert_called_once_with(12345)
        mock_determine_supplier.assert_called_once_with(self.sample_order)
        mock_forward_to_supplier.assert_called_once_with(self.sample_order, {"id": "aliexpress", "name": "AliExpress"})
        self.shopify_client.update_order_status.assert_called_once()
        self.assertEqual(result["status"], "processed")
    
    @patch('managers.order_processor.OrderProcessor._requires_manual_review')
    async def test_requires_manual_review_high_value(self, mock_requires_manual_review):
        """Test de la détection des commandes à haute valeur"""
        # Commande avec un montant supérieur au seuil
        high_value_order = self.sample_order.copy()
        high_value_order["total_price"] = "150.00"
        
        # Configuration du mock
        self.config_manager.get.return_value = 100.0  # seuil de revue manuelle
        
        # Appel direct de la méthode cible sans passer par le mock
        result = await self.order_processor._requires_manual_review(high_value_order)
        
        # Vérifications
        self.config_manager.get.assert_called_with("order_processing.manual_review_threshold", 100.0)
        self.assertTrue(result)  # La revue manuelle est requise
    
    async def test_get_order_status(self):
        """Test de la récupération du statut d'une commande"""
        # Configuration du mock
        order_with_fulfillment = self.sample_order.copy()
        order_with_fulfillment["fulfillments"] = [
            {
                "id": 98765,
                "tracking_number": "TRK123456",
                "tracking_company": "DHL",
                "status": "in_transit",
                "created_at": datetime.now().isoformat()
            }
        ]
        self.shopify_client.get_order.return_value = order_with_fulfillment
        
        # Exécution de la méthode à tester
        result = await self.order_processor.get_order_status(12345)
        
        # Vérifications
        self.shopify_client.get_order.assert_called_once_with(12345)
        self.assertEqual(result["order_id"], 12345)
        self.assertEqual(result["financial_status"], "paid")
        self.assertEqual(len(result["fulfillments"]), 1)
        self.assertEqual(result["fulfillments"][0]["tracking_number"], "TRK123456")

if __name__ == '__main__':
    unittest.main()