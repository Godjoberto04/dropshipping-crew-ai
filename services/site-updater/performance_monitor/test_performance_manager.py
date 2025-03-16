"""
Tests unitaires pour le module PerformanceManager
"""

import unittest
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime
import json

# Importer les modules à tester
from performance_manager import PerformanceManager
from performance_utils import ImageOptimizer, ResourceMinifier, PerformanceMetricsAnalyzer

class TestPerformanceManager(unittest.TestCase):
    """Tests pour la classe PerformanceManager"""
    
    def setUp(self):
        """Initialisation avant chaque test"""
        self.manager = PerformanceManager(
            api_url="http://example.com/api",
            shopify_api_key="test_key",
            shopify_api_secret="test_secret",
            shopify_store_url="http://test-store.myshopify.com"
        )
        
        # Données de test pour la performance
        self.test_performance_data = {
            "page_load_time": 2.5,
            "time_to_first_byte": 0.4,
            "first_contentful_paint": 1.2,
            "largest_contentful_paint": 1.8,
            "cumulative_layout_shift": 0.05,
            "first_input_delay": 0.07,
            "server_response_time": 0.3,
            "timestamp": datetime.now().isoformat(),
            "url": "http://test-store.myshopify.com/products/example"
        }
        
        # Données de test pour les ressources
        self.test_resource_data = {
            "js_files": {
                "count": 8,
                "total_size": 950000,
                "minified_count": 7,
                "issues": [
                    {"file": "custom.js", "issue": "Non minifié", "impact": "Faible"}
                ]
            },
            "css_files": {
                "count": 3,
                "total_size": 250000,
                "minified_count": 3,
                "issues": []
            },
            "images": {
                "count": 15,
                "total_size": 3200000,
                "optimized_count": 10,
                "issues": [
                    {"file": "banner.jpg", "issue": "Image non optimisée", "impact": "Moyen"}
                ]
            },
            "fonts": {
                "count": 2,
                "total_size": 180000,
                "issues": []
            },
            "timestamp": datetime.now().isoformat(),
            "url": "http://test-store.myshopify.com/products/example"
        }
    
    async def async_test(self, coro):
        """Exécute un test asynchrone"""
        return await coro
    
    def test_identify_performance_issues(self):
        """Teste la fonction d'identification des problèmes de performance"""
        issues = self.manager.identify_performance_issues(
            self.test_performance_data, self.test_resource_data
        )
        
        # Vérifier que la fonction identifie correctement les problèmes
        self.assertIsInstance(issues, list)
        
        # Le temps de chargement de page devrait être identifié comme un problème
        page_load_issues = [i for i in issues if i.get("metric") == "page_load_time"]
        self.assertEqual(len(page_load_issues), 1)
        
        # L'image non optimisée devrait être détectée
        image_issues = [i for i in issues if i.get("resource_type") == "images"]
        self.assertEqual(len(image_issues), 1)
        
        # Vérifier que l'impact est correctement évalué
        self.assertEqual(image_issues[0]["severity"], "Moyen")
    
    def test_generate_optimization_suggestions(self):
        """Teste la génération de suggestions d'optimisation"""
        # Créer une liste de problèmes de test
        test_issues = [
            {
                "type": "performance_metric",
                "metric": "page_load_time",
                "value": 4.2,
                "threshold": 3.0,
                "severity": "Élevé",
                "description": "La métrique page_load_time (4.2) dépasse le seuil recommandé (3.0)"
            },
            {
                "type": "resource_issue",
                "resource_type": "images",
                "file": "banner.jpg",
                "issue": "Image non optimisée",
                "severity": "Moyen",
                "description": "Image non optimisée dans banner.jpg (Impact: Moyen)"
            }
        ]
        
        suggestions = self.manager.generate_optimization_suggestions(test_issues)
        
        # Vérifier que des suggestions sont générées
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
        # Vérifier que les suggestions correspondent aux problèmes
        time_suggestions = [s for s in suggestions if "temps de chargement" in s["title"].lower()]
        self.assertEqual(len(time_suggestions), 1)
        
        image_suggestions = [s for s in suggestions if "image" in s["title"].lower()]
        self.assertEqual(len(image_suggestions), 1)
        
        # Vérifier que la priorité est correctement définie
        high_priority = [s for s in suggestions if s["priority"] == "Élevée"]
        self.assertGreater(len(high_priority), 0)
    
    @patch('aiohttp.ClientSession')
    def test_collect_performance_data(self, mock_session):
        """Teste la collecte de données de performance (avec mock)"""
        # Configurer le comportement du mock
        mock_session_instance = MagicMock()
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        
        # Exécuter le test asynchrone
        result = asyncio.run(self.async_test(
            self.manager.collect_performance_data("http://test-store.myshopify.com/products/example")
        ))
        
        # Vérifier le résultat
        self.assertIsInstance(result, dict)
        self.assertIn("page_load_time", result)
        self.assertIn("largest_contentful_paint", result)
        self.assertIn("cumulative_layout_shift", result)
    
    @patch('aiohttp.ClientSession')
    def test_analyze_resources(self, mock_session):
        """Teste l'analyse des ressources (avec mock)"""
        # Configurer le comportement du mock
        mock_session_instance = MagicMock()
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        
        # Exécuter le test asynchrone
        result = asyncio.run(self.async_test(
            self.manager.analyze_resources("http://test-store.myshopify.com/products/example")
        ))
        
        # Vérifier le résultat
        self.assertIsInstance(result, dict)
        self.assertIn("js_files", result)
        self.assertIn("css_files", result)
        self.assertIn("images", result)
    
    def test_calculate_performance_score(self):
        """Teste le calcul du score de performance"""
        # Test avec de bonnes métriques
        good_metrics = {
            "page_load_time": 2.0,
            "largest_contentful_paint": 1.5,
            "cumulative_layout_shift": 0.05
        }
        good_issues = []
        
        good_score = self.manager._calculate_performance_score(good_metrics, good_issues)
        self.assertGreaterEqual(good_score, 90)
        
        # Test avec des métriques problématiques
        bad_metrics = {
            "page_load_time": 6.0,
            "largest_contentful_paint": 4.5,
            "cumulative_layout_shift": 0.3
        }
        bad_issues = [
            {"severity": "Élevé"},
            {"severity": "Élevé"},
            {"severity": "Moyen"}
        ]
        
        bad_score = self.manager._calculate_performance_score(bad_metrics, bad_issues)
        self.assertLessEqual(bad_score, 70)


class TestImageOptimizer(unittest.TestCase):
    """Tests pour la classe ImageOptimizer"""
    
    async def async_test(self, coro):
        """Exécute un test asynchrone"""
        return await coro
    
    def test_optimize_image(self):
        """Teste l'optimisation d'une image"""
        result = asyncio.run(self.async_test(
            ImageOptimizer.optimize_image("http://example.com/image.jpg", "webp")
        ))
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertIn("optimization_ratio", result)
    
    def test_bulk_optimize_images(self):
        """Teste l'optimisation en masse des images"""
        test_urls = [
            "http://example.com/image1.jpg",
            "http://example.com/image2.png",
            "http://example.com/image3.jpg"
        ]
        
        result = asyncio.run(self.async_test(
            ImageOptimizer.bulk_optimize_images(test_urls, "webp")
        ))
        
        self.assertIsInstance(result, dict)
        self.assertIn("summary", result)
        self.assertIn("successful_optimizations", result["summary"])
        self.assertEqual(result["summary"]["total_images"], len(test_urls))


class TestResourceMinifier(unittest.TestCase):
    """Tests pour la classe ResourceMinifier"""
    
    async def async_test(self, coro):
        """Exécute un test asynchrone"""
        return await coro
    
    def test_minify_js(self):
        """Teste la minification JavaScript"""
        test_js = """
        // Ceci est un commentaire
        function testFunction() {
            // Un autre commentaire
            var x = 10;
            var y = 20;
            return x + y;
        }
        """
        
        result = asyncio.run(self.async_test(
            ResourceMinifier.minify_js(test_js)
        ))
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertIn("reduction_percentage", result)
        self.assertGreater(result["reduction_percentage"], 0)
    
    def test_minify_css(self):
        """Teste la minification CSS"""
        test_css = """
        /* Commentaire CSS */
        body {
            font-family: Arial, sans-serif;
            font-size: 16px;
            color: #333333;
            margin: 0;
            padding: 0;
        }
        """
        
        result = asyncio.run(self.async_test(
            ResourceMinifier.minify_css(test_css)
        ))
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertIn("reduction_percentage", result)
        self.assertGreater(result["reduction_percentage"], 0)


class TestPerformanceMetricsAnalyzer(unittest.TestCase):
    """Tests pour la classe PerformanceMetricsAnalyzer"""
    
    def test_analyze_trend(self):
        """Teste l'analyse de tendance"""
        # Tendance à l'amélioration
        improving_metrics = [3.2, 3.0, 2.8, 2.7, 2.5]
        improving_result = PerformanceMetricsAnalyzer.analyze_trend(improving_metrics)
        
        self.assertEqual(improving_result["trend"], "decreasing")  # Décroissant = amélioration pour le temps
        self.assertGreater(improving_result["trend_strength"], 0.5)
        
        # Tendance à la dégradation
        worsening_metrics = [2.5, 2.7, 2.9, 3.2, 3.5]
        worsening_result = PerformanceMetricsAnalyzer.analyze_trend(worsening_metrics)
        
        self.assertEqual(worsening_result["trend"], "increasing")  # Croissant = dégradation pour le temps
        self.assertGreater(worsening_result["trend_strength"], 0.5)
    
    def test_detect_performance_regression(self):
        """Teste la détection de régression de performance"""
        baseline = {
            "page_load_time": 2.5,
            "time_to_first_byte": 0.4,
            "largest_contentful_paint": 1.8
        }
        
        # Cas de régression
        regression = {
            "page_load_time": 3.0,
            "time_to_first_byte": 0.6,
            "largest_contentful_paint": 2.2
        }
        
        regression_result = PerformanceMetricsAnalyzer.detect_performance_regression(regression, baseline)
        self.assertEqual(regression_result["has_regressions"], True)
        
        # Cas d'amélioration
        improvement = {
            "page_load_time": 2.0,
            "time_to_first_byte": 0.3,
            "largest_contentful_paint": 1.5
        }
        
        improvement_result = PerformanceMetricsAnalyzer.detect_performance_regression(improvement, baseline)
        self.assertEqual(improvement_result["has_improvements"], True)


if __name__ == '__main__':
    unittest.main()
