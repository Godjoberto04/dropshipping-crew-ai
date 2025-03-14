#!/usr/bin/env python3
"""
Tests unitaires pour le communicateur avec les fournisseurs
Fait partie du projet Dropshipping Crew AI
"""

import os
import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from models import SupplierType
from integrations.suppliers import SupplierCommunicator, OrderResult
from integrations.suppliers.aliexpress import AliExpressSupplier
from integrations.suppliers.cjdropshipping import CJDropshippingSupplier


class TestSupplierCommunicator(unittest.TestCase):
    """
    Tests pour la classe SupplierCommunicator.
    """
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        # Configurations de test pour les fournisseurs
        self.aliexpress_api_key = "test_aliexpress_key"
        self.cj_dropshipping_api_key = "test_cjdropshipping_key"
        
        # Patcher les variables d'environnement pour les tests
        self.env_patcher = patch.dict(os.environ, {
            "ALIEXPRESS_API_KEY": self.aliexpress_api_key,
            "CJ_DROPSHIPPING_API_KEY": self.cj_dropshipping_api_key
        })
        self.env_patcher.start()
        
        # Créer l'instance à tester
        self.communicator = SupplierCommunicator()
        
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
                "country": "United States",
                "country_code": "US"
            },
            "line_items": [
                {
                    "variant_id": "VAR456",
                    "quantity": 2
                }
            ]
        }
    
    def tearDown(self):
        """Nettoyage après les tests."""
        self.env_patcher.stop()
    
    @patch('integrations.suppliers.aliexpress.AliExpressSupplier.place_order')
    async def test_place_order_aliexpress(self, mock_place_order):
        """Test de place_order avec AliExpress."""
        # Configurer le mock
        mock_result = OrderResult(
            success=True,
            supplier_order_id="AE12345678",
            status="pending"
        )
        mock_place_order.return_value = mock_result
        
        # Appel de la méthode à tester
        result = await self.communicator.place_order(
            SupplierType.ALIEXPRESS,
            self.test_order_data
        )
        
        # Vérifications
        self.assertTrue(result.success)
        self.assertEqual(result.supplier_order_id, "AE12345678")
        self.assertEqual(result.status, "pending")
        mock_place_order.assert_called_once_with(self.test_order_data)
    
    @patch('integrations.suppliers.cjdropshipping.CJDropshippingSupplier.place_order')
    async def test_place_order_cjdropshipping(self, mock_place_order):
        """Test de place_order avec CJ Dropshipping."""
        # Configurer le mock
        mock_result = OrderResult(
            success=True,
            supplier_order_id="CJ12345678",
            status="pending"
        )
        mock_place_order.return_value = mock_result
        
        # Appel de la méthode à tester
        result = await self.communicator.place_order(
            SupplierType.CJ_DROPSHIPPING,
            self.test_order_data
        )
        
        # Vérifications
        self.assertTrue(result.success)
        self.assertEqual(result.supplier_order_id, "CJ12345678")
        self.assertEqual(result.status, "pending")
        mock_place_order.assert_called_once_with(self.test_order_data)
    
    @patch('integrations.suppliers.cjdropshipping.CJDropshippingSupplier.get_order_status')
    async def test_get_order_status_cjdropshipping(self, mock_get_status):
        """Test de get_order_status avec CJ Dropshipping."""
        # Configurer le mock
        mock_result = OrderResult(
            success=True,
            supplier_order_id="CJ12345678",
            status="shipped"
        )
        mock_get_status.return_value = mock_result
        
        # Appel de la méthode à tester
        result = await self.communicator.get_order_status(
            SupplierType.CJ_DROPSHIPPING,
            "CJ12345678"
        )
        
        # Vérifications
        self.assertTrue(result.success)
        self.assertEqual(result.status, "shipped")
        mock_get_status.assert_called_once_with("CJ12345678")
    
    @patch('integrations.suppliers.cjdropshipping.CJDropshippingSupplier.get_tracking_info')
    async def test_get_tracking_info_cjdropshipping(self, mock_get_tracking):
        """Test de get_tracking_info avec CJ Dropshipping."""
        # Configurer le mock
        mock_result = OrderResult(
            success=True,
            supplier_order_id="CJ12345678",
            tracking_number="LX123456789CN",
            tracking_url="https://global.cainiao.com/detail.htm?mailNo=LX123456789CN",
            shipping_company="CJPacket",
            status="shipped"
        )
        mock_get_tracking.return_value = mock_result
        
        # Appel de la méthode à tester
        result = await self.communicator.get_tracking_info(
            SupplierType.CJ_DROPSHIPPING,
            "CJ12345678"
        )
        
        # Vérifications
        self.assertTrue(result.success)
        self.assertEqual(result.tracking_number, "LX123456789CN")
        self.assertEqual(result.shipping_company, "CJPacket")
        mock_get_tracking.assert_called_once_with("CJ12345678")
    
    @patch('integrations.suppliers.cjdropshipping.CJDropshippingSupplier.cancel_order')
    async def test_cancel_order_cjdropshipping(self, mock_cancel):
        """Test de cancel_order avec CJ Dropshipping."""
        # Configurer le mock
        mock_result = OrderResult(
            success=True,
            supplier_order_id="CJ12345678",
            status="cancelled"
        )
        mock_cancel.return_value = mock_result
        
        # Appel de la méthode à tester
        result = await self.communicator.cancel_order(
            SupplierType.CJ_DROPSHIPPING,
            "CJ12345678",
            "Changed my mind"
        )
        
        # Vérifications
        self.assertTrue(result.success)
        self.assertEqual(result.status, "cancelled")
        mock_cancel.assert_called_once_with("CJ12345678", "Changed my mind")
    

# Pour exécuter les tests asynchrones avec unittest
def run_async_test(test_case, method):
    """Exécute un test asynchrone."""
    return asyncio.run(method())


if __name__ == '__main__':
    # Patch the TestCase to run async tests
    original_run = unittest.TestCase.run
    
    def patched_run(self, result=None):
        method_name = self._testMethodName
        method = getattr(self, method_name)
        if asyncio.iscoroutinefunction(method):
            setattr(self, method_name, lambda: run_async_test(self, method))
        return original_run(self, result)
    
    unittest.TestCase.run = patched_run
    
    unittest.main()
