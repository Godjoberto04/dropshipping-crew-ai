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
