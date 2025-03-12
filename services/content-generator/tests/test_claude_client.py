#!/usr/bin/env python3
"""
Tests unitaires pour le client Claude
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

from tools.claude_client import ClaudeClient

class TestClaudeClient(unittest.TestCase):
    """Tests pour la classe ClaudeClient"""
    
    def setUp(self):
        """Configuration commune pour tous les tests"""
        # Créer un client avec une clé API fictive
        self.claude_client = ClaudeClient(
            api_key="fake_api_key_for_testing",
            model="claude-3-haiku-20240307",
        )
    
    @patch("aiohttp.ClientSession.post")
    async def test_generate(self, mock_post):
        """Teste la génération de texte"""
        # Configuration du mock pour simuler une réponse de l'API Claude
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "id": "msg_01234567890abcdef",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "Voici la réponse générée par Claude."}],
            "model": "claude-3-haiku-20240307",
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": 50,
                "output_tokens": 10
            }
        })
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Appel de la méthode à tester
        result = await self.claude_client.generate(
            prompt="Génère une description pour des écouteurs Bluetooth.",
            system_prompt="Tu es un rédacteur de descriptions produit.",
            temperature=0.7,
            max_tokens=1000
        )
        
        # Vérifications
        self.assertEqual(result, "Voici la réponse générée par Claude.")
        
        # Vérifier que l'API a été appelée avec les bons paramètres
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        
        self.assertEqual(args[0], "https://api.anthropic.com/v1/messages")
        self.assertEqual(kwargs["headers"]["x-api-key"], "fake_api_key_for_testing")
        self.assertEqual(kwargs["headers"]["anthropic-version"], "2023-06-01")
        
        # Vérifier le contenu du corps de la requête
        request_body = json.loads(kwargs["json"])
        self.assertEqual(request_body["model"], "claude-3-haiku-20240307")
        self.assertEqual(request_body["temperature"], 0.7)
        self.assertEqual(request_body["max_tokens"], 1000)
        self.assertEqual(request_body["system"], "Tu es un rédacteur de descriptions produit.")
        
        messages = request_body["messages"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[0]["content"], "Génère une description pour des écouteurs Bluetooth.")
    
    @patch("aiohttp.ClientSession.post")
    async def test_generate_error_handling(self, mock_post):
        """Teste la gestion des erreurs lors de la génération"""
        # Configurer le mock pour simuler une erreur API
        mock_response = MagicMock()
        mock_response.status = 400
        mock_response.json = AsyncMock(return_value={
            "error": {
                "type": "invalid_request_error",
                "message": "Invalid API key provided."
            }
        })
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Vérifier que l'exception appropriée est levée
        with self.assertRaises(Exception) as context:
            await self.claude_client.generate(
                prompt="Test d'erreur.",
                system_prompt="Système test."
            )
        
        # Vérifier le message d'erreur
        self.assertIn("Erreur lors de l'appel à l'API Claude", str(context.exception))
    
    @patch("aiohttp.ClientSession.post")
    async def test_rate_limit_handling(self, mock_post):
        """Teste la gestion des limites de taux"""
        # Configurer le mock pour simuler une erreur de limite de taux
        mock_response = MagicMock()
        mock_response.status = 429
        mock_response.json = AsyncMock(return_value={
            "error": {
                "type": "rate_limit_error",
                "message": "Rate limit exceeded. Please try again later."
            }
        })
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Vérifier que l'exception appropriée est levée
        with self.assertRaises(Exception) as context:
            await self.claude_client.generate(
                prompt="Test de limite de taux.",
                system_prompt="Système test."
            )
        
        # Vérifier le message d'erreur
        self.assertIn("Limite de taux dépassée", str(context.exception))

# Helper pour exécuter les tests asynchrones
def run_async_test(coro):
    return asyncio.run(coro)

if __name__ == "__main__":
    # Patch pour les méthodes de test asynchrones
    for test_method in ['test_generate', 'test_generate_error_handling', 'test_rate_limit_handling']:
        original = getattr(TestClaudeClient, test_method)
        setattr(TestClaudeClient, test_method, lambda self, method=original: run_async_test(method(self)))
    
    unittest.main()