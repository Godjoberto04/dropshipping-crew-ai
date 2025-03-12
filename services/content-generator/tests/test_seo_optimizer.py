#!/usr/bin/env python3
"""
Tests unitaires pour l'optimiseur SEO
"""

import unittest
import sys
import os
from pathlib import Path

# Ajout du répertoire parent au path pour importer les modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from optimizers.seo_optimizer import SEOOptimizer

class TestSEOOptimizer(unittest.TestCase):
    """Tests pour la classe SEOOptimizer"""
    
    def setUp(self):
        """Configuration commune pour tous les tests"""
        self.optimizer = SEOOptimizer()
        
        # Exemple de contenu pour les tests
        self.sample_content = """
## Écouteurs Bluetooth Premium

Découvrez nos écouteurs Bluetooth Premium par TechSound, conçus pour offrir une expérience audio exceptionnelle. Avec leur autonomie impressionnante de 24 heures, vous pouvez profiter de votre musique préférée toute la journée sans interruption.

### Caractéristiques principales

* **Autonomie de 24h** - Profitez de votre musique toute la journée sans recharge
* **Suppression active du bruit** - Immergez-vous complètement dans votre musique
* **Résistant à l'eau (IPX7)** - Parfait pour les entraînements intenses
* **Connectivité Bluetooth 5.2** - Connexion stable et économie d'énergie
* **Commandes tactiles intuitives** - Contrôlez facilement votre musique du bout des doigts

### Qualité sonore exceptionnelle

Fabriqués avec des pilotes dynamiques de 10mm, ces écouteurs offrent des basses profondes, des médiums clairs et des aigus cristallins. La technologie de suppression active du bruit élimine efficacement les bruits ambiants pour vous permettre de vous concentrer sur ce qui compte vraiment : votre musique.

### Confort et durabilité

Les embouts en silicone doux s'adaptent parfaitement à vos oreilles pour un port confortable, même pendant de longues périodes. La certification IPX7 garantit une résistance à l'eau et à la transpiration, ce qui en fait le compagnon idéal pour vos entraînements sportifs.

## Commander dès maintenant

Ne manquez pas cette opportunité d'améliorer votre expérience audio quotidienne. Commandez vos écouteurs Bluetooth Premium dès aujourd'hui et profitez d'une livraison rapide et gratuite !
"""
        
        self.sample_keywords = ["écouteurs bluetooth", "suppression de bruit", "autonomie"]
    
    def test_extract_keywords(self):
        """Teste l'extraction automatique de mots-clés"""
        extracted_keywords = self.optimizer.extract_keywords(self.sample_content, max_keywords=5)
        
        # Vérifier qu'on obtient bien le bon nombre de mots-clés
        self.assertEqual(len(extracted_keywords), 5)
        
        # Vérifier que les mots-clés extraits sont pertinents
        common_audio_terms = ["écouteurs", "bluetooth", "audio", "musique", "bruit", "autonomie"]
        matches = sum(1 for kw in extracted_keywords if any(term in kw for term in common_audio_terms))
        
        # Au moins 3 mots-clés devraient correspondre à des termes audio courants
        self.assertGreaterEqual(matches, 3)
    
    def test_analyze_keyword_density(self):
        """Teste l'analyse de densité des mots-clés"""
        densities = self.optimizer.analyze_keyword_density(self.sample_content, self.sample_keywords)
        
        # Vérifier que tous les mots-clés ont une densité calculée
        self.assertEqual(len(densities), len(self.sample_keywords))
        
        # Vérifier que toutes les densités sont positives ou nulles
        for keyword, density in densities.items():
            self.assertGreaterEqual(density, 0.0)
        
        # Le mot-clé "écouteurs bluetooth" devrait avoir une densité non nulle
        self.assertGreater(densities["écouteurs bluetooth"], 0.0)
    
    def test_optimize(self):
        """Teste l'optimisation du contenu"""
        optimized_content = self.optimizer.optimize(
            content=self.sample_content,
            keywords=self.sample_keywords,
            content_type="product_description"
        )
        
        # Dans cette première version, optimize() ne modifie pas le contenu
        # donc on vérifie juste que le contenu est retourné sans modification
        self.assertEqual(optimized_content, self.sample_content)
    
    def test_generate_meta_description(self):
        """Teste la génération de méta-description"""
        product_name = "Écouteurs Bluetooth Premium"
        meta_description = self.optimizer.generate_meta_description(
            content=self.sample_content,
            product_name=product_name,
            max_length=160
        )
        
        # Vérifier que la méta-description n'est pas vide
        self.assertTrue(meta_description)
        
        # Vérifier que la méta-description respecte la limite de longueur
        self.assertLessEqual(len(meta_description), 160)
        
        # Vérifier que le nom du produit est présent dans la méta-description
        self.assertIn(product_name.lower(), meta_description.lower())
    
    def test_calculate_improvement_score(self):
        """Teste le calcul du score d'amélioration"""
        original_content = "Écouteurs Bluetooth avec suppression du bruit et grande autonomie."
        optimized_content = "Écouteurs Bluetooth Premium avec technologie avancée de suppression active du bruit et une autonomie exceptionnelle de 24 heures. Parfaits pour les amateurs de musique en déplacement."
        
        score = self.optimizer.calculate_improvement_score(original_content, optimized_content)
        
        # Vérifier que le score est dans la plage attendue (entre 0 et 100)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
        
        # L'optimized_content étant plus long, le score devrait être > 0
        self.assertGreater(score, 0.0)
        
        # Cas inverse (contenu optimisé plus court)
        inverse_score = self.optimizer.calculate_improvement_score(optimized_content, original_content)
        self.assertEqual(inverse_score, 0.0)  # Devrait retourner 0 car pas d'amélioration

if __name__ == "__main__":
    unittest.main()