#!/usr/bin/env python3
"""
Tests unitaires pour le sélecteur de fournisseur
Fait partie du projet Dropshipping Crew AI
"""

import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from integrations.suppliers.supplier_selector import SupplierSelector
from integrations.suppliers.communicator import SupplierCommunicator
from models import SupplierType


class TestSupplierSelector(unittest.TestCase):
    """
    Tests pour la classe SupplierSelector.
    """
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        self.communicator = MagicMock(spec=SupplierCommunicator)
        self.selector = SupplierSelector(self.communicator)
        
        # ID de test
        self.test_product_id = "TEST123"
        self.test_variant_id = "VAR456"
        
        # Données simulées pour AliExpress
        self.aliexpress_details = {
            "success": True,
            "id": self.test_product_id,
            "title": "Test Product",
            "description": "Test description",
            "price": {"min": 19.99, "max": 29.99, "currency": "USD"},
            "images": ["https://example.com/image1.jpg"],
            "variations": [
                {
                    "id": self.test_variant_id,
                    "price": 24.99,
                    "stock": 50,
                    "properties": {"color": "red", "size": "M"}
                }
            ],
            "shipping_info": {
                "methods": [
                    {
                        "name": "Standard",
                        "price": 5.99,
                        "currency": "USD",
                        "delivery_time": "15-20 days"
                    }
                ]
            },
            "seller": {
                "rating": 4.7,
                "name": "Test Seller"
            }
        }
        
        # Données simulées pour CJ Dropshipping
        self.cj_details = {
            "success": True,
            "id": self.test_product_id,
            "title": "Test Product",
            "description": "Test description",
            "price": {"min": 22.99, "max": 32.99, "currency": "USD"},
            "images": ["https://example.com/image1.jpg"],
            "variations": [
                {
                    "id": self.test_variant_id,
                    "price": 27.99,
                    "stock": 100,
                    "properties": {"color": "red", "size": "M"}
                }
            ],
            "shipping_info": {
                "methods": [
                    {
                        "name": "Standard",
                        "price": 3.99,
                        "currency": "USD",
                        "delivery_time": "10-15 days"
                    }
                ]
            },
            "seller": {
                "rating": 4.9,
                "name": "Test Seller"
            }
        }
    
    async def _mock_get_product_details(self, supplier, product_id):
        """Mock pour la fonction get_product_details."""
        if supplier == SupplierType.ALIEXPRESS:
            return self.aliexpress_details
        elif supplier == SupplierType.CJ_DROPSHIPPING:
            return self.cj_details
        else:
            return {"success": False, "error": "Supplier not supported"}
    
    async def _mock_search_products(self, supplier, query, page=1, limit=20):
        """Mock pour la fonction search_products."""
        if supplier == SupplierType.ALIEXPRESS:
            return {
                "success": True,
                "products": [
                    {
                        "id": "ALI123",
                        "title": f"AliExpress {query}",
                        "price": 19.99,
                        "image_url": "https://example.com/ali_image.jpg"
                    }
                ]
            }
        elif supplier == SupplierType.CJ_DROPSHIPPING:
            return {
                "success": True,
                "products": [
                    {
                        "id": "CJ123",
                        "title": f"CJ {query}",
                        "price": 22.99,
                        "image_url": "https://example.com/cj_image.jpg"
                    }
                ]
            }
        else:
            return {"success": False, "error": "Supplier not supported"}
    
    def test_select_optimal_supplier_aliexpress_better(self):
        """Test de sélection de fournisseur avec AliExpress comme meilleure option."""
        # Modifier les détails pour rendre AliExpress plus attractif
        self.aliexpress_details["price"]["min"] = 15.99
        self.aliexpress_details["variations"][0]["price"] = 18.99
        
        # Mock pour get_product_details
        self.communicator.get_product_details = AsyncMock(side_effect=self._mock_get_product_details)
        
        # Exécution du test
        best_supplier, details = asyncio.run(self.selector.select_optimal_supplier(self.test_product_id, self.test_variant_id))
        
        # Vérifications
        self.assertEqual(best_supplier, SupplierType.ALIEXPRESS)
        self.communicator.get_product_details.assert_any_call(SupplierType.ALIEXPRESS, self.test_product_id)
        self.communicator.get_product_details.assert_any_call(SupplierType.CJ_DROPSHIPPING, self.test_product_id)
    
    def test_select_optimal_supplier_cj_better(self):
        """Test de sélection de fournisseur avec CJ Dropshipping comme meilleure option."""
        # Les données par défaut favorisent déjà CJ (prix légèrement plus élevé mais meilleure 
        # expédition, meilleur stock et meilleure notation vendeur)
        
        # Mock pour get_product_details
        self.communicator.get_product_details = AsyncMock(side_effect=self._mock_get_product_details)
        
        # Exécution du test
        best_supplier, details = asyncio.run(self.selector.select_optimal_supplier(self.test_product_id, self.test_variant_id))
        
        # Vérifications
        self.assertEqual(best_supplier, SupplierType.CJ_DROPSHIPPING)
        self.communicator.get_product_details.assert_any_call(SupplierType.ALIEXPRESS, self.test_product_id)
        self.communicator.get_product_details.assert_any_call(SupplierType.CJ_DROPSHIPPING, self.test_product_id)
    
    def test_select_optimal_supplier_one_unavailable(self):
        """Test de sélection de fournisseur lorsqu'un des fournisseurs n'a pas le produit."""
        # Simuler l'indisponibilité chez AliExpress
        async def mock_get_product_details_one_unavailable(supplier, product_id):
            if supplier == SupplierType.ALIEXPRESS:
                return {"success": False, "error": "Product not found"}
            elif supplier == SupplierType.CJ_DROPSHIPPING:
                return self.cj_details
            else:
                return {"success": False, "error": "Supplier not supported"}
        
        # Mock pour get_product_details
        self.communicator.get_product_details = AsyncMock(side_effect=mock_get_product_details_one_unavailable)
        
        # Exécution du test
        best_supplier, details = asyncio.run(self.selector.select_optimal_supplier(self.test_product_id, self.test_variant_id))
        
        # Vérifications
        self.assertEqual(best_supplier, SupplierType.CJ_DROPSHIPPING)
        self.communicator.get_product_details.assert_any_call(SupplierType.ALIEXPRESS, self.test_product_id)
        self.communicator.get_product_details.assert_any_call(SupplierType.CJ_DROPSHIPPING, self.test_product_id)
    
    def test_select_optimal_supplier_all_unavailable(self):
        """Test de sélection de fournisseur lorsqu'aucun fournisseur n'a le produit."""
        # Simuler l'indisponibilité chez tous les fournisseurs
        async def mock_get_product_details_all_unavailable(supplier, product_id):
            return {"success": False, "error": "Product not found"}
        
        # Mock pour get_product_details
        self.communicator.get_product_details = AsyncMock(side_effect=mock_get_product_details_all_unavailable)
        
        # Exécution du test
        best_supplier, details = asyncio.run(self.selector.select_optimal_supplier(self.test_product_id, self.test_variant_id))
        
        # Vérifications
        self.assertIsNone(best_supplier)
        self.assertIn("error", details)
        self.communicator.get_product_details.assert_any_call(SupplierType.ALIEXPRESS, self.test_product_id)
        self.communicator.get_product_details.assert_any_call(SupplierType.CJ_DROPSHIPPING, self.test_product_id)
    
    def test_find_product_across_suppliers(self):
        """Test de recherche de produits chez tous les fournisseurs."""
        # Mock pour search_products
        self.communicator.search_products = AsyncMock(side_effect=self._mock_search_products)
        
        # Exécution du test
        results = asyncio.run(self.selector.find_product_across_suppliers("test query", limit=5))
        
        # Vérifications
        self.assertEqual(len(results), 2)  # Un résultat de chaque fournisseur
        self.assertTrue(any(product["supplier"] == SupplierType.ALIEXPRESS for product in results))
        self.assertTrue(any(product["supplier"] == SupplierType.CJ_DROPSHIPPING for product in results))
        self.communicator.search_products.assert_any_call(SupplierType.ALIEXPRESS, "test query", page=1, limit=5)
        self.communicator.search_products.assert_any_call(SupplierType.CJ_DROPSHIPPING, "test query", page=1, limit=5)
    
    def test_find_product_one_supplier_error(self):
        """Test de recherche lorsqu'un fournisseur renvoie une erreur."""
        # Simuler une erreur chez AliExpress
        async def mock_search_one_error(supplier, query, page=1, limit=20):
            if supplier == SupplierType.ALIEXPRESS:
                raise Exception("Connection error")
            elif supplier == SupplierType.CJ_DROPSHIPPING:
                return {
                    "success": True,
                    "products": [
                        {
                            "id": "CJ123",
                            "title": f"CJ {query}",
                            "price": 22.99,
                            "image_url": "https://example.com/cj_image.jpg"
                        }
                    ]
                }
            else:
                return {"success": False, "error": "Supplier not supported"}
        
        # Mock pour search_products
        self.communicator.search_products = AsyncMock(side_effect=mock_search_one_error)
        
        # Exécution du test
        results = asyncio.run(self.selector.find_product_across_suppliers("test query", limit=5))
        
        # Vérifications
        self.assertEqual(len(results), 1)  # Seulement le résultat de CJ Dropshipping
        self.assertEqual(results[0]["supplier"], SupplierType.CJ_DROPSHIPPING)
        self.communicator.search_products.assert_any_call(SupplierType.ALIEXPRESS, "test query", page=1, limit=5)
        self.communicator.search_products.assert_any_call(SupplierType.CJ_DROPSHIPPING, "test query", page=1, limit=5)


if __name__ == '__main__':
    unittest.main()
