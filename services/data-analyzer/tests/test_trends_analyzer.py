#!/usr/bin/env python3
"""
Tests unitaires pour le module TrendsAnalyzer.
"""

import unittest
import os
import json
import pandas as pd
from unittest.mock import patch, MagicMock

# Inclusion du chemin parent pour importer les modules
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_sources.trends.trends_analyzer import TrendsAnalyzer

class TestTrendsAnalyzer(unittest.TestCase):
    """Tests pour la classe TrendsAnalyzer."""
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        # Configuration d'un répertoire de cache temporaire pour les tests
        self.temp_cache_dir = "/tmp/pytrends_test_cache"
        os.makedirs(self.temp_cache_dir, exist_ok=True)
        
        # Création d'une instance de l'analyseur
        self.analyzer = TrendsAnalyzer(
            hl="fr",
            tz=0,
            geo="FR",
            cache_dir=self.temp_cache_dir
        )
    
    def tearDown(self):
        """Nettoyage après les tests."""
        # Nettoyage du cache de test (optionnel)
        # import shutil
        # shutil.rmtree(self.temp_cache_dir, ignore_errors=True)
        pass
    
    def test_init(self):
        """Test l'initialisation de l'analyseur."""
        self.assertEqual(self.analyzer.hl, "fr")
        self.assertEqual(self.analyzer.tz, 0)
        self.assertEqual(self.analyzer.geo, "FR")
        self.assertEqual(self.analyzer.cache_dir, self.temp_cache_dir)
    
    def test_cache_file_path(self):
        """Test la génération du chemin de fichier de cache."""
        keywords = ["test1", "test2"]
        timeframe = "today 3-m"
        geo = "FR"
        cat = 0
        
        cache_path = self.analyzer._get_cache_file_path(keywords, timeframe, geo, cat)
        
        # Vérifier que le chemin contient le répertoire de cache
        self.assertTrue(cache_path.startswith(self.temp_cache_dir))
        
        # Vérifier que le chemin contient les paramètres
        self.assertIn("test1", cache_path)
        self.assertIn("test2", cache_path)
        self.assertIn("today", cache_path)
        self.assertIn("FR", cache_path)
    
    def test_calculate_trend_score(self):
        """Test le calcul du score de tendance."""
        # Cas 1: Bonne tendance
        score1 = self.analyzer._calculate_trend_score(
            current_interest=80,
            growth_rate=30,
            volatility=10,
            momentum=40
        )
        
        # Cas 2: Tendance moyenne
        score2 = self.analyzer._calculate_trend_score(
            current_interest=50,
            growth_rate=5,
            volatility=20,
            momentum=0
        )
        
        # Cas 3: Mauvaise tendance
        score3 = self.analyzer._calculate_trend_score(
            current_interest=20,
            growth_rate=-20,
            volatility=40,
            momentum=-30
        )
        
        # Vérifications
        self.assertGreater(score1, 70)  # Bon score
        self.assertGreater(score2, 40)  # Score moyen
        self.assertLess(score2, 70)     # Score moyen
        self.assertLess(score3, 40)     # Mauvais score
    
    @patch('pytrends.request.TrendReq')
    def test_analyze_keywords_mock(self, mock_trend_req):
        """Test l'analyse des mots-clés avec un mock PyTrends."""
        # Configuration du mock
        mock_pytrends = MagicMock()
        mock_trend_req.return_value = mock_pytrends
        
        # Mock des réponses
        mock_interest_over_time = pd.DataFrame({
            'test_keyword': [10, 20, 30, 40, 50],
            'isPartial': [False, False, False, False, False]
        })
        mock_interest_by_region = pd.DataFrame({
            'test_keyword': [30, 40, 50]
        })
        mock_related_queries = {
            'test_keyword': {
                'top': pd.DataFrame({'query': ['test query 1'], 'value': [100]}),
                'rising': pd.DataFrame({'query': ['test query 2'], 'value': [200]})
            }
        }
        mock_related_topics = {
            'test_keyword': {
                'top': pd.DataFrame({'value': ['test topic 1'], 'formattedValue': [1]}),
                'rising': pd.DataFrame({'value': ['test topic 2'], 'formattedValue': [2]})
            }
        }
        
        mock_pytrends.interest_over_time.return_value = mock_interest_over_time
        mock_pytrends.interest_by_region.return_value = mock_interest_by_region
        mock_pytrends.related_queries.return_value = mock_related_queries
        mock_pytrends.related_topics.return_value = mock_related_topics
        
        # Remplacer l'attribut pytrends de l'analyseur par notre mock
        self.analyzer.pytrends = mock_pytrends
        
        # Exécuter l'analyse avec le mock
        result = self.analyzer.analyze_keywords(
            keywords=["test_keyword"],
            timeframe="medium_term",
            use_cache=False
        )
        
        # Vérifier que la méthode build_payload a été appelée
        mock_pytrends.build_payload.assert_called_once()
        
        # Vérifier que les méthodes pour obtenir les données ont été appelées
        mock_pytrends.interest_over_time.assert_called_once()
        mock_pytrends.interest_by_region.assert_called_once()
        mock_pytrends.related_queries.assert_called_once()
        mock_pytrends.related_topics.assert_called_once()
        
        # Vérifier que le résultat contient les bonnes clés
        expected_keys = [
            'interest_over_time', 'related_queries', 'related_topics',
            'interest_by_region', 'trend_metrics', 'summary'
        ]
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Vérifier que le trend_metrics contient l'entrée pour le mot-clé
        self.assertIn('test_keyword', result['trend_metrics'])
        
        # Vérifier quelques métriques de base
        metrics = result['trend_metrics']['test_keyword']
        self.assertEqual(metrics['current_interest'], 50)  # Dernière valeur
        self.assertEqual(metrics['average_interest'], 30)  # Moyenne
        self.assertEqual(metrics['growth_rate'], 400.0)    # (50-10)/10 * 100
    
    def test_cache_save_load(self):
        """Test la sauvegarde et le chargement depuis le cache."""
        # Données de test
        test_data = {
            'interest_over_time': pd.DataFrame({
                'test_keyword': [10, 20, 30],
                'isPartial': [False, False, False]
            }),
            'summary': {
                'highlights': ['Test highlight'],
                'trend_status': {'test_keyword': 'stable'}
            }
        }
        
        # Chemin du fichier de cache
        cache_file = os.path.join(self.temp_cache_dir, 'test_cache.json')
        
        # Sauvegarde dans le cache
        self.analyzer._save_to_cache(cache_file, test_data)
        
        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(cache_file))
        
        # Chargement depuis le cache
        loaded_data = self.analyzer._load_from_cache(cache_file)
        
        # Vérifier que les données ont été correctement chargées
        self.assertIn('summary', loaded_data)
        self.assertIn('highlights', loaded_data['summary'])
        self.assertEqual(loaded_data['summary']['highlights'], ['Test highlight'])
        
        # Vérifier le chargement du DataFrame
        self.assertIn('interest_over_time', loaded_data)
        self.assertTrue(isinstance(loaded_data['interest_over_time'], pd.DataFrame))
    
    def test_generate_summary(self):
        """Test la génération de résumé d'analyse."""
        # Données de test
        trend_metrics = {
            'test_keyword': {
                'current_interest': 80,
                'average_interest': 60,
                'growth_rate': 30,
                'volatility': 10,
                'momentum': 20,
                'is_growing': True,
                'is_seasonal': False,
                'seasonality_score': 0,
                'trend_score': 75
            }
        }
        
        related_queries = {
            'test_keyword': {
                'top': pd.DataFrame({
                    'query': ['test query 1', 'test query 2'],
                    'value': [100, 90]
                }),
                'rising': pd.DataFrame({
                    'query': ['test query 3', 'test query 4'],
                    'value': [200, 150]
                })
            }
        }
        
        # Génération du résumé
        summary = self.analyzer._generate_summary(trend_metrics, related_queries)
        
        # Vérifications
        self.assertIn('highlights', summary)
        self.assertIn('top_related_queries', summary)
        self.assertIn('trend_status', summary)
        
        # Vérifier les points saillants
        self.assertTrue(any('tendance à la hausse' in h for h in summary['highlights']))
        
        # Vérifier le statut de tendance
        self.assertEqual(summary['trend_status']['test_keyword'], 'hausse')
        
        # Vérifier les requêtes associées
        self.assertIn('test_keyword', summary['top_related_queries'])
        self.assertEqual(len(summary['top_related_queries']['test_keyword']['top']), 2)
        self.assertEqual(len(summary['top_related_queries']['test_keyword']['rising']), 2)
    
    @patch('pytrends.request.TrendReq')
    def test_analyze_product(self, mock_trend_req):
        """Test l'analyse complète d'un produit."""
        # Configuration du mock
        mock_pytrends = MagicMock()
        mock_trend_req.return_value = mock_pytrends
        
        # Mock des réponses pour différentes périodes
        mock_responses = {}
        for timeframe in ['short_term', 'medium_term', 'long_term']:
            mock_responses[timeframe] = {
                'interest_over_time': pd.DataFrame({
                    'test_product': [30, 40, 50],
                    'isPartial': [False, False, False]
                }),
                'related_queries': {
                    'test_product': {
                        'top': pd.DataFrame({'query': [f'{timeframe} query'], 'value': [100]}),
                        'rising': pd.DataFrame({'query': [f'{timeframe} rising'], 'value': [200]})
                    }
                },
                'trend_metrics': {
                    'test_product': {
                        'current_interest': 50,
                        'growth_rate': 66.67,
                        'is_growing': True,
                        'trend_score': 70
                    }
                },
                'summary': {'highlights': [f'{timeframe} highlight']}
            }
        
        # Patch de la méthode analyze_keywords pour retourner nos mock responses
        with patch.object(self.analyzer, 'analyze_keywords') as mock_analyze:
            def side_effect(keywords, timeframe, **kwargs):
                if timeframe in mock_responses:
                    return mock_responses[timeframe]
                return {}
            
            mock_analyze.side_effect = side_effect
            
            # Exécution de l'analyse de produit
            result = self.analyzer.analyze_product(
                product_name="test_product",
                product_keywords=["keyword1", "keyword2"]
            )
            
            # Vérifications
            self.assertEqual(result['product_name'], 'test_product')
            self.assertIn('overall_trend_score', result)
            self.assertIn('is_trending', result)
            self.assertIn('seasonality', result)
            self.assertIn('conclusion', result)
            
            # Vérifier les appels à analyze_keywords
            self.assertEqual(mock_analyze.call_count, 3)  # Une fois pour chaque timeframe
    
    def test_is_product_trending(self):
        """Test la détection de produit en tendance."""
        # Cas où le produit est en tendance
        trending_results = {
            'short_term': {
                'trend_metrics': {
                    'test_product': {
                        'is_growing': True,
                        'trend_score': 80
                    }
                }
            },
            'medium_term': {
                'trend_metrics': {
                    'test_product': {
                        'is_growing': True,
                        'trend_score': 70
                    }
                }
            }
        }
        
        # Cas où le produit n'est pas en tendance
        not_trending_results = {
            'short_term': {
                'trend_metrics': {
                    'test_product': {
                        'is_growing': False,
                        'trend_score': 60
                    }
                }
            },
            'medium_term': {
                'trend_metrics': {
                    'test_product': {
                        'is_growing': True,
                        'trend_score': 50
                    }
                }
            }
        }
        
        # Cas avec erreur
        error_results = {
            'short_term': {
                'error': 'Something went wrong'
            },
            'medium_term': {
                'trend_metrics': {
                    'test_product': {
                        'is_growing': True,
                        'trend_score': 80
                    }
                }
            }
        }
        
        # Vérifications
        self.assertTrue(self.analyzer._is_product_trending(trending_results))
        self.assertFalse(self.analyzer._is_product_trending(not_trending_results))
        self.assertFalse(self.analyzer._is_product_trending(error_results))


if __name__ == '__main__':
    unittest.main()
