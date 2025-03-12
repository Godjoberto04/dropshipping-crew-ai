#!/usr/bin/env python3
"""
Tests unitaires pour les templates de descriptions produit
"""

import unittest
import sys
import os
from pathlib import Path
import re

# Ajout du répertoire parent au path pour importer les modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from templates.product_templates import (
    TEMPLATE_PRODUCT_DESCRIPTION_STANDARD,
    TEMPLATE_PRODUCT_DESCRIPTION_FASHION,
    TEMPLATE_PRODUCT_DESCRIPTION_ELECTRONICS,
    TEMPLATE_PRODUCT_DESCRIPTION_HOME,
    TEMPLATE_PRODUCT_DESCRIPTION_BEAUTY
)

class TestProductTemplates(unittest.TestCase):
    """Tests pour les templates de descriptions produit"""
    
    def setUp(self):
        """Configuration commune pour tous les tests"""
        # Variables de remplacement communes pour les tests
        self.replacement_vars = {
            "{{product_info}}": "Nom du produit: Écouteurs Bluetooth Premium\nPrix: 89.99\nMarque: TechSound\nCaractéristiques:\n- Autonomie 24h\n- Suppression active du bruit\n- Résistant à l'eau\nSpécifications techniques:\n- connectivité: Bluetooth 5.2\n- poids: 45g",
            "{{tone}}": "persuasif",
            "{{language}}": "fr",
            "{{niche}}": "electronics"
        }
    
    def test_templates_have_placeholders(self):
        """Teste que chaque template contient les placeholders requis"""
        required_placeholders = [
            "{{product_info}}",
            "{{tone}}",
            "{{language}}",
            "{{niche}}"
        ]
        
        templates = [
            TEMPLATE_PRODUCT_DESCRIPTION_STANDARD,
            TEMPLATE_PRODUCT_DESCRIPTION_FASHION,
            TEMPLATE_PRODUCT_DESCRIPTION_ELECTRONICS,
            TEMPLATE_PRODUCT_DESCRIPTION_HOME,
            TEMPLATE_PRODUCT_DESCRIPTION_BEAUTY
        ]
        
        for template in templates:
            for placeholder in required_placeholders:
                self.assertIn(placeholder, template, 
                              f"Le placeholder {placeholder} est manquant dans un template")
    
    def test_standard_template_structure(self):
        """Vérifie la structure du template standard"""
        # Vérifier que le template contient les sections attendues
        sections = ["# Informations sur le produit", "# Ton et style", "# Instructions", "# Format de la réponse"]
        
        for section in sections:
            self.assertIn(section, TEMPLATE_PRODUCT_DESCRIPTION_STANDARD)
        
        # Vérifier que les instructions contiennent des étapes numérotées
        self.assertRegex(TEMPLATE_PRODUCT_DESCRIPTION_STANDARD, r"1\.\s+Commence")
        
        # Vérifier qu'il contient des indications de format Markdown
        self.assertIn("Markdown", TEMPLATE_PRODUCT_DESCRIPTION_STANDARD)
    
    def test_fashion_template_specificity(self):
        """Vérifie que le template mode contient des éléments spécifiques à cette niche"""
        fashion_specific_terms = [
            "mode", "vêtement", "accessoir", "porté", "style"
        ]
        
        # Au moins 3 des termes spécifiques doivent être présents
        count = sum(1 for term in fashion_specific_terms if term.lower() in TEMPLATE_PRODUCT_DESCRIPTION_FASHION.lower())
        self.assertGreaterEqual(count, 3)
        
        # Vérifier que le template mentionne explicitement la niche mode
        self.assertIn("Mode et accessoires", TEMPLATE_PRODUCT_DESCRIPTION_FASHION)
    
    def test_electronics_template_specificity(self):
        """Vérifie que le template électronique contient des éléments spécifiques à cette niche"""
        electronics_specific_terms = [
            "technique", "spécification", "innovation", "performance", "technologie", "compatibilité"
        ]
        
        # Au moins 3 des termes spécifiques doivent être présents
        count = sum(1 for term in electronics_specific_terms if term.lower() in TEMPLATE_PRODUCT_DESCRIPTION_ELECTRONICS.lower())
        self.assertGreaterEqual(count, 3)
        
        # Vérifier que le template mentionne explicitement la niche électronique
        self.assertIn("Électronique et technologie", TEMPLATE_PRODUCT_DESCRIPTION_ELECTRONICS)
    
    def test_home_template_specificity(self):
        """Vérifie que le template maison contient des éléments spécifiques à cette niche"""
        home_specific_terms = [
            "décoration", "intérieur", "espace", "ambiance", "design"
        ]
        
        # Au moins 3 des termes spécifiques doivent être présents
        count = sum(1 for term in home_specific_terms if term.lower() in TEMPLATE_PRODUCT_DESCRIPTION_HOME.lower())
        self.assertGreaterEqual(count, 3)
        
        # Vérifier que le template mentionne explicitement la niche maison
        self.assertIn("Maison et décoration", TEMPLATE_PRODUCT_DESCRIPTION_HOME)
    
    def test_beauty_template_specificity(self):
        """Vérifie que le template beauté contient des éléments spécifiques à cette niche"""
        beauty_specific_terms = [
            "beauté", "cosmétique", "ingrédient", "peau", "cheveux", "sensoriel"
        ]
        
        # Au moins 3 des termes spécifiques doivent être présents
        count = sum(1 for term in beauty_specific_terms if term.lower() in TEMPLATE_PRODUCT_DESCRIPTION_BEAUTY.lower())
        self.assertGreaterEqual(count, 3)
        
        # Vérifier que le template mentionne explicitement la niche beauté
        self.assertIn("Beauté et cosmétiques", TEMPLATE_PRODUCT_DESCRIPTION_BEAUTY)
    
    def test_template_variables_replacement(self):
        """Teste le remplacement des variables de template"""
        # Fonction pour remplacer les variables dans un template
        def replace_vars(template, vars_dict):
            result = template
            for var, value in vars_dict.items():
                result = result.replace(var, value)
            return result
        
        # Appliquer le remplacement sur le template standard
        filled_template = replace_vars(TEMPLATE_PRODUCT_DESCRIPTION_STANDARD, self.replacement_vars)
        
        # Vérifier que les variables ont été remplacées
        self.assertNotIn("{{product_info}}", filled_template)
        self.assertIn("Écouteurs Bluetooth Premium", filled_template)
        self.assertIn("Autonomie 24h", filled_template)
        
        # Vérifier que tone et language ont été remplacés
        self.assertIn("Ton: persuasif", filled_template)
        self.assertIn("Langue: fr", filled_template)
        self.assertIn("Niche: electronics", filled_template)
    
    def test_templates_differences(self):
        """Vérifie que les templates sont différents entre eux"""
        templates = [
            TEMPLATE_PRODUCT_DESCRIPTION_STANDARD,
            TEMPLATE_PRODUCT_DESCRIPTION_FASHION,
            TEMPLATE_PRODUCT_DESCRIPTION_ELECTRONICS,
            TEMPLATE_PRODUCT_DESCRIPTION_HOME,
            TEMPLATE_PRODUCT_DESCRIPTION_BEAUTY
        ]
        
        # Vérifier l'unicité de chaque template
        for i in range(len(templates)):
            for j in range(i + 1, len(templates)):
                self.assertNotEqual(templates[i], templates[j], 
                                   f"Les templates {i} et {j} sont identiques")
    
    def test_templates_length(self):
        """Vérifie que les templates ont une longueur raisonnable"""
        templates = [
            TEMPLATE_PRODUCT_DESCRIPTION_STANDARD,
            TEMPLATE_PRODUCT_DESCRIPTION_FASHION,
            TEMPLATE_PRODUCT_DESCRIPTION_ELECTRONICS,
            TEMPLATE_PRODUCT_DESCRIPTION_HOME,
            TEMPLATE_PRODUCT_DESCRIPTION_BEAUTY
        ]
        
        # Chaque template devrait avoir une longueur suffisante pour guider la génération
        min_length = 500  # Caractères
        
        for i, template in enumerate(templates):
            self.assertGreater(len(template), min_length, 
                              f"Le template {i} est trop court")
    
    def test_templates_formatting(self):
        """Vérifie que les templates ont un formatage cohérent"""
        templates = [
            TEMPLATE_PRODUCT_DESCRIPTION_STANDARD,
            TEMPLATE_PRODUCT_DESCRIPTION_FASHION,
            TEMPLATE_PRODUCT_DESCRIPTION_ELECTRONICS,
            TEMPLATE_PRODUCT_DESCRIPTION_HOME,
            TEMPLATE_PRODUCT_DESCRIPTION_BEAUTY
        ]
        
        for template in templates:
            # Vérifier que le template utilise des sections avec des titres (# Section)
            self.assertRegex(template, r"#\s+\w+")
            
            # Vérifier qu'il contient des instructions numérotées
            # (au moins 5 instructions numérotées)
            instruction_matches = re.findall(r"\d+\.\s+\w+", template)
            self.assertGreaterEqual(len(instruction_matches), 5)
    
    def test_templates_consistency(self):
        """Vérifie la cohérence entre les templates"""
        templates = [
            TEMPLATE_PRODUCT_DESCRIPTION_STANDARD,
            TEMPLATE_PRODUCT_DESCRIPTION_FASHION,
            TEMPLATE_PRODUCT_DESCRIPTION_ELECTRONICS,
            TEMPLATE_PRODUCT_DESCRIPTION_HOME,
            TEMPLATE_PRODUCT_DESCRIPTION_BEAUTY
        ]
        
        # Tous les templates devraient avoir certaines sections communes
        common_sections = ["# Informations sur le produit", "# Ton et style", "# Instructions"]
        
        for template in templates:
            for section in common_sections:
                self.assertIn(section, template, 
                             f"Section {section} manquante dans un template")

if __name__ == "__main__":
    unittest.main()
