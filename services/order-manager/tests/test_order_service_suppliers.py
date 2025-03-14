#!/usr/bin/env python3
"""
Tests unitaires pour le service de gestion des commandes côté fournisseurs
Fait partie du projet Dropshipping Crew AI
"""

import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from services.order_service_suppliers import OrderServiceSuppliers
from storage import OrderRepository
from integrations.suppliers.communicator import SupplierCommunicator
from models import SupplierType


class TestOrderServiceSuppliers(unittest.TestCase):
    """
    Tests pour la classe OrderServiceSuppliers.
    """
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        self.repository = MagicMock(spec=OrderRepository)
        self.communicator = MagicMock(spec=SupplierCommunicator)
        self.service = OrderServiceSuppliers(repository=self.repository, communicator=self.communicator)
        
        # Données de test
        self.test_order_data = {
            "id": "TEST-123",
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
                    "product_id": "PROD1",
                    "variant_id": "VAR1",
                    "quantity": 2,
                    "shipping_method": "Standard"
                },
                {
                    "product_id": "PROD2",
                    "variant_id": "VAR2",
                    "quantity": 1,
                    "shipping_method": "Express"
                }
            ]
        }
        
        # Configuration du mock du sélecteur de fournisseur
        self.service.supplier_selector = MagicMock()
        self.service.supplier_selector._auto_select_supplier = AsyncMock()
        
        # Test pour 2 produits: un produit d'AliExpress et un produit de CJ Dropshipping
        self.service.supplier_selector._auto_select_supplier.side_effect = [
            (SupplierType.ALIEXPRESS, {"success": True, "id": "PROD1"}),
            (SupplierType.CJ_DROPSHIPPING, {"success": True, "id": "PROD2"})
        ]
        
        # Mock pour le communicator
        self.communicator.place_order = AsyncMock()
        self.communicator.place_order.side_effect = [
            MagicMock(
                success=True, 
                supplier_order_id="ALI123",
                status="pending",
                error_message=None,
                details={}
            ),
            MagicMock(
                success=True, 
                supplier_order_id="CJ123",
                status="processing",
                error_message=None,
                details={}
            )
        ]
    
    async def _test_process_supplier_order(self):
        """Méthode helper pour tester process_supplier_order."""
        # Appel de la méthode à tester
        result = await self.service.process_supplier_order(self.test_order_data, "auto")
        return result
    
    def test_process_supplier_order_success(self):
        """Test de traitement de commande réussi avec plusieurs fournisseurs."""
        # Exécution du test
        result = asyncio.run(self._test_process_supplier_order())
        
        # Vérifications
        self.assertTrue(result["success"])
        self.assertEqual(len(result["orders"]), 2)
        
        # Vérifier que les commandes ont été passées chez les bons fournisseurs
        suppliers = set(order["supplier"] for order in result["orders"])
        self.assertEqual(suppliers, {SupplierType.ALIEXPRESS, SupplierType.CJ_DROPSHIPPING})
        
        # Vérifier que le sélecteur de fournisseur a été appelé pour chaque produit
        self.assertEqual(self.service.supplier_selector._auto_select_supplier.call_count, 2)
        
        # Vérifier que les commandes ont été passées
        self.assertEqual(self.communicator.place_order.call_count, 2)
        
        # Vérifier que les résultats ont été enregistrés dans la base de données
        self.assertEqual(self.repository.create_supplier_order.call_count, 2)
    
    async def _test_process_supplier_order_error(self):
        """Méthode helper pour tester process_supplier_order avec erreur."""
        # Modifier les mocks pour simuler une erreur
        self.service.supplier_selector._auto_select_supplier.side_effect = [
            (None, {"error": "Product not available"}),
            (SupplierType.CJ_DROPSHIPPING, {"success": True, "id": "PROD2"})
        ]
        
        # Appel de la méthode à tester
        result = await self.service.process_supplier_order(self.test_order_data, "auto")
        return result
    
    def test_process_supplier_order_partial_error(self):
        """Test de traitement de commande avec erreur partielle."""
        # Exécution du test
        result = asyncio.run(self._test_process_supplier_order_error())
        
        # Vérifications: l'opération réussit quand même car un produit est disponible
        self.assertTrue(result["success"])
        
        # Une seule commande est passée
        self.assertEqual(len(result["orders"]), 1)
        self.assertEqual(result["orders"][0]["supplier"], SupplierType.CJ_DROPSHIPPING)
        
        # Le sélecteur a été appelé pour chaque produit
        self.assertEqual(self.service.supplier_selector._auto_select_supplier.call_count, 2)
        
        # Une seule commande a été passée
        self.assertEqual(self.communicator.place_order.call_count, 1)
    
    async def _test_process_supplier_order_all_errors(self):
        """Méthode helper pour tester process_supplier_order avec erreur totale."""
        # Modifier les mocks pour simuler une erreur pour tous les produits
        self.service.supplier_selector._auto_select_supplier.side_effect = [
            (None, {"error": "Product not available"}),
            (None, {"error": "Product not available"})
        ]
        
        # Appel de la méthode à tester
        result = await self.service.process_supplier_order(self.test_order_data, "auto")
        return result
    
    def test_process_supplier_order_all_errors(self):
        """Test de traitement de commande avec erreur pour tous les produits."""
        # Exécution du test
        result = asyncio.run(self._test_process_supplier_order_all_errors())
        
        # Vérifications: l'opération échoue car aucun produit n'est disponible
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        
        # Le sélecteur a été appelé pour chaque produit
        self.assertEqual(self.service.supplier_selector._auto_select_supplier.call_count, 2)
        
        # Aucune commande n'a été passée
        self.assertEqual(self.communicator.place_order.call_count, 0)
    
    async def _test_supplier_selection_strategies(self):
        """Méthode helper pour tester les différentes stratégies de sélection."""
        # Mock pour le communicator get_product_details
        self.communicator.get_product_details = AsyncMock()
        self.communicator.get_product_details.side_effect = [
            {"success": True, "id": "PROD1", "price": {"min": 10}},  # ALIEXPRESS
            {"success": True, "id": "PROD1", "price": {"min": 12}}   # CJ_DROPSHIPPING
        ]
        
        # Test des différentes stratégies
        results = {}
        
        for strategy in ["auto", "cheapest", "fastest", "default"]:
            # Réinitialiser le mock
            self.communicator.get_product_details.reset_mock()
            self.communicator.get_product_details.side_effect = [
                {"success": True, "id": "PROD1", "price": {"min": 10}},  # ALIEXPRESS
                {"success": True, "id": "PROD1", "price": {"min": 12}}   # CJ_DROPSHIPPING
            ]
            
            # Appel de la méthode à tester avec la stratégie spécifiée
            strategy_method = getattr(self.service, f"_select_{strategy}_supplier")
            supplier, details = await strategy_method("PROD1", "VAR1")
            
            results[strategy] = (supplier, details)
        
        return results
    
    def test_supplier_selection_strategies(self):
        """Test des différentes stratégies de sélection de fournisseur."""
        # Exécution du test
        results = asyncio.run(self._test_supplier_selection_strategies())
        
        # Pour la stratégie "cheapest", AliExpress devrait être sélectionné
        # (prix 10 vs 12 pour CJ Dropshipping)
        self.assertEqual(results["cheapest"][0], SupplierType.ALIEXPRESS)
        
        # Pour la stratégie "default", le fournisseur par défaut devrait être sélectionné
        # (AliExpress est le défaut par défaut)
        self.assertEqual(results["default"][0], SupplierType.ALIEXPRESS)
        
        # Les autres stratégies ne sont pas testées ici car elles dépendent de l'implémentation spécifique


if __name__ == '__main__':
    unittest.main()
