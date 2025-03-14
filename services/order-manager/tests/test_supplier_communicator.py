#!/usr/bin/env python3
"""
Tests unitaires pour le communicateur des fournisseurs
Fait partie du projet Dropshipping Crew AI
"""

import os
import json
import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp

# Import du module à tester
from integrations.suppliers.communicator import SupplierCommunicator
from models import SupplierType


class TestSupplierCommunicator(unittest.TestCase):
    """
    Tests pour la classe SupplierCommunicator.
    """
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        # Configuration de l'environnement pour les tests
        os.environ["ALIEXPRESS_API_KEY"] = "test_aliexpress_key"
        os.environ["CJ_DROPSHIPPING_API_KEY"] = "test_cj_key"
        
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
                "country_code": "US",
                "country": "United States"
            },
            "line_items": [
                {
                    "variant_id": "VAR456",
                    "quantity": 2,
                    "shipping_method": "Standard"
                }
            ]
        }
        
        self.test_supplier_order_id = "SUP12345678"
    
    @patch('integrations.suppliers.aliexpress.AliExpressSupplier.place_order')
    async def _test_place_order_aliexpress(self, mock_place_order):
        """Helper pour tester place_order avec AliExpress."""
        mock_place_order.return_value = AsyncMock(return_value={
            "success": True,
            "supplier_order_id": self.test_supplier_order_id,
            "status": "pending"
        })
        
        result = await self.communicator.place_order(SupplierType.ALIEXPRESS, self.test_order_data)
        return result, mock_place_order
    
    @patch('integrations.suppliers.cjdropshipping.CJDropshippingSupplier.place_order')
    async def _test_place_order_cj(self, mock_place_order):
        """Helper pour tester place_order avec CJ Dropshipping."""
        mock_place_order.return_value = AsyncMock(return_value={
            "success": True,
            "supplier_order_id": self.test_supplier_order_id,
            "status": "pending"
        })
        
        result = await self.communicator.place_order(SupplierType.CJ_DROPSHIPPING, self.test_order_data)
        return result, mock_place_order
    
    def test_place_order_aliexpress(self):
        """Test de placement de commande via AliExpress."""
        result, mock_place_order = asyncio.run(self._test_place_order_aliexpress())
        
        # Vérifications
        self.assertTrue(result.success)
        self.assertEqual(result.supplier_order_id, self.test_supplier_order_id)
        mock_place_order.assert_called_once_with(self.test_order_data)
    
    def test_place_order_cj(self):
        """Test de placement de commande via CJ Dropshipping."""
        result, mock_place_order = asyncio.run(self._test_place_order_cj())
        
        # Vérifications
        self.assertTrue(result.success)
        self.assertEqual(result.supplier_order_id, self.test_supplier_order_id)
        mock_place_order.assert_called_once_with(self.test_order_data)
    
    @patch('integrations.suppliers.aliexpress.AliExpressSupplier.get_order_status')
    async def _test_get_order_status(self, mock_get_status):
        """Helper pour tester get_order_status."""
        mock_get_status.return_value = AsyncMock(return_value={
            "success": True,
            "supplier_order_id": self.test_supplier_order_id,
            "status": "shipped"
        })
        
        result = await self.communicator.get_order_status(SupplierType.ALIEXPRESS, self.test_supplier_order_id)
        return result, mock_get_status
    
    def test_get_order_status(self):
        """Test de récupération du statut de commande."""
        result, mock_get_status = asyncio.run(self._test_get_order_status())
        
        # Vérifications
        self.assertTrue(result.success)
        self.assertEqual(result.status, "shipped")
        mock_get_status.assert_called_once_with(self.test_supplier_order_id)
    
    @patch('integrations.suppliers.cjdropshipping.CJDropshippingSupplier.get_tracking_info')
    async def _test_get_tracking_info(self, mock_get_tracking):
        """Helper pour tester get_tracking_info."""
        mock_get_tracking.return_value = AsyncMock(return_value={
            "success": True,
            "supplier_order_id": self.test_supplier_order_id,
            "tracking_number": "TRK123456",
            "tracking_url": "https://tracking.example.com/TRK123456",
            "status": "shipped"
        })
        
        result = await self.communicator.get_tracking_info(SupplierType.CJ_DROPSHIPPING, self.test_supplier_order_id)
        return result, mock_get_tracking
    
    def test_get_tracking_info(self):
        """Test de récupération des informations de suivi."""
        result, mock_get_tracking = asyncio.run(self._test_get_tracking_info())
        
        # Vérifications
        self.assertTrue(result.success)
        self.assertEqual(result.tracking_number, "TRK123456")
        mock_get_tracking.assert_called_once_with(self.test_supplier_order_id)
    
    @patch('integrations.suppliers.aliexpress.AliExpressSupplier.search_products')
    async def _test_search_products(self, mock_search):
        """Helper pour tester search_products."""
        mock_search.return_value = AsyncMock(return_value={
            "success": True,
            "total": 100,
            "products": [{"id": "123", "title": "Test Product"}]
        })
        
        result = await self.communicator.search_products(SupplierType.ALIEXPRESS, "test query", 1, 20)
        return result, mock_search
    
    def test_search_products(self):
        """Test de recherche de produits."""
        result, mock_search = asyncio.run(self._test_search_products())
        
        # Vérifications
        self.assertTrue(result["success"])
        self.assertEqual(len(result["products"]), 1)
        mock_search.assert_called_once_with("test query", 1, 20)
    
    def test_get_supported_suppliers(self):
        """Test de récupération des fournisseurs supportés."""
        suppliers = self.communicator.get_supported_suppliers()
        
        # Vérification que les fournisseurs sont bien présents
        self.assertIn("ALIEXPRESS", suppliers)
        self.assertIn("CJ_DROPSHIPPING", suppliers)
    
    @patch('integrations.suppliers.aliexpress.AliExpressSupplier')
    @patch('integrations.suppliers.cjdropshipping.CJDropshippingSupplier')
    def test_supplier_loading(self, mock_cj_class, mock_aliexpress_class):
        """Test du chargement dynamique des fournisseurs."""
        # Supprimer les variables d'environnement pour le test
        if "ALIEXPRESS_API_KEY" in os.environ:
            del os.environ["ALIEXPRESS_API_KEY"]
        
        if "CJ_DROPSHIPPING_API_KEY" in os.environ:
            del os.environ["CJ_DROPSHIPPING_API_KEY"]
        
        # Créer un nouveau communicateur avec les mocks
        communicator = SupplierCommunicator()
        
        # Tester un fournisseur sans clé API
        result = asyncio.run(communicator.place_order(SupplierType.ALIEXPRESS, self.test_order_data))
        self.assertFalse(result.success)
        self.assertIn("non disponible", result.error_message)
        
        # Maintenant ajouter la clé API et tester à nouveau
        os.environ["ALIEXPRESS_API_KEY"] = "test_key"
        result = asyncio.run(communicator.place_order(SupplierType.ALIEXPRESS, self.test_order_data))
        
        # La clé a été ajoutée, mais comme on a mocké la classe, ça échouera quand même
        # Cependant, on peut vérifier que la classe a été instanciée
        mock_aliexpress_class.assert_called()
    
    def test_unsupported_supplier(self):
        """Test avec un fournisseur non supporté."""
        result = asyncio.run(self.communicator.place_order("UNSUPPORTED_SUPPLIER", self.test_order_data))
        
        # Vérifications
        self.assertFalse(result.success)
        self.assertIn("non supporté", result.error_message)
    
    @patch('integrations.suppliers.aliexpress.AliExpressSupplier.place_order')
    def test_exception_handling(self, mock_place_order):
        """Test de la gestion des exceptions."""
        # Simuler une exception
        mock_place_order.side_effect = Exception("Test exception")
        
        result = asyncio.run(self.communicator.place_order(SupplierType.ALIEXPRESS, self.test_order_data))
        
        # Vérifications
        self.assertFalse(result.success)
        self.assertIn("Test exception", result.error_message)


if __name__ == '__main__':
    unittest.main()
