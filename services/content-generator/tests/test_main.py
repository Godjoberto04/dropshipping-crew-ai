#!/usr/bin/env python3
"""
Tests d'intégration pour l'agent Content Generator
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import json

# Ajout du répertoire parent au path pour importer les modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from main import ContentGeneratorAgent
from tools.api_client import ApiClient
from tools.claude_client import ClaudeClient
from generators.product_description import ProductDescriptionGenerator
from optimizers.seo_optimizer import SEOOptimizer
from integrations.data_analyzer import DataAnalyzerClient
from integrations.shopify import ShopifyClient

class TestContentGeneratorAgent(unittest.TestCase):
    """Tests d'intégration pour la classe ContentGeneratorAgent"""
    
    def setUp(self):
        """Configuration commune pour tous les tests"""
        # Patch la configuration
        self.config_patcher = patch('main.settings')
        self.mock_settings = self.config_patcher.start()
        self.mock_settings.AGENT_ID = "content-generator-test"
        self.mock_settings.AGENT_VERSION = "0.1.0-test"
        self.mock_settings.API_BASE_URL = "http://api-test:8000"
        self.mock_settings.CLAUDE_API_KEY = "fake-key-for-testing"
        self.mock_settings.CLAUDE_MODEL = "claude-3-haiku-20240307"
        self.mock_settings.TEMPLATES_DIR = Path(__file__).resolve().parent / "test_templates"
        os.makedirs(self.mock_settings.TEMPLATES_DIR, exist_ok=True)
        
        # Patch les dépendances externes
        self.api_client_patcher = patch('main.ApiClient')
        self.mock_api_client_class = self.api_client_patcher.start()
        self.mock_api_client = MagicMock(spec=ApiClient)
        self.mock_api_client.register_agent = AsyncMock()
        self.mock_api_client.update_task_status = AsyncMock()
        self.mock_api_client.get_pending_tasks = AsyncMock(return_value=[])
        self.mock_api_client_class.return_value = self.mock_api_client
        
        self.claude_client_patcher = patch('main.ClaudeClient')
        self.mock_claude_client_class = self.claude_client_patcher.start()
        self.mock_claude_client = MagicMock(spec=ClaudeClient)
        self.mock_claude_client.generate = AsyncMock(return_value="Description générée de test.")
        self.mock_claude_client_class.return_value = self.mock_claude_client
        
        # Patch les intégrations
        self.data_analyzer_patcher = patch('main.DataAnalyzerClient')
        self.mock_data_analyzer_class = self.data_analyzer_patcher.start()
        self.mock_data_analyzer = MagicMock(spec=DataAnalyzerClient)
        self.mock_data_analyzer.get_product_details = AsyncMock(return_value={})
        self.mock_data_analyzer_class.return_value = self.mock_data_analyzer
        
        self.shopify_patcher = patch('main.ShopifyClient')
        self.mock_shopify_class = self.shopify_patcher.start()
        self.mock_shopify = MagicMock(spec=ShopifyClient)
        self.mock_shopify.update_product_description = AsyncMock()
        self.mock_shopify_class.return_value = self.mock_shopify
        
        # Créer l'agent à tester
        self.agent = ContentGeneratorAgent()
    
    def tearDown(self):
        """Nettoyer après chaque test"""
        self.config_patcher.stop()
        self.api_client_patcher.stop()
        self.claude_client_patcher.stop()
        self.data_analyzer_patcher.stop()
        self.shopify_patcher.stop()
    
    async def test_register_agent(self):
        """Teste l'enregistrement de l'agent"""
        await self.agent.register_agent()
        
        # Vérifier que l'API a été appelée correctement
        self.mock_api_client.register_agent.assert_called_once_with(
            status="online",
            version="0.1.0-test",
            capabilities=["generate_product_description", "optimize_seo_content"]
        )
    
    async def test_process_task_product_description(self):
        """Teste le traitement d'une tâche de génération de description produit"""
        # Créer une tâche de test
        task = {
            "id": "test-task-123",
            "params": {
                "action": "generate_product_description",
                "product_data": {
                    "name": "Écouteurs Bluetooth Premium",
                    "features": ["Autonomie 24h", "Suppression active du bruit"],
                    "price": "89.99",
                    "brand": "TechSound"
                },
                "tone": "persuasif",
                "niche": "electronics",
                "language": "fr",
                "seo_optimize": True
            }
        }
        
        # Exécuter la méthode à tester
        result = await self.agent.process_task(task)
        
        # Vérifier les appels aux dépendances
        self.mock_api_client.update_task_status.assert_any_call("test-task-123", "processing", progress=10)
        self.mock_api_client.update_task_status.assert_any_call("test-task-123", "processing", progress=30)
        self.mock_api_client.update_task_status.assert_any_call("test-task-123", "processing", progress=60)
        self.mock_api_client.update_task_status.assert_any_call("test-task-123", "processing", progress=90)
        
        # Vérifier le résultat
        self.assertIn("description", result)
        self.assertIn("seo_metadata", result)
        self.assertEqual(result["description"], "Description générée de test.")
    
    async def test_process_task_optimize_content(self):
        """Teste le traitement d'une tâche d'optimisation de contenu"""
        # Créer une tâche de test
        task = {
            "id": "test-task-456",
            "params": {
                "action": "optimize_content",
                "content": "Contenu original à optimiser.",
                "content_type": "product_description",
                "keywords": ["mot-clé 1", "mot-clé 2"]
            }
        }
        
        # Patch la méthode optimize de SEOOptimizer pour contrôler le résultat
        with patch.object(SEOOptimizer, 'optimize', return_value="Contenu optimisé SEO."):
            with patch.object(SEOOptimizer, 'generate_meta_description', return_value="Meta description de test."):
                with patch.object(SEOOptimizer, 'calculate_improvement_score', return_value=85.0):
                    # Exécuter la méthode à tester
                    result = await self.agent.process_task(task)
        
        # Vérifier les appels aux dépendances
        self.mock_api_client.update_task_status.assert_any_call("test-task-456", "processing", progress=10)
        self.mock_api_client.update_task_status.assert_any_call("test-task-456", "processing", progress=40)
        self.mock_api_client.update_task_status.assert_any_call("test-task-456", "processing", progress=90)
        
        # Vérifier le résultat
        self.assertIn("optimized_content", result)
        self.assertIn("seo_metadata", result)
        self.assertIn("improvement_score", result)
        self.assertEqual(result["optimized_content"], "Contenu optimisé SEO.")
        self.assertEqual(result["improvement_score"], 85.0)
    
    async def test_process_task_with_auto_publish(self):
        """Teste une tâche avec publication automatique"""
        # Créer une tâche de test avec auto_publish=True
        task = {
            "id": "test-task-789",
            "params": {
                "action": "generate_product_description",
                "product_data": {
                    "product_id": "prod-123",
                    "name": "Produit test"
                },
                "tone": "informatif",
                "language": "fr",
                "auto_publish": True
            }
        }
        
        # Exécuter la méthode à tester
        result = await self.agent.process_task(task)
        
        # Vérifier l'appel à Shopify pour publication
        self.mock_shopify.update_product_description.assert_called_once()
        call_args = self.mock_shopify.update_product_description.call_args[1]
        self.assertEqual(call_args["product_id"], "prod-123")
        self.assertEqual(call_args["description"], "Description générée de test.")
        
        # Vérifier le résultat
        self.assertIn("published", result)
        self.assertTrue(result["published"])
    
    async def test_process_task_error_handling(self):
        """Teste la gestion des erreurs lors du traitement d'une tâche"""
        # Créer une tâche de test
        task = {
            "id": "test-task-error",
            "params": {
                "action": "action_invalide"
            }
        }
        
        # Exécuter la méthode à tester et vérifier l'exception
        with self.assertRaises(ValueError):
            await self.agent.process_task(task)
        
        # Vérifier que l'erreur est signalée à l'API
        self.mock_api_client.update_task_status.assert_any_call(
            "test-task-error", 
            "failed", 
            result={"error": "Action non reconnue: action_invalide"}
        )
    
    async def test_poll_tasks(self):
        """Teste la boucle principale de vérification des tâches"""
        # Configurer le mock pour simuler une tâche, puis pas de tâche
        task = {
            "id": "test-task-poll",
            "params": {
                "action": "generate_product_description",
                "product_data": {"name": "Produit test"}
            }
        }
        self.mock_api_client.get_pending_tasks.side_effect = [
            [task],  # Premier appel: retourne une tâche
            Exception("Erreur simulée"),  # Deuxième appel: lancement d'une exception
            []  # Troisième appel: aucune tâche
        ]
        
        # Patch asyncio.sleep pour accélérer le test
        with patch('asyncio.sleep', new=AsyncMock()):
            # Créer une tâche pour exécuter poll_tasks pendant un court moment
            poll_task = asyncio.create_task(self.agent.poll_tasks())
            
            # Attendre un peu pour laisser le temps d'exécuter quelques itérations
            await asyncio.sleep(0.1)
            
            # Annuler la tâche pour ne pas bloquer indéfiniment
            poll_task.cancel()
            
            try:
                await poll_task
            except asyncio.CancelledError:
                pass
        
        # Vérifier que get_pending_tasks a été appelé au moins une fois
        self.mock_api_client.get_pending_tasks.assert_called()
        
        # Vérifier que process_task a été appelé pour la tâche
        # Nous pouvons vérifier indirectement en examinant les appels à update_task_status
        self.mock_api_client.update_task_status.assert_any_call("test-task-poll", "processing", progress=10)

# Helper pour exécuter les tests asynchrones
def run_async_test(coro):
    return asyncio.run(coro)

if __name__ == "__main__":
    # Patch pour les méthodes de test asynchrones
    for test_method in [
        'test_register_agent',
        'test_process_task_product_description',
        'test_process_task_optimize_content',
        'test_process_task_with_auto_publish',
        'test_process_task_error_handling',
        'test_poll_tasks'
    ]:
        original = getattr(TestContentGeneratorAgent, test_method)
        setattr(TestContentGeneratorAgent, test_method, 
                lambda self, method=original: run_async_test(method(self)))
    
    unittest.main()