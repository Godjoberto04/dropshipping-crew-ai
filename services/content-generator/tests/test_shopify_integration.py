#!/usr/bin/env python3
"""
Tests unitaires pour l'intégration avec Shopify
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

# Ajout du répertoire parent au path pour importer les modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from integrations.shopify import ShopifyClient
from tools.api_client import ApiClient

class TestShopifyClient(unittest.TestCase):
    """Tests pour la classe ShopifyClient"""
    
    def setUp(self):
        """Configuration commune pour tous les tests"""
        # Mock du client API
        self.mock_api_client = MagicMock(spec=ApiClient)
        self.mock_api_client.create_task = AsyncMock()
        self.mock_api_client.wait_for_task_completion = AsyncMock()
        
        # Créer un client avec le mock
        self.client = ShopifyClient(api_client=self.mock_api_client)
        
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
            "result": {
                "success": True
            }
        }
    
    async def test_update_product_description(self):
        """Teste la mise à jour de la description d'un produit"""
        # Configurer le mock pour retourner un résultat de succès
        self.mock_api_client.wait_for_task_completion.return_value = {
            "id": "task-123",
            "status": "completed",
            "result": {
                "product_id": "prod-123",
                "updated": True
            }
        }
        
        # Données pour le test
        product_id = "prod-123"
        description = "Description mise à jour du produit"
        seo_metadata = {
            "meta_description": "Méta-description optimisée",
            "title": "Titre SEO optimisé",
            "keywords": ["mot-clé1", "mot-clé2"]
        }
        
        # Appeler la méthode à tester
        result = await self.client.update_product_description(
            product_id=product_id,
            description=description,
            seo_metadata=seo_metadata
        )
        
        # Vérifier que create_task a été appelé avec les bons paramètres
        self.mock_api_client.create_task.assert_called_once_with(
            agent_id="website-builder",
            params={
                "action": "update_product",
                "product_id": product_id,
                "fields": {
                    "description": description,
                    "seo_metadata": seo_metadata
                }
            }
        )
        
        # Vérifier que wait_for_task_completion a été appelé
        self.mock_api_client.wait_for_task_completion.assert_called_once_with("task-123")
        
        # Vérifier le résultat
        self.assertTrue(result["success"])
        self.assertEqual(result["result"]["product_id"], "prod-123")
    
    async def test_create_product(self):
        """Teste la création d'un nouveau produit"""
        # Configurer le mock pour retourner un résultat de succès
        self.mock_api_client.wait_for_task_completion.return_value = {
            "id": "task-123",
            "status": "completed",
            "result": {
                "product_id": "new-prod-456",
                "created": True
            }
        }
        
        # Données pour le test
        product_data = {
            "title": "Écouteurs Bluetooth Premium",
            "price": 89.99,
            "variants": [
                {"title": "Noir", "price": 89.99},
                {"title": "Blanc", "price": 89.99}
            ],
            "images": ["https://example.com/image1.jpg"]
        }
        description = "Une description détaillée du produit..."
        seo_metadata = {
            "meta_description": "Écouteurs sans fil avec suppression active du bruit et autonomie de 24h.",
            "title": "Écouteurs Bluetooth Premium - Suppression de bruit et longue autonomie",
            "keywords": ["écouteurs bluetooth", "suppression de bruit", "autonomie"]
        }
        
        # Appeler la méthode à tester
        result = await self.client.create_product(
            product_data=product_data,
            description=description,
            seo_metadata=seo_metadata
        )
        
        # Vérifier que create_task a été appelé avec les bons paramètres
        expected_product_data = product_data.copy()
        expected_product_data["description"] = description
        expected_product_data["seo_metadata"] = seo_metadata
        
        self.mock_api_client.create_task.assert_called_once_with(
            agent_id="website-builder",
            params={
                "action": "add_product",
                "product_data": expected_product_data
            }
        )
        
        # Vérifier que wait_for_task_completion a été appelé
        self.mock_api_client.wait_for_task_completion.assert_called_once_with("task-123")
        
        # Vérifier le résultat
        self.assertTrue(result["success"])
        self.assertEqual(result["result"]["product_id"], "new-prod-456")
    
    async def test_update_category_description(self):
        """Teste la mise à jour de la description d'une catégorie"""
        # Configurer le mock pour retourner un résultat de succès
        self.mock_api_client.wait_for_task_completion.return_value = {
            "id": "task-123",
            "status": "completed",
            "result": {
                "collection_id": "coll-123",
                "updated": True
            }
        }
        
        # Données pour le test
        category_id = "coll-123"
        description = "Description de la catégorie mise à jour"
        seo_metadata = {
            "meta_description": "Catégorie regroupant nos meilleurs produits audio",
            "title": "Audio Premium - Collection exclusive",
            "keywords": ["audio premium", "écouteurs", "casques"]
        }
        
        # Appeler la méthode à tester
        result = await self.client.update_category_description(
            category_id=category_id,
            description=description,
            seo_metadata=seo_metadata
        )
        
        # Vérifier que create_task a été appelé avec les bons paramètres
        self.mock_api_client.create_task.assert_called_once_with(
            agent_id="website-builder",
            params={
                "action": "update_collection",
                "collection_id": category_id,
                "fields": {
                    "description": description,
                    "seo_metadata": seo_metadata
                }
            }
        )
        
        # Vérifier que wait_for_task_completion a été appelé
        self.mock_api_client.wait_for_task_completion.assert_called_once_with("task-123")
        
        # Vérifier le résultat
        self.assertTrue(result["success"])
        self.assertEqual(result["result"]["collection_id"], "coll-123")
    
    async def test_create_blog_post(self):
        """Teste la création d'un article de blog"""
        # Configurer le mock pour retourner un résultat de succès
        self.mock_api_client.wait_for_task_completion.return_value = {
            "id": "task-123",
            "status": "completed",
            "result": {
                "post_id": "blog-123",
                "created": True,
                "url": "https://example.com/blog/post-title"
            }
        }
        
        # Données pour le test
        title = "Guide complet sur les écouteurs sans fil en 2025"
        content = "Contenu détaillé de l'article..."
        seo_metadata = {
            "meta_description": "Tout ce que vous devez savoir sur les écouteurs sans fil en 2025",
            "keywords": ["guide écouteurs", "technologies audio", "comparatif écouteurs"]
        }
        tags = ["écouteurs", "audio", "guide"]
        
        # Appeler la méthode à tester
        result = await self.client.create_blog_post(
            title=title,
            content=content,
            seo_metadata=seo_metadata,
            tags=tags,
            publish=True
        )
        
        # Vérifier que create_task a été appelé avec les bons paramètres
        self.mock_api_client.create_task.assert_called_once_with(
            agent_id="website-builder",
            params={
                "action": "create_blog_post",
                "post_data": {
                    "title": title,
                    "content": content,
                    "seo_metadata": seo_metadata,
                    "tags": tags,
                    "publish": True
                }
            }
        )
        
        # Vérifier que wait_for_task_completion a été appelé
        self.mock_api_client.wait_for_task_completion.assert_called_once_with("task-123")
        
        # Vérifier le résultat
        self.assertTrue(result["success"])
        self.assertEqual(result["result"]["post_id"], "blog-123")
    
    async def test_update_page_content(self):
        """Teste la mise à jour du contenu d'une page statique"""
        # Configurer le mock pour retourner un résultat de succès
        self.mock_api_client.wait_for_task_completion.return_value = {
            "id": "task-123",
            "status": "completed",
            "result": {
                "page_id": "page-123",
                "updated": True
            }
        }
        
        # Données pour le test
        page_id = "page-123"
        content = "Nouveau contenu de la page à propos..."
        seo_metadata = {
            "meta_description": "À propos de notre boutique spécialisée en audio premium",
            "title": "À propos - Notre histoire et nos valeurs",
            "keywords": ["à propos", "histoire", "valeurs"]
        }
        
        # Appeler la méthode à tester
        result = await self.client.update_page_content(
            page_id=page_id,
            content=content,
            seo_metadata=seo_metadata
        )
        
        # Vérifier que create_task a été appelé avec les bons paramètres
        self.mock_api_client.create_task.assert_called_once_with(
            agent_id="website-builder",
            params={
                "action": "update_page",
                "page_id": page_id,
                "fields": {
                    "content": content,
                    "seo_metadata": seo_metadata
                }
            }
        )
        
        # Vérifier que wait_for_task_completion a été appelé
        self.mock_api_client.wait_for_task_completion.assert_called_once_with("task-123")
        
        # Vérifier le résultat
        self.assertTrue(result["success"])
        self.assertEqual(result["result"]["page_id"], "page-123")
    
    async def test_handle_task_failure(self):
        """Teste la gestion d'une tâche échouée"""
        # Configurer le mock pour simuler un échec
        self.mock_api_client.wait_for_task_completion.return_value = {
            "id": "task-123",
            "status": "failed",
            "result": {
                "error": "Échec de la mise à jour - produit non trouvé"
            }
        }
        
        # Appeler la méthode à tester
        result = await self.client.update_product_description(
            product_id="invalid-id",
            description="Description test"
        )
        
        # Vérifier que create_task a été appelé
        self.mock_api_client.create_task.assert_called_once()
        
        # Vérifier que wait_for_task_completion a été appelé
        self.mock_api_client.wait_for_task_completion.assert_called_once()
        
        # Vérifier que le résultat indique un échec
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Échec de la mise à jour - produit non trouvé")
    
    async def test_handle_exception(self):
        """Teste la gestion des exceptions"""
        # Configurer le mock pour lever une exception
        self.mock_api_client.create_task.side_effect = Exception("Erreur de connexion")
        
        # Appeler la méthode à tester
        result = await self.client.create_blog_post(
            title="Test",
            content="Contenu test"
        )
        
        # Vérifier que le résultat indique un échec
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Erreur de connexion")

# Helper pour exécuter les tests asynchrones
def run_async_test(coro):
    return asyncio.run(coro)

if __name__ == "__main__":
    # Patch pour les méthodes de test asynchrones
    test_methods = [
        'test_update_product_description',
        'test_create_product',
        'test_update_category_description',
        'test_create_blog_post',
        'test_update_page_content',
        'test_handle_task_failure',
        'test_handle_exception'
    ]
    
    for method_name in test_methods:
        original_method = getattr(TestShopifyClient, method_name)
        setattr(TestShopifyClient, method_name, 
                lambda self, method=original_method: run_async_test(method(self)))
    
    unittest.main()
