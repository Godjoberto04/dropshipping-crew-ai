#!/usr/bin/env python3
"""
Tests unitaires pour le système de scoring multicritères.
"""

import unittest
import os
import sys
import json
from unittest.mock import MagicMock, patch

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.scoring.multicriteria import AdvancedProductScorer
from models.scoring.multicriteria_core import (
    apply_niche_optimizations,
    calculate_category_score,
    calculate_confidence,
    identify_strengths_weaknesses
)

class TestAdvancedProductScorer(unittest.TestCase):
    """Tests pour la classe AdvancedProductScorer."""
    
    def setUp(self):
        """Configuration des tests."""
        self.scorer = AdvancedProductScorer()
        
        # Données de test
        self.test_product = {
            'id': 'test_product_1',
            'name': 'Test Product',
            'niche': 'electronics',
            'seo': {
                'search_volume': 5000,
                'keyword_difficulty': 45
            },
            'marketplace': {
                'competitor_count': 15,
                'price_competition': 60,
                'margin_percentage': 40,
                'price_gap': 25,
                'retail_price': 99.99,
                'supplier_price': 59.99
            },
            'trends': {
                'trend_metrics': {
                    'test product': {
                        'current_interest': 65,
                        'growth_rate': 22,
                        'volatility': 30,
                        'momentum': 15,
                        'is_growing': True,
                        'is_seasonal': False,
                        'trend_score': 70
                    }
                }
            }
        }
    
    def test_initialization(self):
        """Teste l'initialisation du scorer."""
        self.assertIsNotNone(self.scorer)
        self.assertIsNotNone(self.scorer.config)
        self.assertIsNotNone(self.scorer.criterion_functions)
        self.assertEqual(len(self.scorer.criterion_functions), 15)
    
    def test_default_config(self):
        """Teste la configuration par défaut."""
        config = self.scorer._default_config()
        self.assertIn('weights', config)
        self.assertIn('criteria', config)
        self.assertIn('market_potential', config['criteria'])
        self.assertIn('competition', config['criteria'])
        self.assertIn('profitability', config['criteria'])
        self.assertIn('operational', config['criteria'])
        self.assertIn('trend', config['criteria'])
    
    def test_niche_optimizations(self):
        """Teste le chargement des optimisations par niche."""
        niche_optimizations = self.scorer._load_niche_optimizations()
        self.assertIn('fashion', niche_optimizations)
        self.assertIn('electronics', niche_optimizations)
        self.assertIn('home_decor', niche_optimizations)
        self.assertIn('beauty', niche_optimizations)
        self.assertIn('fitness', niche_optimizations)
    
    def test_apply_niche_optimizations(self):
        """Teste l'application des optimisations par niche."""
        # Créer une configuration de test
        test_config = {
            'weights': {'market_potential': 0.3, 'trend': 0.1},
            'criteria': {
                'trend': [
                    {'name': 'seasonality', 'weight': 0.3}
                ]
            },
            'niche_adjustments': True
        }
        
        # Créer des optimisations de test
        test_optimizations = {
            'electronics': {
                'weights': {'trend': 0.15},
                'criteria_adjustments': {'seasonality': 1.5}
            }
        }
        
        # Appliquer les optimisations
        adjusted_config = apply_niche_optimizations(test_config, 'electronics', test_optimizations)
        
        # Vérifier les ajustements
        self.assertEqual(adjusted_config['weights']['trend'], 0.15)
        self.assertEqual(adjusted_config['criteria']['trend'][0]['weight'], 0.45)
    
    def test_score_product(self):
        """Teste le calcul du score d'un produit."""
        # Exécuter le scoring
        result = self.scorer.score_product(self.test_product)
        
        # Vérifier les résultats de base
        self.assertIn('overall_score', result)
        self.assertIn('category_scores', result)
        self.assertIn('recommendation', result)
        self.assertIn('confidence', result)
        self.assertIn('strengths', result)
        self.assertIn('weaknesses', result)
        self.assertIn('explanation', result)
        
        # Vérifier les scores par catégorie
        category_scores = result['category_scores']
        self.assertIn('market_potential', category_scores)
        self.assertIn('competition', category_scores)
        self.assertIn('profitability', category_scores)
        
        # Vérifier que les scores sont dans la plage 0-100
        self.assertGreaterEqual(result['overall_score'], 0)
        self.assertLessEqual(result['overall_score'], 100)
        
        for _, score in category_scores.items():
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)
    
    def test_gather_data(self):
        """Teste la collecte de données."""
        # Créer des mocks pour les sources de données
        mock_trends = MagicMock()
        mock_trends.analyze.return_value = {'trend_data': 'test'}
        
        mock_marketplace = MagicMock()
        mock_marketplace.analyze.return_value = {'marketplace_data': 'test'}
        
        # Enregistrer les sources mockées
        self.scorer.register_data_source('trends', mock_trends)
        self.scorer.register_data_source('marketplace', mock_marketplace)
        
        # Exécuter la collecte de données
        data = self.scorer.gather_data('test_product_1', {'name': 'Test Product'})
        
        # Vérifier que les données ont été collectées
        self.assertIn('product_id', data)
        self.assertIn('basic_info', data)
        self.assertIn('trends', data)
        self.assertIn('marketplace', data)
        
        # Vérifier que les méthodes d'analyse ont été appelées
        mock_trends.analyze.assert_called_once()
        mock_marketplace.analyze.assert_called_once_with('test_product_1')
    
    def test_calculate_confidence(self):
        """Teste le calcul du niveau de confiance."""
        # Données de test
        data = {
            'seo': {'search_volume': 5000},
            'marketplace': {'margin_percentage': 40, 'competitor_count': 15},
            'trends': {'test': 'data'},
            'social': {'test': 'data'}
        }
        
        category_scores = {
            'market_potential': 70,
            'competition': 60,
            'profitability': 65,
            'operational': 55,
            'trend': 75
        }
        
        critical_criteria = ['search_volume', 'margin', 'competitor_count']
        
        # Calculer la confiance
        confidence = calculate_confidence(data, category_scores, critical_criteria)
        
        # Vérifier que la confiance est dans la plage 0-100
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 100)
    
    def test_identify_strengths_weaknesses(self):
        """Teste l'identification des forces et faiblesses."""
        # Données de test
        category_scores = {
            'market_potential': 80,  # Force
            'competition': 30,       # Faiblesse
            'profitability': 65,     # Neutre
            'operational': 75,       # Force
            'trend': 35              # Faiblesse
        }
        
        config = {'default_config': 'test'}
        
        # Identifier les forces et faiblesses
        strengths, weaknesses = identify_strengths_weaknesses(category_scores, config)
        
        # Vérifier les résultats
        self.assertEqual(len(strengths), 2)
        self.assertEqual(len(weaknesses), 2)
        
        # Vérifier que les forces et faiblesses sont correctement identifiées
        strength_categories = [s['category'] for s in strengths]
        weakness_categories = [w['category'] for w in weaknesses]
        
        self.assertIn('market_potential', strength_categories)
        self.assertIn('operational', strength_categories)
        self.assertIn('competition', weakness_categories)
        self.assertIn('trend', weakness_categories)
    
    def test_batch_scoring(self):
        """Teste le scoring par lots."""
        # Créer une liste de produits à évaluer
        products = [
            self.test_product,
            {
                'id': 'test_product_2',
                'name': 'Another Test Product',
                'niche': 'fashion',
                'seo': {'search_volume': 2000},
                'marketplace': {'competitor_count': 25, 'margin_percentage': 30}
            }
        ]
        
        # Exécuter le scoring par lots
        results = self.scorer.batch_score_products(products)
        
        # Vérifier les résultats
        self.assertEqual(len(results), 2)
        self.assertIn('overall_score', results[0])
        self.assertIn('overall_score', results[1])
        
        # Vérifier que les résultats sont différents
        self.assertNotEqual(results[0]['overall_score'], results[1]['overall_score'])
    
    def test_explain_score(self):
        """Teste la génération d'explications de score."""
        # Exécuter le scoring
        result = self.scorer.score_product(self.test_product)
        
        # Obtenir l'explication
        explanation = self.scorer.explain_score(result)
        
        # Vérifier l'explication
        self.assertIn('summary', explanation)
        self.assertIn('key_factors', explanation)
        self.assertIn('confidence_statement', explanation)
        
        # Vérifier que le résumé n'est pas vide
        self.assertTrue(len(explanation['summary']) > 0)
        
        # Vérifier qu'il y a des facteurs clés
        self.assertTrue(len(explanation['key_factors']) > 0)

if __name__ == '__main__':
    unittest.main()
