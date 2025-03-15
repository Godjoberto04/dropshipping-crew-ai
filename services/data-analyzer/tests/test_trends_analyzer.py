#!/usr/bin/env python3
"""
Tests unitaires pour le module TrendsAnalyzer.
Vérifie le bon fonctionnement de la classe d'analyse de tendances via Google Trends.
"""

import unittest
import os
import tempfile
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Import du module à tester
from data_sources.trends.trends_analyzer import TrendsAnalyzer

class TestTrendsAnalyzer(unittest.TestCase):
    """Classe de tests pour TrendsAnalyzer."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        # Création d'un répertoire temporaire pour le cache
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_dir = self.temp_dir.name
        
        # Création d'une instance de TrendsAnalyzer avec Mock
        self.patcher = patch('data_sources.trends.trends_analyzer.TrendReq')
        self.mock_trend_req = self.patcher.start()
        self.mock_trend_req.return_value = MagicMock()
        
        self.analyzer = TrendsAnalyzer(
            hl='fr',
            tz=0,
            geo='FR',
            cache_dir=self.cache_dir
        )
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        self.patcher.stop()
        self.temp_dir.cleanup()
    
    def test_init(self):
        """Test de l'initialisation de la classe."""
        self.assertEqual(self.analyzer.hl, 'fr')
        self.assertEqual(self.analyzer.tz, 0)
        self.assertEqual(self.analyzer.geo, 'FR')
        self.assertEqual(self.analyzer.cache_dir, self.cache_dir)
        self.assertTrue(os.path.exists(self.cache_dir))
    
    def test_get_cache_file_path(self):
        """Test de la génération du chemin de fichier cache."""
        keywords = ['smartphone', 'tablette']
        timeframe = 'today 3-m'
        geo = 'FR'
        category = 0
        
        cache_path = self.analyzer._get_cache_file_path(keywords, timeframe, geo, category)
        
        self.assertTrue(cache_path.startswith(self.cache_dir))
        self.assertTrue('trends_' in cache_path)
        self.assertTrue(cache_path.endswith('.pkl'))
    
    def test_is_likely_product(self):
        """Test de la détection de produits probables."""
        # Requêtes qui devraient être des produits
        self.assertTrue(self.analyzer._is_likely_product("iPhone 14 Pro Max"))
        self.assertTrue(self.analyzer._is_likely_product("Écouteurs Bluetooth sans fil"))
        self.assertTrue(self.analyzer._is_likely_product("Caméra de sécurité extérieure"))
        
        # Requêtes qui ne devraient pas être des produits
        self.assertFalse(self.analyzer._is_likely_product("comment réparer iPhone"))
        self.assertFalse(self.analyzer._is_likely_product("smartphone"))  # Mot unique
        self.assertFalse(self.analyzer._is_likely_product("où acheter des écouteurs"))
    
    def test_get_category_keywords(self):
        """Test de la récupération des mots-clés par catégorie."""
        # Test avec une catégorie connue
        fashion_keywords = self.analyzer._get_category_keywords("fashion")
        self.assertTrue("fashion" in fashion_keywords)
        self.assertTrue("fashion trends" in fashion_keywords)
        
        # Test avec une catégorie inconnue
        unknown_keywords = self.analyzer._get_category_keywords("unknown_category")
        self.assertTrue("unknown_category" in unknown_keywords)
        self.assertTrue("unknown_category trends" in unknown_keywords)
        
        # Test sans catégorie
        default_keywords = self.analyzer._get_category_keywords()
        self.assertTrue("trending products" in default_keywords)
    
    @patch('data_sources.trends.trends_analyzer.TrendsAnalyzer._calculate_trend_metrics')
    @patch('data_sources.trends.trends_analyzer.TrendsAnalyzer._generate_summary')
    def test_analyze_keywords_basic(self, mock_generate_summary, mock_calculate_metrics):
        """Test de base de la méthode analyze_keywords."""
        # Configuration des mocks
        self.analyzer.pytrends.interest_over_time.return_value = pd.DataFrame({
            'smartphone': [50, 60, 70]
        })
        self.analyzer.pytrends.related_queries.return_value = {'smartphone': {}}
        self.analyzer.pytrends.related_topics.return_value = {'smartphone': {}}
        self.analyzer.pytrends.interest_by_region.return_value = pd.DataFrame({
            'smartphone': [40, 50, 60]
        })
        
        mock_calculate_metrics.return_value = {'smartphone': {'trend_score': 75}}
        mock_generate_summary.return_value = {'top_keyword': 'smartphone'}
        
        # Appel de la méthode à tester avec cache désactivé
        result = self.analyzer.analyze_keywords('smartphone', use_cache=False)
        
        # Vérification des appels
        self.analyzer.pytrends.build_payload.assert_called_once()
        self.analyzer.pytrends.interest_over_time.assert_called_once()
        self.analyzer.pytrends.related_queries.assert_called_once()
        self.analyzer.pytrends.related_topics.assert_called_once()
        self.analyzer.pytrends.interest_by_region.assert_called_once()
        mock_calculate_metrics.assert_called_once()
        mock_generate_summary.assert_called_once()
        
        # Vérification du résultat
        self.assertIn('interest_over_time', result)
        self.assertIn('related_queries', result)
        self.assertIn('related_topics', result)
        self.assertIn('interest_by_region', result)
        self.assertIn('trend_metrics', result)
        self.assertIn('summary', result)
    
    def test_calculate_trend_score(self):
        """Test du calcul du score de tendance."""
        # Test avec des valeurs significatives
        score1 = self.analyzer._calculate_trend_score(
            current_interest=80,
            growth_rate=30,
            volatility=15,
            momentum=20,
            average_interest=75
        )
        self.assertGreater(score1, 70)  # Score élevé pour de bonnes métriques
        
        # Test avec des valeurs faibles
        score2 = self.analyzer._calculate_trend_score(
            current_interest=20,
            growth_rate=-15,
            volatility=50,
            momentum=-20,
            average_interest=25
        )
        self.assertLess(score2, 40)  # Score faible pour de mauvaises métriques
        
        # Vérification que current_interest est plafonné à 100
        score3 = self.analyzer._calculate_trend_score(
            current_interest=150,
            growth_rate=30,
            volatility=15,
            momentum=20,
            average_interest=75
        )
        score3_capped = self.analyzer._calculate_trend_score(
            current_interest=100,
            growth_rate=30,
            volatility=15,
            momentum=20,
            average_interest=75
        )
        self.assertEqual(score3, score3_capped)
    
    @patch('data_sources.trends.trends_analyzer.TrendsAnalyzer.analyze_keywords')
    def test_compare_products(self, mock_analyze_keywords):
        """Test de la comparaison de produits."""
        # Configuration du mock
        mock_analyze_keywords.return_value = {
            'interest_over_time': pd.DataFrame({
                'produit1': [50, 60, 70],
                'produit2': [40, 45, 50]
            }),
            'trend_metrics': {
                'produit1': {'trend_score': 75, 'growth_rate': 20, 'is_growing': True},
                'produit2': {'trend_score': 60, 'growth_rate': 10, 'is_growing': True}
            }
        }
        
        # Appel de la méthode à tester
        result = self.analyzer.compare_products(['produit1', 'produit2'])
        
        # Vérification du mock
        mock_analyze_keywords.assert_called_once()
        
        # Vérification du résultat
        self.assertIn('ranked_products', result)
        self.assertEqual(len(result['ranked_products']), 2)
        self.assertEqual(result['ranked_products'][0]['name'], 'produit1')  # Premier produit doit être produit1
        self.assertEqual(result['top_product'], 'produit1')
        self.assertIn('interest_over_time', result)
        self.assertIn('product_trends', result)
    
    @patch('data_sources.trends.trends_analyzer.TrendsAnalyzer.analyze_keywords')
    def test_calculate_overall_trend_score(self, mock_analyze_keywords):
        """Test du calcul du score de tendance global."""
        # Préparation des données de test
        results_by_timeframe = {
            'short_term': {
                'trend_metrics': {
                    'produit': {'trend_score': 80}
                }
            },
            'medium_term': {
                'trend_metrics': {
                    'produit': {'trend_score': 70}
                }
            },
            'long_term': {
                'trend_metrics': {
                    'produit': {'trend_score': 60}
                }
            }
        }
        
        # Appel de la méthode à tester
        score = self.analyzer._calculate_overall_trend_score(results_by_timeframe)
        
        # Vérification du résultat
        # Le score global devrait être une moyenne pondérée (0.5*80 + 0.3*70 + 0.2*60) = 73
        self.assertAlmostEqual(score, 73, delta=1)
        
        # Test avec données incomplètes
        incomplete_results = {
            'short_term': {
                'trend_metrics': {
                    'produit': {'trend_score': 80}
                }
            },
            'medium_term': {
                'error': 'Erreur lors de l\'analyse'
            }
        }
        
        incomplete_score = self.analyzer._calculate_overall_trend_score(incomplete_results)
        self.assertEqual(incomplete_score, 80)  # Seulement le short_term est pris en compte
    
    @patch('data_sources.trends.trends_analyzer.TrendsAnalyzer.analyze_keywords')
    def test_analyze_product(self, mock_analyze_keywords):
        """Test de l'analyse complète d'un produit."""
        # Configuration du mock
        def mock_analyze_side_effect(keywords, timeframe, **kwargs):
            return {
                'interest_over_time': pd.DataFrame({
                    keywords[0]: [60, 70, 80] if timeframe == 'now 7-d' else [50, 60, 70]
                }),
                'trend_metrics': {
                    keywords[0]: {
                        'trend_score': 75 if timeframe == 'now 7-d' else 65,
                        'growth_rate': 20 if timeframe == 'now 7-d' else 10,
                        'is_growing': True,
                        'is_seasonal': False
                    }
                }
            }
        
        mock_analyze_keywords.side_effect = mock_analyze_side_effect
        
        # Appel de la méthode à tester
        result = self.analyzer.analyze_product('produit test', product_keywords=['keyword1'])
        
        # Vérification des appels
        self.assertEqual(mock_analyze_keywords.call_count, 4)  # 3 timeframes + 1 produit associé
        
        # Vérification du résultat
        self.assertEqual(result['product_name'], 'produit test')
        self.assertIn('analysis_by_timeframe', result)
        self.assertIn('related_keywords_analysis', result)
        self.assertIn('overall_trend_score', result)
        self.assertIn('is_trending', result)
        self.assertIn('seasonality', result)
        self.assertIn('conclusion', result)
        
        # Le premier appel devrait être avec le nom du produit et le timeframe short_term
        first_call_args = mock_analyze_keywords.call_args_list[0][0]
        self.assertEqual(first_call_args[0], ['produit test'])

if __name__ == '__main__':
    unittest.main()
