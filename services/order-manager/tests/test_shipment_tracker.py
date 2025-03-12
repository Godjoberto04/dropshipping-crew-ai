import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import sys
import os
from datetime import datetime

# Ajouter le dossier parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.shipment_tracker import ShipmentTracker
from utils.config_manager import ConfigManager

class TestShipmentTracker(unittest.TestCase):
    """Tests unitaires pour le tracker d'expédition"""
    
    def setUp(self):
        """Configuration des tests"""
        # Mock des dépendances
        self.shopify_client = MagicMock()
        self.shopify_client.get_order = AsyncMock()
        self.shopify_client.update_order_status = AsyncMock()
        self.shopify_client.create_fulfillment = AsyncMock()
        
        self.config_manager = MagicMock(spec=ConfigManager)
        self.config_manager.get = MagicMock()
        
        # Initialisation de l'objet à tester
        self.shipment_tracker = ShipmentTracker(self.shopify_client, self.config_manager)
        
        # Données de test
        self.sample_order = {
            "id": 12345,
            "fulfillments": [
                {
                    "id": 98765,
                    "tracking_number": "TRK123456",
                    "tracking_company": "DHL",
                    "status": "in_transit",
                    "created_at": datetime.now().isoformat()
                }
            ],
            "financial_status": "paid",
            "fulfillment_status": "partial",
            "created_at": datetime.now().isoformat()
        }
    
    @patch('managers.shipment_tracker.ShipmentTracker._get_shipment_status')
    async def test_track_shipment_with_tracking_number(self, mock_get_shipment_status):
        """Test de suivi d'expédition avec numéro de suivi fourni"""
        # Configuration des mocks
        shipment_status = {
            "status": "in_transit",
            "status_text": "En transit",
            "location": "Centre de distribution",
            "last_update": datetime.now().isoformat(),
            "estimated_delivery": (datetime.now()).isoformat(),
            "events": [
                {
                    "timestamp": (datetime.now()).isoformat(),
                    "status": "in_transit",
                    "location": "Centre de distribution",
                    "description": "Colis en transit"
                }
            ]
        }
        mock_get_shipment_status.return_value = shipment_status
        
        # Exécution de la méthode à tester
        result = await self.shipment_tracker.track_shipment(12345, "TRK123456", "dhl")
        
        # Vérifications
        mock_get_shipment_status.assert_called_once_with("TRK123456", "dhl")
        self.assertEqual(result["order_id"], 12345)
        self.assertEqual(result["tracking_number"], "TRK123456")
        self.assertEqual(result["status"], "in_transit")
    
    @patch('managers.shipment_tracker.ShipmentTracker._get_tracking_from_shopify')
    @patch('managers.shipment_tracker.ShipmentTracker._get_shipment_status')
    async def test_track_shipment_without_tracking_number(self, mock_get_shipment_status, mock_get_tracking_from_shopify):
        """Test de suivi d'expédition sans numéro de suivi fourni"""
        # Configuration des mocks
        tracking_info = {
            "tracking_number": "TRK123456",
            "carrier": "dhl",
            "tracking_company": "DHL",
            "fulfillment_id": 98765
        }
        mock_get_tracking_from_shopify.return_value = tracking_info
        
        shipment_status = {
            "status": "in_transit",
            "status_text": "En transit",
            "location": "Centre de distribution",
            "last_update": datetime.now().isoformat(),
            "estimated_delivery": (datetime.now()).isoformat(),
            "events": []
        }
        mock_get_shipment_status.return_value = shipment_status
        
        # Exécution de la méthode à tester
        result = await self.shipment_tracker.track_shipment(12345)  # Sans tracking_number ni carrier
        
        # Vérifications
        mock_get_tracking_from_shopify.assert_called_once_with(12345)
        mock_get_shipment_status.assert_called_once_with("TRK123456", "dhl")
        self.assertEqual(result["order_id"], 12345)
        self.assertEqual(result["tracking_number"], "TRK123456")
        self.assertEqual(result["carrier"], "DHL Express")
    
    @patch('managers.shipment_tracker.ShipmentTracker._get_shipment_status')
    @patch('managers.shipment_tracker.ShipmentTracker._update_shopify_fulfillment_status')
    async def test_track_shipment_delivered(self, mock_update_shopify_fulfillment_status, mock_get_shipment_status):
        """Test de suivi d'expédition pour un colis livré"""
        # Configuration des mocks
        shipment_status = {
            "status": "delivered",
            "status_text": "Livré",
            "location": "Adresse de livraison",
            "last_update": datetime.now().isoformat(),
            "estimated_delivery": (datetime.now()).isoformat(),
            "events": []
        }
        mock_get_shipment_status.return_value = shipment_status
        mock_update_shopify_fulfillment_status.return_value = True
        
        # Exécution de la méthode à tester
        result = await self.shipment_tracker.track_shipment(12345, "TRK123456", "dhl")
        
        # Vérifications
        mock_get_shipment_status.assert_called_once_with("TRK123456", "dhl")
        mock_update_shopify_fulfillment_status.assert_called_once_with(12345, "delivered")
        self.assertEqual(result["status"], "delivered")
    
    async def test_get_tracking_from_shopify(self):
        """Test de récupération des informations de suivi depuis Shopify"""
        # Configuration du mock
        self.shopify_client.get_order.return_value = self.sample_order
        
        # Exécution de la méthode à tester
        result = await self.shipment_tracker._get_tracking_from_shopify(12345)
        
        # Vérifications
        self.shopify_client.get_order.assert_called_once_with(12345)
        self.assertEqual(result["tracking_number"], "TRK123456")
        self.assertEqual(result["tracking_company"], "DHL")
        self.assertEqual(result["carrier"], "dhl")
        self.assertEqual(result["fulfillment_id"], 98765)
    
    @patch('managers.shipment_tracker.ShipmentTracker.track_shipment')
    async def test_update_all_shipments(self, mock_track_shipment):
        """Test de mise à jour de toutes les expéditions"""
        # Configuration des mocks
        orders = [
            {
                "id": 12345,
                "fulfillment_status": "in_transit",
                "fulfillments": [{}]
            },
            {
                "id": 67890,
                "fulfillment_status": "out_for_delivery",
                "fulfillments": [{}]
            }
        ]
        self.shopify_client.get_fulfilled_orders.return_value = orders
        
        tracking_result = {
            "order_id": 12345,
            "status": "updated",
            "tracking_number": "TRK123456"
        }
        mock_track_shipment.return_value = tracking_result
        
        # Exécution de la méthode à tester
        results = await self.shipment_tracker.update_all_shipments()
        
        # Vérifications
        self.shopify_client.get_fulfilled_orders.assert_called_once()
        self.assertEqual(mock_track_shipment.call_count, 2)  # Appelé pour chaque commande
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertEqual(result["status"], "updated")
            self.assertEqual(result["tracking_result"], tracking_result)

if __name__ == '__main__':
    unittest.main()