"""
Tests pour le module d'analyse de complémentarité.

Ce module contient les tests unitaires pour valider le fonctionnement
des classes ComplementaryAnalyzer et AssociationRulesMiner.
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import logging

# Import des modules à tester
from models.complementary.association_rules import AssociationRulesMiner
from models.complementary.complementary_analyzer import ComplementaryAnalyzer

# Configuration du logging
logging.basicConfig(level=logging.ERROR)


class TestAssociationRulesMiner(unittest.TestCase):
    """Tests pour la classe AssociationRulesMiner."""
    
    def setUp(self):
        """Initialisation des données de test."""
        # Données de transactions simples pour les tests
        self.transactions = [
            ['product1', 'product2', 'product3'],
            ['product1', 'product2', 'product4'],
            ['product1', 'product4'],
            ['product2', 'product3'],
            ['product1', 'product2'],
            ['product2', 'product3', 'product5'],
            ['product1', 'product2', 'product3', 'product5'],
            ['product2', 'product4'],
            ['product1', 'product3'],
            ['product2', 'product3', 'product4']
        ]
        
        # Initialisation avec des seuils bas pour les tests
        self.miner = AssociationRulesMiner(min_support=0.2, min_confidence=0.3, min_lift=1.0)
    
    def test_fit_and_get_rules(self):
        """Test de l'extraction des règles d'association."""
        # Extraction des règles
        self.miner.fit(self.transactions)
        
        # Vérification qu'on a bien des règles
        rules = self.miner.get_rules()
        self.assertGreater(len(rules), 0, "Aucune règle d'association trouvée")
        
        # Vérification de la structure d'une règle
        rule = rules[0]
        self.assertIn('antecedent', rule, "La règle ne contient pas d'antécédent")
        self.assertIn('consequent', rule, "La règle ne contient pas de conséquent")
        self.assertIn('support', rule, "La règle ne contient pas de support")
        self.assertIn('confidence', rule, "La règle ne contient pas de confiance")
        self.assertIn('lift', rule, "La règle ne contient pas de lift")
        
        # Vérification que le support, la confiance et le lift sont dans les bornes attendues
        self.assertGreaterEqual(rule['support'], self.miner.min_support)
        self.assertGreaterEqual(rule['confidence'], self.miner.min_confidence)
        self.assertGreaterEqual(rule['lift'], self.miner.min_lift)
    
    def test_get_product_recommendations(self):
        """Test des recommandations de produits."""
        # Extraction des règles
        self.miner.fit(self.transactions)
        
        # Obtention des recommandations pour product1
        recommendations = self.miner.get_product_recommendations(['product1'])
        
        # Vérification qu'on a des recommandations
        self.assertGreater(len(recommendations), 0, "Aucune recommandation trouvée")
        
        # Vérification que product1 n'est pas dans les recommandations
        recommended_products = [rec['product'] for rec in recommendations]
        self.assertNotIn('product1', recommended_products, "Le produit lui-même est recommandé")
        
        # Vérification qu'on peut limiter le nombre de recommandations
        limited_recommendations = self.miner.get_product_recommendations(['product1'], top_n=1)
        self.assertEqual(len(limited_recommendations), 1, "Limitation du nombre de recommandations ne fonctionne pas")
        
        # Vérification que la meilleure recommandation a un lift plus élevé
        self.assertGreaterEqual(
            recommendations[0]['lift'],
            recommendations[-1]['lift'] if len(recommendations) > 1 else 0,
            "Les recommandations ne sont pas triées par lift"
        )
    
    def test_min_thresholds(self):
        """Test de l'effet des seuils minimaux."""
        # Initialisation avec des seuils plus élevés
        strict_miner = AssociationRulesMiner(min_support=0.4, min_confidence=0.6, min_lift=1.5)
        strict_miner.fit(self.transactions)
        
        # Initialisation avec des seuils bas
        lenient_miner = AssociationRulesMiner(min_support=0.1, min_confidence=0.2, min_lift=1.0)
        lenient_miner.fit(self.transactions)
        
        # Vérification que des seuils plus élevés donnent moins de règles
        strict_rules = strict_miner.get_rules()
        lenient_rules = lenient_miner.get_rules()
        
        self.assertGreaterEqual(
            len(lenient_rules),
            len(strict_rules),
            "Des seuils plus stricts devraient donner moins de règles"
        )


class TestComplementaryAnalyzer(unittest.TestCase):
    """Tests pour la classe ComplementaryAnalyzer."""
    
    def setUp(self):
        """Initialisation des données de test."""
        # Données de transactions simples pour les tests
        self.transactions = [
            ['product1', 'product2', 'product3'],
            ['product1', 'product2', 'product4'],
            ['product1', 'product4'],
            ['product2', 'product3'],
            ['product1', 'product2'],
            ['product2', 'product3', 'product5'],
            ['product1', 'product2', 'product3', 'product5'],
            ['product2', 'product4'],
            ['product1', 'product3'],
            ['product2', 'product3', 'product4']
        ]
        
        # Métadonnées des produits
        self.product_metadata = {
            'product1': {
                'name': 'Smartphone XYZ',
                'category': 'smartphones',
                'price': 299.99,
                'rating': 4.2,
                'popularity': 85
            },
            'product2': {
                'name': 'Coque de protection',
                'category': 'phone_cases',
                'price': 19.99,
                'rating': 4.5,
                'popularity': 92
            },
            'product3': {
                'name': 'Chargeur rapide',
                'category': 'chargers',
                'price': 29.99,
                'rating': 4.0,
                'popularity': 78
            },
            'product4': {
                'name': 'Écouteurs sans fil',
                'category': 'headphones',
                'price': 89.99,
                'rating': 4.7,
                'popularity': 90
            },
            'product5': {
                'name': 'Protection d\'écran',
                'category': 'screen_protectors',
                'price': 9.99,
                'rating': 3.8,
                'popularity': 65
            },
            'product6': {
                'name': 'Smartphone Premium',
                'category': 'smartphones',
                'price': 499.99,
                'rating': 4.8,
                'popularity': 75
            }
        }
        
        # Initialisation de l'analyseur
        self.analyzer = ComplementaryAnalyzer()
        
        # Chargement des données
        self.analyzer.load_transaction_data(self.transactions)
        self.analyzer.load_product_metadata(self.product_metadata)
        
        # Définition manuelle des paires de catégories
        self.category_pairs = {
            'smartphones': ['phone_cases', 'screen_protectors', 'chargers', 'headphones'],
            'phone_cases': ['screen_protectors', 'smartphones'],
            'chargers': ['smartphones', 'headphones'],
            'headphones': ['smartphones', 'chargers'],
            'screen_protectors': ['smartphones', 'phone_cases']
        }
        self.analyzer.set_category_pairs(self.category_pairs)
    
    def test_get_complementary_products(self):
        """Test de l'obtention de produits complémentaires."""
        # Obtention des produits complémentaires pour product1 (smartphone)
        complementary_products = self.analyzer.get_complementary_products('product1')
        
        # Vérification qu'on a des recommandations
        self.assertGreater(len(complementary_products), 0, "Aucun produit complémentaire trouvé")
        
        # Vérification que product1 n'est pas dans les recommandations
        recommended_products = [rec['product'] for rec in complementary_products]
        self.assertNotIn('product1', recommended_products, "Le produit lui-même est recommandé")
        
        # Vérification qu'on peut limiter le nombre de recommandations
        limited_recommendations = self.analyzer.get_complementary_products('product1', max_products=2)
        self.assertLessEqual(len(limited_recommendations), 2, "Limitation du nombre de recommandations ne fonctionne pas")
        
        # Vérification que chaque recommandation a un score
        for rec in complementary_products:
            self.assertIn('score', rec, "La recommandation n'a pas de score")
            self.assertIn('source', rec, "La recommandation n'a pas de source")
    
    def test_get_upsell_products(self):
        """Test de l'obtention de produits d'up-sell."""
        # Obtention des produits d'up-sell pour product1 (smartphone)
        upsell_products = self.analyzer.get_upsell_products('product1')
        
        # Vérification qu'on a des recommandations d'up-sell
        self.assertGreater(len(upsell_products), 0, "Aucun produit d'up-sell trouvé")
        
        # Vérification que product6 (smartphone premium) est recommandé
        upsell_product_ids = [up['product'] for up in upsell_products]
        self.assertIn('product6', upsell_product_ids, "Le smartphone premium n'est pas recommandé en up-sell")
        
        # Vérification des métadonnées d'up-sell
        for up in upsell_products:
            self.assertIn('score', up, "L'up-sell n'a pas de score")
            self.assertIn('price_difference', up, "L'up-sell n'a pas de différence de prix")
            self.assertIn('price_ratio', up, "L'up-sell n'a pas de ratio de prix")
            self.assertIn('source', up, "L'up-sell n'a pas de source")
    
    def test_bundle_products(self):
        """Test de la création de bundles."""
        # Création de bundles pour product1 + product2
        bundles = self.analyzer.bundle_products(['product1', 'product2'])
        
        # Vérification qu'on a des bundles
        self.assertGreater(len(bundles), 0, "Aucun bundle créé")
        
        # Vérification des attributs du bundle
        bundle = bundles[0]
        self.assertIn('name', bundle, "Le bundle n'a pas de nom")
        self.assertIn('products', bundle, "Le bundle n'a pas de liste de produits")
        self.assertIn('original_price', bundle, "Le bundle n'a pas de prix original")
        self.assertIn('bundle_price', bundle, "Le bundle n'a pas de prix de bundle")
        self.assertIn('discount_percentage', bundle, "Le bundle n'a pas de pourcentage de remise")
        
        # Vérification que le prix du bundle est inférieur au prix original
        self.assertLess(bundle['bundle_price'], bundle['original_price'], "Le prix du bundle n'est pas réduit")
        
        # Vérification que tous les produits du panier initial sont dans le bundle
        for product_id in ['product1', 'product2']:
            self.assertIn(product_id, bundle['products'], f"{product_id} n'est pas dans le bundle")
    
    def test_analyze_cart(self):
        """Test de l'analyse de panier."""
        # Analyse d'un panier simple
        cart_analysis = self.analyzer.analyze_cart(['product1'])
        
        # Vérification des sections de l'analyse
        self.assertIn('cart_value', cart_analysis, "L'analyse n'a pas de valeur de panier")
        self.assertIn('product_count', cart_analysis, "L'analyse n'a pas de nombre de produits")
        self.assertIn('missing_complementary', cart_analysis, "L'analyse n'a pas de produits complémentaires manquants")
        self.assertIn('potential_upsells', cart_analysis, "L'analyse n'a pas d'opportunités d'up-sell")
        self.assertIn('bundle_opportunities', cart_analysis, "L'analyse n'a pas d'opportunités de bundle")
        self.assertIn('cart_score', cart_analysis, "L'analyse n'a pas de score de panier")
        
        # Vérification que la valeur du panier est correcte
        self.assertEqual(cart_analysis['cart_value'], 299.99, "La valeur du panier est incorrecte")
        
        # Vérification qu'on a des recommandations complémentaires pour un panier incomplet
        self.assertGreater(len(cart_analysis['missing_complementary']), 0, "Pas de produits complémentaires suggérés")
        
        # Vérification qu'on a des opportunités d'up-sell
        self.assertGreater(len(cart_analysis['potential_upsells']), 0, "Pas d'opportunités d'up-sell")
        
        # Vérification qu'on a des opportunités de bundle pour un petit panier
        self.assertGreater(len(cart_analysis['bundle_opportunities']), 0, "Pas d'opportunités de bundle")
        
        # Test avec un panier plus complet
        complete_cart_analysis = self.analyzer.analyze_cart(['product1', 'product2', 'product3', 'product4'])
        
        # Vérification que le score du panier plus complet est meilleur (plus bas)
        self.assertLess(
            complete_cart_analysis['cart_score'],
            cart_analysis['cart_score'],
            "Le score d'un panier plus complet devrait être meilleur"
        )


if __name__ == '__main__':
    unittest.main()
