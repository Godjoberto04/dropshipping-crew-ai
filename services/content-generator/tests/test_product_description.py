#!/usr/bin/env python3
"""
Tests unitaires pour le générateur de descriptions produit
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

# Ajout du répertoire parent au path pour importer les modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from generators.product_description import ProductDescriptionGenerator
from tools.claude_client import ClaudeClient

class TestProductDescriptionGenerator(unittest.TestCase):
    """Tests pour la classe ProductDescriptionGenerator"""
    
    def setUp(self):
        """Configuration commune pour tous les tests"""
        # Mock du client Claude
        self.mock_claude_client = MagicMock(spec=ClaudeClient)
        self.mock_claude_client.generate = AsyncMock(return_value="## Description générée\n\nVoici une description de test généré par le mock.")
        
        # Répertoire de templates pour les tests
        self.templates_dir = Path(__file__).resolve().parent / "test_templates"
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Créer un générateur avec des mocks
        self.generator = ProductDescriptionGenerator(
            claude_client=self.mock_claude_client,
            templates_dir=self.templates_dir
        )
        
        # Remplacer la méthode _load_prompt_templates par une version simplifiée pour les tests
        self.generator.prompt_templates = {
            "TEMPLATE_PRODUCT_DESCRIPTION_STANDARD": self.generator._get_default_template(),
            "TEMPLATE_PRODUCT_DESCRIPTION_ELECTRONICS": "Template spécifique pour l'électronique {{product_info}}\nTon: {{tone}}\nLangue: {{language}}\nNiche: {{niche}}"
        }
        
        # Exemple de données produit pour les tests
        self.sample_product = {
            "name": "Écouteurs Bluetooth Premium",
            "price": "89.99",
            "brand": "TechSound",
            "features": ["Autonomie 24h", "Suppression active du bruit", "Résistant à l'eau"],
            "specifications": {
                "connectivité": "Bluetooth 5.2",
                "poids": "45g"
            }
        }
    
    def test_format_product_info(self):
        """Teste le formatage des informations produit"""
        formatted_info = self.generator._format_product_info(self.sample_product)
        
        # Vérifier que les informations essentielles sont présentes
        self.assertIn("Nom du produit: Écouteurs Bluetooth Premium", formatted_info)
        self.assertIn("Prix: 89.99", formatted_info)
        self.assertIn("Marque: TechSound", formatted_info)
        
        # Vérifier que les caractéristiques sont incluses
        self.assertIn("Caractéristiques:", formatted_info)
        self.assertIn("- Autonomie 24h", formatted_info)
        
        # Vérifier que les spécifications sont incluses
        self.assertIn("Spécifications techniques:", formatted_info)
        self.assertIn("- connectivité: Bluetooth 5.2", formatted_info)
    
    def test_prepare_prompt(self):
        """Teste la préparation du prompt"""
        prompt = self.generator._prepare_prompt(
            product_data=self.sample_product,
            tone="persuasif",
            language="fr",
            niche="electronics",
            template_key="TEMPLATE_PRODUCT_DESCRIPTION_ELECTRONICS"
        )
        
        # Vérifier que le template spécifique à l'électronique est utilisé
        self.assertIn("Template spécifique pour l'électronique", prompt)
        
        # Vérifier que les variables sont correctement remplacées
        self.assertIn("Ton: persuasif", prompt)
        self.assertIn("Langue: fr", prompt)
        self.assertIn("Niche: electronics", prompt)
        
        # Vérifier que les informations produit sont incluses
        self.assertIn("Nom du produit: Écouteurs Bluetooth Premium", prompt)
    
    def test_clean_description(self):
        """Teste le nettoyage des descriptions générées"""
        # Description avec divers problèmes de formatage
        dirty_description = "\n\n# Titre principal\n\n\n\nParagraphe 1\n\n\n\nParagraphe 2\n\n• Point 1\n◦ Point 2\n▪ Point 3\n- Point 4"
        
        cleaned = self.generator._clean_description(dirty_description)
        
        # Vérifier que les lignes vides multiples sont réduites
        self.assertNotIn("\n\n\n", cleaned)
        
        # Vérifier que les titres sont standardisés
        self.assertIn("## Titre principal", cleaned)
        
        # Vérifier que les puces sont standardisées
        self.assertIn("* Point 1", cleaned)
        self.assertIn("* Point 2", cleaned)
        self.assertIn("* Point 3", cleaned)
        self.assertIn("* Point 4", cleaned)
    
    def test_get_system_prompt(self):
        """Teste la génération du prompt système"""
        system_prompt = self.generator._get_system_prompt("fr", "electronics")
        
        # Vérifier que le prompt système est cohérent
        self.assertIn("rédacteur de descriptions produit", system_prompt)
        self.assertIn("spécialisé dans la niche electronics", system_prompt)
        self.assertIn("en fr", system_prompt)
    
    async def test_generate(self):
        """Teste la génération complète d'une description"""
        description = await self.generator.generate(
            product_data=self.sample_product,
            tone="persuasif",
            language="fr",
            niche="electronics"
        )
        
        # Vérifier que Claude a été appelé avec les bons paramètres
        self.mock_claude_client.generate.assert_called_once()
        args, kwargs = self.mock_claude_client.generate.call_args
        
        # Vérifier que le prompt contient les informations produit
        self.assertIn("Écouteurs Bluetooth Premium", kwargs["prompt"])
        
        # Vérifier que la description est bien retournée
        self.assertEqual(description, "## Description générée\n\nVoici une description de test généré par le mock.")

# Helper pour exécuter les tests asynchrones
def run_async_test(coro):
    return asyncio.run(coro)

if __name__ == "__main__":
    # Patch pour test_generate
    original_test_generate = TestProductDescriptionGenerator.test_generate
    TestProductDescriptionGenerator.test_generate = lambda self: run_async_test(original_test_generate(self))
    
    unittest.main()