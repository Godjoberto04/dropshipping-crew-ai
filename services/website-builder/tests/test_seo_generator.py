import sys
import os
import unittest
import json
from unittest.mock import MagicMock, patch

# Ajout du chemin pour pouvoir importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.seo_generator import SEOMetaGenerator

class TestSEOMetaGenerator(unittest.TestCase):
    """Tests pour le générateur de métadonnées SEO"""
    
    def setUp(self):
        """Configuration des objets pour les tests"""
        self.seo_generator = SEOMetaGenerator(config={
            'shop_name': 'Test Dropshipping Store',
            'maxTitleLength': 60,
            'maxDescriptionLength': 160
        })
        
        # Exemple d'informations sur la boutique
        self.shop_info = {
            'name': 'Test Dropshipping Store',
            'domain': 'test-store.myshopify.com',
            'twitter_handle': '@teststoreshop'
        }
    
    def test_product_metadata_generation(self):
        """Test la génération de métadonnées pour un produit"""
        
        # Données d'exemple pour un produit
        product_data = {
            'type': 'product',
            'name': 'Écouteurs Bluetooth Pro',
            'description': 'Ces écouteurs bluetooth premium offrent une qualité sonore exceptionnelle et une autonomie de 24 heures.',
            'price': 89.99,
            'currency': 'EUR',
            'images': ['https://example.com/image1.jpg', 'https://example.com/image2.jpg'],
            'brand': 'TechSound',
            'features': ['Autonomie 24h', 'Suppression active du bruit', 'Résistant à l\'eau'],
            'benefits': ['Son cristallin', 'Confort optimal', 'Connexion stable']
        }
        
        # Générer les métadonnées
        metadata = self.seo_generator.generate_metadata(product_data, self.shop_info, 'electronics')
        
        # Vérifier que toutes les clés attendues sont présentes
        self.assertIn('title', metadata)
        self.assertIn('description', metadata)
        self.assertIn('canonical', metadata)
        self.assertIn('structuredData', metadata)
        self.assertIn('openGraph', metadata)
        self.assertIn('twitterCard', metadata)
        self.assertIn('keywords', metadata)
        
        # Vérifier que le titre contient le nom du produit et le nom de la boutique
        self.assertIn('Écouteurs Bluetooth Pro', metadata['title'])
        self.assertIn(self.shop_info['name'], metadata['title'])
        
        # Vérifier que la description contient le nom du produit
        self.assertIn('Écouteurs Bluetooth Pro', metadata['description'])
        
        # Vérifier que l'URL canonique est correcte
        self.assertEqual(f"https://{self.shop_info['domain']}/products/ecouteurs-bluetooth-pro", metadata['canonical'])
        
        # Vérifier les données structurées
        self.assertEqual(metadata['structuredData']['@type'], 'Product')
        self.assertEqual(metadata['structuredData']['name'], product_data['name'])
        
        # Vérifier les balises Open Graph
        self.assertEqual(metadata['openGraph']['og:title'], metadata['title'])
        self.assertEqual(metadata['openGraph']['og:type'], 'product')
        
        # Vérifier les balises Twitter Card
        self.assertEqual(metadata['twitterCard']['twitter:title'], metadata['title'])
        
        # Vérifier les mots-clés
        self.assertIsInstance(metadata['keywords'], list)
        self.assertTrue(len(metadata['keywords']) > 0)
    
    def test_collection_metadata_generation(self):
        """Test la génération de métadonnées pour une collection"""
        
        # Données d'exemple pour une collection
        collection_data = {
            'type': 'collection',
            'name': 'Accessoires Audio',
            'description': 'Découvrez notre sélection d\'accessoires audio de haute qualité.',
            'handle': 'accessoires-audio',
            'image': 'https://example.com/collection.jpg'
        }
        
        # Générer les métadonnées
        metadata = self.seo_generator.generate_metadata(collection_data, self.shop_info, 'electronics')
        
        # Vérifier que le titre et la description sont générés correctement
        self.assertIn('Accessoires Audio', metadata['title'])
        self.assertIn('Accessoires Audio', metadata['description'])
        
        # Vérifier que l'URL canonique est correcte
        self.assertEqual(f"https://{self.shop_info['domain']}/collections/accessoires-audio", metadata['canonical'])
        
        # Vérifier que les données structurées sont du bon type
        self.assertEqual(metadata['structuredData']['@type'], 'CollectionPage')
    
    def test_blog_metadata_generation(self):
        """Test la génération de métadonnées pour un article de blog"""
        
        # Données d'exemple pour un article de blog
        blog_data = {
            'type': 'blog',
            'name': 'Comment choisir les meilleurs écouteurs Bluetooth',
            'description': 'Guide complet pour choisir les écouteurs Bluetooth adaptés à vos besoins.',
            'content': 'Le choix des écouteurs Bluetooth peut s\'avérer complexe. Dans cet article, nous vous guidons à travers les critères essentiels pour faire le bon choix.',
            'author': 'Jean Dupont',
            'published_at': '2025-03-01T12:00:00Z',
            'blog_handle': 'tech-blog',
            'handle': 'comment-choisir-ecouteurs-bluetooth'
        }
        
        # Générer les métadonnées
        metadata = self.seo_generator.generate_metadata(blog_data, self.shop_info, 'electronics')
        
        # Vérifier que le titre et la description sont générés correctement
        self.assertIn('Comment choisir les meilleurs écouteurs Bluetooth', metadata['title'])
        self.assertIn('Guide complet', metadata['description'])
        
        # Vérifier que l'URL canonique est correcte
        self.assertEqual(f"https://{self.shop_info['domain']}/blogs/tech-blog/comment-choisir-ecouteurs-bluetooth", metadata['canonical'])
        
        # Vérifier que les données structurées sont du bon type
        self.assertEqual(metadata['structuredData']['@type'], 'BlogPosting')
        self.assertEqual(metadata['structuredData']['headline'], blog_data['name'])
        
        # Vérifier que les OpenGraph tags sont corrects pour un article
        self.assertEqual(metadata['openGraph']['og:type'], 'article')
    
    def test_page_metadata_generation(self):
        """Test la génération de métadonnées pour une page statique"""
        
        # Données d'exemple pour une page statique
        page_data = {
            'type': 'page',
            'name': 'À propos de nous',
            'content': 'Nous sommes une boutique spécialisée dans la vente d\'accessoires électroniques de haute qualité.',
            'handle': 'a-propos'
        }
        
        # Générer les métadonnées
        metadata = self.seo_generator.generate_metadata(page_data, self.shop_info, 'electronics')
        
        # Vérifier que le titre et la description sont générés correctement
        self.assertIn('À propos de nous', metadata['title'])
        self.assertIn('boutique spécialisée', metadata['description'])
        
        # Vérifier que l'URL canonique est correcte
        self.assertEqual(f"https://{self.shop_info['domain']}/pages/a-propos", metadata['canonical'])
        
        # Vérifier que les données structurées sont du bon type
        self.assertEqual(metadata['structuredData']['@type'], 'WebPage')
    
    def test_emotional_triggers(self):
        """Test que les déclencheurs émotionnels sont correctement sélectionnés par niche"""
        
        # Créer un produit simple
        product_data = {
            'type': 'product',
            'name': 'Produit Test',
            'description': 'Description du produit test'
        }
        
        # Tester avec différentes niches
        for niche in ['fashion', 'electronics', 'homeDecor', 'beauty', 'fitness']:
            metadata = self.seo_generator.generate_metadata(product_data, self.shop_info, niche)
            
            # Vérifier que le titre contient un déclencheur émotionnel approprié pour la niche
            any_trigger_present = False
            for trigger in self.seo_generator.emotional_triggers.get(niche, []):
                if trigger in metadata['title']:
                    any_trigger_present = True
                    break
            
            self.assertTrue(any_trigger_present, f"Aucun déclencheur émotionnel de la niche {niche} trouvé dans le titre")
    
    def test_generate_handle(self):
        """Test la génération de handle SEO-friendly"""
        # Test avec des caractères spéciaux et espaces
        self.assertEqual(self.seo_generator._generate_handle("Test Produit Génial ! @#"), "test-produit-genial")
        
        # Test avec des tirets multiples
        self.assertEqual(self.seo_generator._generate_handle("Test  -  Produit"), "test-produit")
        
        # Test avec des tirets au début et à la fin
        self.assertEqual(self.seo_generator._generate_handle("-Test Produit-"), "test-produit")
    
    def test_strip_html(self):
        """Test la suppression des balises HTML"""
        html = "<p>Ceci est un <strong>test</strong> avec des <a href='#'>balises</a> HTML.</p>"
        expected = "Ceci est un test avec des balises HTML."
        self.assertEqual(self.seo_generator._strip_html(html), expected)
        
        # Test avec des entités HTML
        html = "Test avec des entit&eacute;s HTML &amp; autres caractères"
        expected = "Test avec des entités HTML & autres caractères"
        self.assertEqual(self.seo_generator._strip_html(html), expected)

if __name__ == '__main__':
    unittest.main()
