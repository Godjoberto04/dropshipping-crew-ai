#!/usr/bin/env python3
"""
Tests unitaires pour le client API
"""

import unittest
import sys
import os
import json
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
import httpx
import time

# Ajout du répertoire parent au path pour importer les modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from tools.api_client import ApiClient

class TestApiClient(unittest.TestCase):
    """Tests pour la classe ApiClient"""
    
    def setUp(self):
        """Configuration commune pour tous les tests"""
        self.base_url = "http://api:8000"
        self.agent_id = "content-generator"
        self.api_client = ApiClient(
            base_url=self.base_url,
            agent_id=self.agent_id,
            timeout=5,
            max_retries=2
        )
        
        # Patch pour le client httpx
        self.patcher = patch("httpx.AsyncClient")
        self.mock_client = self.patcher.start()
        
        # Configuration du mock
        self.mock_async_client = AsyncMock()
        self.mock_client.return_value.__aenter__.return_value = self.mock_async_client
        self.mock_client.return_value.__aexit__.return_value = None
        
        # Configurer les réponses par défaut
        self.mock_async_client.get = AsyncMock()
        self.mock_async_client.post = AsyncMock()
        self.mock_async_client.put = AsyncMock()
        
        # Réponse HTTP mock par défaut
        self.default_response = MagicMock()
        self.default_response.raise_for_status = MagicMock()
        self.default_response.json = MagicMock(return_value={"success": True})
        
        # Attribuer la réponse par défaut à toutes les méthodes HTTP
        self.mock_async_client.get.return_value = self.default_response
        self.mock_async_client.post.return_value = self.default_response
        self.mock_async_client.put.return_value = self.default_response
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        self.patcher.stop()
    
    async def test_make_request_get(self):
        """Teste la méthode _make_request avec une requête GET"""
        # Configurer une réponse spécifique
        response_data = {"key": "value"}
        self.default_response.json.return_value = response_data
        
        # Exécuter la méthode à tester
        result = await self.api_client._make_request("GET", "/endpoint", params={"param": "value"})
        
        # Vérifier que la méthode get a été appelée avec les bons arguments
        self.mock_async_client.get.assert_called_once_with(
            f"{self.base_url}/endpoint",
            params={"param": "value"},
            headers={"Content-Type": "application/json"}
        )
        
        # Vérifier que raise_for_status a été appelé
        self.default_response.raise_for_status.assert_called_once()
        
        # Vérifier que le résultat est correct
        self.assertEqual(result, response_data)
    
    async def test_make_request_post(self):
        """Teste la méthode _make_request avec une requête POST"""
        # Configurer une réponse spécifique
        response_data = {"id": "123", "status": "created"}
        self.default_response.json.return_value = response_data
        
        # Données à envoyer
        data = {"name": "Test", "value": 42}
        
        # Exécuter la méthode à tester
        result = await self.api_client._make_request("POST", "/endpoint", data=data)
        
        # Vérifier que la méthode post a été appelée avec les bons arguments
        self.mock_async_client.post.assert_called_once_with(
            f"{self.base_url}/endpoint",
            json=data,
            params=None,
            headers={"Content-Type": "application/json"}
        )
        
        # Vérifier que raise_for_status a été appelé
        self.default_response.raise_for_status.assert_called_once()
        
        # Vérifier que le résultat est correct
        self.assertEqual(result, response_data)
    
    async def test_make_request_put(self):
        """Teste la méthode _make_request avec une requête PUT"""
        # Configurer une réponse spécifique
        response_data = {"id": "123", "status": "updated"}
        self.default_response.json.return_value = response_data
        
        # Données à envoyer
        data = {"status": "completed", "result": {"success": True}}
        
        # Exécuter la méthode à tester
        result = await self.api_client._make_request("PUT", "/endpoint/123", data=data)
        
        # Vérifier que la méthode put a été appelée avec les bons arguments
        self.mock_async_client.put.assert_called_once_with(
            f"{self.base_url}/endpoint/123",
            json=data,
            params=None,
            headers={"Content-Type": "application/json"}
        )
        
        # Vérifier que raise_for_status a été appelé
        self.default_response.raise_for_status.assert_called_once()
        
        # Vérifier que le résultat est correct
        self.assertEqual(result, response_data)
    
    async def test_make_request_invalid_method(self):
        """Teste la méthode _make_request avec une méthode HTTP non supportée"""
        # Vérifier que la méthode lève une exception pour une méthode HTTP non supportée
        with self.assertRaises(ValueError):
            await self.api_client._make_request("DELETE", "/endpoint")
    
    async def test_make_request_json_decode_error(self):
        """Teste la gestion des erreurs de décodage JSON"""
        # Configurer le mock pour simuler une erreur de décodage JSON
        self.default_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        self.default_response.text = "Not a JSON response"
        
        # Exécuter la méthode à tester
        result = await self.api_client._make_request("GET", "/endpoint")
        
        # Vérifier que le résultat est correctement formaté
        self.assertEqual(result, {"success": True, "data": "Not a JSON response"})
    
    async def test_make_request_http_error_retry(self):
        """Teste la gestion des erreurs HTTP avec retry"""
        # Configurer le mock pour simuler une erreur HTTP puis une réussite
        error_response = MagicMock()
        error_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error",
            request=MagicMock(),
            response=MagicMock(status_code=500)
        )
        
        success_response = MagicMock()
        success_response.raise_for_status = MagicMock()
        success_response.json.return_value = {"success": True}
        
        # Premier appel génère une erreur, deuxième appel réussit
        self.mock_async_client.get.side_effect = [error_response, success_response]
        
        # Remplacer asyncio.sleep par un mock pour accélérer le test
        with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
            # Exécuter la méthode à tester
            result = await self.api_client._make_request("GET", "/endpoint")
            
            # Vérifier que sleep a été appelé pour implémenter le retry
            mock_sleep.assert_called_once()
            
            # Vérifier que get a été appelé deux fois (une erreur, une réussite)
            self.assertEqual(self.mock_async_client.get.call_count, 2)
            
            # Vérifier que le résultat est correct (celui de la deuxième tentative)
            self.assertEqual(result, {"success": True})
    
    async def test_register_agent(self):
        """Teste l'enregistrement de l'agent"""
        # Configurer la réponse
        response_data = {"success": True, "agent_id": self.agent_id}
        self.default_response.json.return_value = response_data
        
        # Paramètres d'enregistrement
        status = "online"
        version = "1.0.0"
        capabilities = ["generate_product_description", "optimize_content"]
        
        # Exécuter la méthode à tester
        result = await self.api_client.register_agent(
            status=status,
            version=version,
            capabilities=capabilities
        )
        
        # Vérifier que post a été appelé avec les bons arguments
        self.mock_async_client.post.assert_called_once_with(
            f"{self.base_url}/agents/register",
            json={
                "id": self.agent_id,
                "status": status,
                "version": version,
                "capabilities": capabilities
            },
            params=None,
            headers={"Content-Type": "application/json"}
        )
        
        # Vérifier que le résultat est correct
        self.assertEqual(result, response_data)
    
    async def test_get_pending_tasks(self):
        """Teste la récupération des tâches en attente"""
        # Configurer la réponse
        tasks = [
            {"id": "task-1", "status": "pending", "params": {"action": "generate"}},
            {"id": "task-2", "status": "pending", "params": {"action": "optimize"}}
        ]
        self.default_response.json.return_value = {"tasks": tasks}
        
        # Exécuter la méthode à tester
        result = await self.api_client.get_pending_tasks()
        
        # Vérifier que get a été appelé avec les bons arguments
        self.mock_async_client.get.assert_called_once_with(
            f"{self.base_url}/tasks",
            params={"agent_id": self.agent_id, "status": "pending"},
            headers={"Content-Type": "application/json"}
        )
        
        # Vérifier que le résultat est correct
        self.assertEqual(result, tasks)
    
    async def test_update_task_status(self):
        """Teste la mise à jour du statut d'une tâche"""
        # Configurer la réponse
        response_data = {"success": True, "task_id": "task-123"}
        self.default_response.json.return_value = response_data
        
        # Paramètres de mise à jour
        task_id = "task-123"
        status = "completed"
        progress = 100
        result = {"output": "Description générée avec succès"}
        
        # Exécuter la méthode à tester
        result = await self.api_client.update_task_status(
            task_id=task_id,
            status=status,
            progress=progress,
            result=result
        )
        
        # Vérifier que put a été appelé avec les bons arguments
        self.mock_async_client.put.assert_called_once_with(
            f"{self.base_url}/tasks/{task_id}",
            json={
                "status": status,
                "progress": progress,
                "result": result
            },
            params=None,
            headers={"Content-Type": "application/json"}
        )
        
        # Vérifier que le résultat est correct
        self.assertEqual(result, response_data)
    
    async def test_create_task(self):
        """Teste la création d'une tâche"""
        # Configurer la réponse
        response_data = {"id": "task-456", "status": "pending"}
        self.default_response.json.return_value = response_data
        
        # Paramètres de la tâche
        agent_id = "website-builder"
        params = {
            "action": "update_product",
            "product_id": "123",
            "fields": {"description": "Nouvelle description"}
        }
        
        # Exécuter la méthode à tester
        result = await self.api_client.create_task(
            agent_id=agent_id,
            params=params
        )
        
        # Vérifier que post a été appelé avec les bons arguments
        self.mock_async_client.post.assert_called_once_with(
            f"{self.base_url}/tasks",
            json={
                "agent_id": agent_id,
                "params": params
            },
            params=None,
            headers={"Content-Type": "application/json"}
        )
        
        # Vérifier que le résultat est correct
        self.assertEqual(result, response_data)
    
    async def test_get_task_result(self):
        """Teste la récupération du résultat d'une tâche"""
        # Configurer la réponse
        response_data = {
            "id": "task-123",
            "status": "completed",
            "result": {"output": "Description générée avec succès"}
        }
        self.default_response.json.return_value = response_data
        
        # Exécuter la méthode à tester
        result = await self.api_client.get_task_result("task-123")
        
        # Vérifier que get a été appelé avec les bons arguments
        self.mock_async_client.get.assert_called_once_with(
            f"{self.base_url}/tasks/task-123",
            params=None,
            headers={"Content-Type": "application/json"}
        )
        
        # Vérifier que le résultat est correct
        self.assertEqual(result, response_data)
    
    async def test_wait_for_task_completion_success(self):
        """Teste l'attente de la fin d'une tâche (succès)"""
        # Configurer les réponses pour simuler une tâche en cours puis terminée
        in_progress_response = MagicMock()
        in_progress_response.raise_for_status = MagicMock()
        in_progress_response.json.return_value = {
            "id": "task-123",
            "status": "processing",
            "progress": 50
        }
        
        completed_response = MagicMock()
        completed_response.raise_for_status = MagicMock()
        completed_response.json.return_value = {
            "id": "task-123",
            "status": "completed",
            "result": {"output": "Description générée avec succès"}
        }
        
        # Premier appel retourne en cours, deuxième appel retourne terminé
        self.mock_async_client.get.side_effect = [in_progress_response, completed_response]
        
        # Remplacer asyncio.sleep par un mock pour accélérer le test
        with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
            # Exécuter la méthode à tester avec un temps de polling court
            result = await self.api_client.wait_for_task_completion(
                task_id="task-123",
                polling_interval=0.1,
                timeout=10.0
            )
            
            # Vérifier que sleep a été appelé une fois
            mock_sleep.assert_called_once_with(0.1)
            
            # Vérifier que get a été appelé deux fois
            self.assertEqual(self.mock_async_client.get.call_count, 2)
            
            # Vérifier que le résultat est celui de la tâche terminée
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["result"]["output"], "Description générée avec succès")
    
    async def test_wait_for_task_completion_timeout(self):
        """Teste l'attente de la fin d'une tâche avec timeout"""
        # Configurer la réponse pour simuler une tâche toujours en cours
        in_progress_response = MagicMock()
        in_progress_response.raise_for_status = MagicMock()
        in_progress_response.json.return_value = {
            "id": "task-123",
            "status": "processing",
            "progress": 50
        }
        
        # Toujours retourner en cours
        self.mock_async_client.get.return_value = in_progress_response
        
        # Remplacer asyncio.sleep et time.time par des mocks
        with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
            with patch("time.time") as mock_time:
                # Simuler un dépassement de délai
                mock_time.side_effect = [0, 1, 301]  # Démarrage à 0, puis 1s écoulée, puis 301s écoulées (> timeout)
                
                # Vérifier que la méthode lève un TimeoutError
                with self.assertRaises(TimeoutError):
                    await self.api_client.wait_for_task_completion(
                        task_id="task-123",
                        polling_interval=1.0,
                        timeout=300.0
                    )
                
                # Vérifier que sleep a été appelé une fois
                mock_sleep.assert_called_once_with(1.0)
                
                # Vérifier que get a été appelé une fois
                self.mock_async_client.get.assert_called_once()

# Helper pour exécuter les tests asynchrones
def run_async_test(coro):
    return asyncio.run(coro)

if __name__ == "__main__":
    # Patch pour les méthodes de test asynchrones
    test_methods = [
        'test_make_request_get',
        'test_make_request_post',
        'test_make_request_put',
        'test_make_request_invalid_method',
        'test_make_request_json_decode_error',
        'test_make_request_http_error_retry',
        'test_register_agent',
        'test_get_pending_tasks',
        'test_update_task_status',
        'test_create_task',
        'test_get_task_result',
        'test_wait_for_task_completion_success',
        'test_wait_for_task_completion_timeout'
    ]
    
    for method_name in test_methods:
        original_method = getattr(TestApiClient, method_name)
        setattr(TestApiClient, method_name, 
                lambda self, method=original_method: run_async_test(method(self)))
    
    unittest.main()
