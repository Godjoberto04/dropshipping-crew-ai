#!/usr/bin/env python3
"""
Tests unitaires pour le module SEMrushAnalyzer.
"""

import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Import du module à tester
from data_sources.seo.semrush_analyzer import SEMrushAnalyzer

class TestSEMrushAnalyzer(unittest.TestCase):
    """Tests pour la classe SEMrushAnalyzer."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        # Création d'un répertoire temporaire pour le cache
        self.temp_dir = tempfile.mkdtemp()
        
        # Configuration de test
        self.test_api_key = "test_api_key"
        self.test_keyword = "écouteurs bluetooth"
        
        # Création de l'analyseur en mode simulation (pas d'API réelle)
        self.analyzer = SEMrushAnalyzer(
            api_key=None,  # Mode simulation
            cache_dir=self.temp_dir,
            rate_limit=10,
            daily_limit=1000
        )
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        # Suppression du répertoire temporaire
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Teste l'initialisation correcte de l'analyseur."""
        # Vérification que l'analyseur est en mode simulation sans clé API
        self.assertTrue(self.analyzer._simulation_mode)
        
        # Création d'un analyseur avec clé API
        analyzer_with_key = SEMrushAnalyzer(api_key=self.test_api_key)
        self.assertFalse(analyzer_with_key._simulation_mode)
    
    def test_cache_management(self):
        """Teste la gestion du cache."""
        # Données de test
        test_data = {"keyword": "test", "volume": 1000}
        cache_key = "test_cache_key"
        
        # Sauvegarde dans le cache
        self.analyzer._save_to_cache(cache_key, test_data)
        
        # Vérification que le fichier de cache existe
        cache_file = self.analyzer._get_cache_file(cache_key)
        self.assertTrue(os.path.exists(cache_file))
        
        # Chargement depuis le cache
        cached_data = self.analyzer._load_from_cache(cache_key)
        self.assertEqual(cached_data, test_data)
        
        # Test avec une clé inexistante
        self.assertIsNone(self.analyzer._load_from_cache("nonexistent_key"))
    
    def test_analyze_keyword(self):
        """Teste l'analyse d'un mot-clé simple."""
        # Analyse du mot-clé
        result = self.analyzer.analyze_keyword(self.test_keyword)
        
        # Vérification des champs obligatoires
        self.assertEqual(result['keyword'], self.test_keyword)
        self.assertIn('volume', result)
        self.assertIn('cpc', result)
        self.assertIn('difficulty', result)
        self.assertIn('competition', result)
        self.assertIn('competition_score', result)
        self.assertIn('opportunity_score', result)
        
        # Vérification des types de données
        self.assertIsInstance(result['volume'], int)
        self.assertIsInstance(result['cpc'], float)
        self.assertIsInstance(result['difficulty'], int)
        self.assertIsInstance(result['competition'], float)
        self.assertIsInstance(result['competition_score'], int)
        self.assertIsInstance(result['opportunity_score'], float)
        
        # Vérification des plages de valeurs
        self.assertGreaterEqual(result['volume'], 0)
        self.assertGreaterEqual(result['cpc'], 0)
        self.assertGreaterEqual(result['difficulty'], 0)
        self.assertLessEqual(result['difficulty'], 100)
        self.assertGreaterEqual(result['competition'], 0)
        self.assertLessEqual(result['competition'], 1)
        self.assertGreaterEqual(result['competition_score'], 0)
        self.assertLessEqual(result['competition_score'], 100)
        self.assertGreaterEqual(result['opportunity_score'], 0)
    
    def test_analyze_keywords(self):
        """Teste l'analyse de plusieurs mots-clés."""
        # Liste de mots-clés de test
        test_keywords = ["écouteurs bluetooth", "casque sans fil", "enceinte portable"]
        
        # Analyse des mots-clés
        results = self.analyzer.analyze_keywords(test_keywords)
        
        # Vérification que tous les mots-clés sont traités
        self.assertEqual(len(results), len(test_keywords))
        for keyword in test_keywords:
            self.assertIn(keyword, results)
            self.assertIn('volume', results[keyword])
            self.assertIn('difficulty', results[keyword])
    
    def test_get_keyword_suggestions(self):
        """Teste l'obtention de suggestions de mots-clés."""
        # Obtention de suggestions
        suggestions = self.analyzer.get_keyword_suggestions(self.test_keyword, limit=5)
        
        # Vérification du nombre de suggestions
        self.assertLessEqual(len(suggestions), 5)
        
        # Vérification des champs obligatoires pour chaque suggestion
        for suggestion in suggestions:
            self.assertIn('keyword', suggestion)
            self.assertIn('volume', suggestion)
            self.assertIn('difficulty', suggestion)
    
    def test_get_competitors(self):
        """Teste l'obtention des concurrents pour un mot-clé."""
        # Obtention des concurrents (en mode simulation)
        competitors = self.analyzer.get_competitors(self.test_keyword, limit=3)
        
        # Vérification du nombre de concurrents
        self.assertLessEqual(len(competitors), 3)
        
        # Vérification des champs obligatoires pour chaque concurrent
        for competitor in competitors:
            self.assertIn('domain', competitor)
            self.assertIn('visibility', competitor)
            self.assertIn('traffic', competitor)
            self.assertIn('position', competitor)
    
    def test_process_keyword_data(self):
        """Teste le traitement des données de mot-clé."""
        # Données brutes (format API SEMrush)
        raw_data = {
            'Ph': 'écouteurs bluetooth',
            'Nq': '5000',
            'Cp': '1.5',
            'Co': '0.75',
            'Nr': '2000000'
        }
        
        # Traitement des données
        processed = self.analyzer._process_keyword_data(raw_data)
        
        # Vérification des champs transformés
        self.assertEqual(processed['keyword'], 'écouteurs bluetooth')
        self.assertEqual(processed['volume'], 5000)
        self.assertEqual(processed['cpc'], 1.5)
        self.assertEqual(processed['competition'], 0.75)
        self.assertEqual(processed['competition_score'], 75)
        self.assertIn('difficulty', processed)
        self.assertIn('opportunity_score', processed)
    
    @patch('requests.get')
    def test_api_request_with_real_api(self, mock_get):
        """Teste la requête API avec une vraie clé API (simulée)."""
        # Configuration d'un analyseur avec une clé API
        analyzer = SEMrushAnalyzer(
            api_key=self.test_api_key,
            cache_dir=self.temp_dir
        )
        
        # Mock de la réponse de l'API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [{'Ph': 'test', 'Nq': '1000', 'Cp': '0.5', 'Co': '0.3', 'Nr': '100000'}]
        }
        mock_get.return_value = mock_response
        
        # Exécution de la requête
        params = {'phrase': 'test', 'database': 'fr'}
        result = analyzer._api_request(SEMrushAnalyzer.KEYWORD_OVERVIEW_ENDPOINT, params)
        
        # Vérification que la requête a été effectuée correctement
        mock_get.assert_called_once()
        call_args = mock_get.call_args[0][0]
        self.assertIn(SEMrushAnalyzer.API_URL, call_args)
        self.assertIn(SEMrushAnalyzer.KEYWORD_OVERVIEW_ENDPOINT, call_args)
        
        # Vérification que la clé API a été ajoutée aux paramètres
        self.assertEqual(mock_get.call_args[1]['params']['key'], self.test_api_key)
    
    def test_daily_limit_reset(self):
        """Teste la réinitialisation du compteur quotidien."""
        # Configuration initiale
        self.analyzer._daily_requests = 100
        
        # Modification de la date à hier
        import datetime
        yesterday = datetime.datetime.now().date() - datetime.timedelta(days=1)
        self.analyzer._daily_reset_date = yesterday
        
        # Vérification de la réinitialisation
        self.analyzer._reset_daily_counter()
        self.assertEqual(self.analyzer._daily_requests, 0)
    
    def test_error_handling(self):
        """Teste la gestion des erreurs lors de l'analyse."""
        # Test avec un mot-clé vide
        with self.assertRaises(ValueError):
            self.analyzer.analyze_keyword("")
        
        # Test avec une liste de mots-clés vide
        with self.assertRaises(ValueError):
            self.analyzer.analyze_keywords([])

if __name__ == '__main__':
    unittest.main()
