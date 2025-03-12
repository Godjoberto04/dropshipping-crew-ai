#!/usr/bin/env python3
"""
Tests unitaires pour l'intégration avec Data Analyzer
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

# Ajout du répertoire parent au path pour importer les modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from integrations.data_analyzer import DataAnalyzerClient
from tools.api_client import ApiClient

class TestDataAnalyzerClient(unittest.TestCase):
    """Tests pour la classe DataAnalyzerClient"""
    
    def setUp(self):
        """Configuration commune pour tous les tests"""
        # Mock du client API
        self.mock_api_client = MagicMock(spec=ApiClient)
        self.mock_api_client.create_task = AsyncMock()
        self.mock_api_client.wait_for_task_completion = AsyncMock()
        
        # Créer un client avec le mock
        self.client = DataAnalyzerClient(api_client=self.mock_api_client)
        
        # Configurer les retours des mocks pour les tests
        self.setup_mock_responses()
    
    def setup_mock_responses(self):
        """Configure les réponses par défaut pour les mocks"""
        # Réponse pour la création de tâche
        self.mock_api_client.create_task.return_value = {
            "id": "task-123",
            "status": "pending"
        }
        
        # Réponse par défaut pour l'attente de complétion
        self.mock_api_client.wait_for_task_completion.return_value = {
            "id": "task-123",
            "status": "completed",
            "result": {}
        }
    
    async def test_get_product_details(self):
        """Teste la récupération des détails d'un produit"""
        # Configurer le mock pour retourner des détails de produit
        product_details = {
            "name": "Écouteurs Bluetooth Premium",
            "price": 89.99,
            "features": ["Autonomie 24h", "Suppression active du bruit"],
            "market_analysis": {
                "competition_level": "medium",
                "trend": "rising",
                "demand_score": 78
            }
        }
        
        self.mock_api_client.wait_for_task_completion.return_value = {
            "id": "task-123",
            "status": "completed",
            "result": {
                "product_details": product_details
            }
        }
        
        # Appeler la méthode à tester
        result = await self.client.get_product_details("prod-123")
        
        # Vérifier que create_task a été appelé avec les bons paramètres
        self.mock_api_client.create_task.assert_called_once_with(
            agent_id="data-analyzer",
            params={
                "action": "get_product_details",
                "product_id": "prod-123"
            }
        )
        
        # Vérifier que wait_for_task_completion a été appelé
        self.mock_api_client.wait_for_task_completion.assert_called_once_with("task-123")
        
        # Vérifier le résultat
        self.assertEqual(result, product_details)
    
    async def test_get_market_analysis(self):
        """Teste la récupération d'une analyse de marché"""
        # Configurer le mock pour retourner une analyse de marché
        market_analysis = {
            "niche": "electronics",
            "overall_score": 85,
            "growth_potential": "high",
            "top_products": [
                {"name": "Écouteurs Bluetooth", "score": 92},
                {"name": "Chargeur sans fil", "score": 87}
            ],
            "keywords": ["écouteurs sans fil", "suppression de bruit", "bluetooth 5.0"]
        }
        
        self.mock_api_client.wait_for_task_completion.return_value = {
            "id": "task-123",
            "status": "completed",
            "result": {
                "market_analysis": market_analysis
            }
        }
        
        # Appeler la méthode à tester
        result = await self.client.get_market_analysis("electronics")
        
        # Vérifier que create_task a été appelé avec les bons paramètres
        self.mock_api_client.create_task.assert_called_once_with(
            agent_id="data-analyzer",
            params={
                "action": "analyze_market",
                "niche": "electronics"
            }
        )
        
        # Vérifier que wait_for_task_completion a été appelé
        self.mock_api_client.wait_for_task_completion.assert_called_once_with("task-123")
        
        # Vérifier le résultat
        self.assertEqual(result, market_analysis)
    
    async def test_get_keywords_suggestions(self):
        """Teste la récupération de suggestions de mots-clés"""
        # Configurer le mock pour retourner des suggestions de mots-clés
        keywords = [
            "écouteurs bluetooth premium",
            "casque sans fil haute qualité",
            "écouteurs suppression bruit active",
            "écouteurs longue autonomie",
            "casque bluetooth étanche"
        ]
        
        self.mock_api_client.wait_for_task_completion.return_value = {
            "id": "task-123",
            "status": "completed",
            "result": {
                "keywords": keywords
            }
        }
        
        # Appeler la méthode à tester
        result = await self.client.get_keywords_suggestions(
            product_name="Écouteurs Bluetooth Premium",
            niche="electronics",
            count=5
        )
        
        # Vérifier que create_task a été appelé avec les bons paramètres
        self.mock_api_client.create_task.assert_called_once_with(
            agent_id="data-analyzer",
            params={
                "action": "suggest_keywords",
                "product_name": "Écouteurs Bluetooth Premium",
                "niche": "electronics",
                "count": 5
            }
        )
        
        # Vérifier que wait_for_task_completion a été appelé
        self.mock_api_client.wait_for_task_completion.assert_called_once_with("task-123")
        
        # Vérifier le résultat
        self.assertEqual(result, keywords)
    
    async def test_handle_task_failure(self):
        """Teste la gestion d'une tâche échouée"""
        # Configurer le mock pour simuler un échec
        self.mock_api_client.wait_for_task_completion.return_value = {
            "id": "task-123",
            "status": "failed",
            "result": {
                "error": "Erreur de connexion à l'API externe"
            }
        }
        
        # Appeler la méthode à tester
        result = await self.client.get_market_analysis("electronics")
        
        # Vérifier que create_task a été appelé
        self.mock_api_client.create_task.assert_called_once()
        
        # Vérifier que wait_for_task_completion a été appelé
        self.mock_api_client.wait_for_task_completion.assert_called_once()
        
        # Vérifier que le résultat est vide en cas d'échec
        self.assertEqual(result, {})
    
    async def test_handle_exception(self):
        """Teste la gestion des exceptions"""
        # Configurer le mock pour lever une exception
        self.mock_api_client.create_task.side_effect = Exception("Erreur de connexion")
        
        # Appeler la méthode à tester
        result = await self.client.get_keywords_suggestions(
            product_name="Produit test",
            niche="test"
        )
        
        # Vérifier que le résultat est une liste vide en cas d'exception
        self.assertEqual(result, [])

# Helper pour exécuter les tests asynchrones
def run_async_test(coro):
    return asyncio.run(coro)

if __name__ == "__main__":
    # Patch pour les méthodes de test asynchrones
    test_methods = [
        'test_get_product_details',
        'test_get_market_analysis',
        'test_get_keywords_suggestions',
        'test_handle_task_failure',
        'test_handle_exception'
    ]
    
    for method_name in test_methods:
        original_method = getattr(TestDataAnalyzerClient, method_name)
        setattr(TestDataAnalyzerClient, method_name, 
                lambda self, method=original_method: run_async_test(method(self)))
    
    unittest.main()
