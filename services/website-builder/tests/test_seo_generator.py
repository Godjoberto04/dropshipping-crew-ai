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
        
        # Vérifier les données structurées
        self.assertEqual(metadata['structuredData']['@type'], 'CollectionPage')
        self.assertEqual(metadata['structuredData']['name'], collection_data['name'])
        
        # Vérifier que l'image est correctement incluse dans les métadonnées Open Graph
        self.assertEqual(metadata['openGraph']['og:image'], collection_data['image'])
    
    def test_page_metadata_generation(self):
        """Test la génération de métadonnées pour une page statique"""
        
        # Données d'exemple pour une page
        page_data = {
            'type': 'page',
            'name': 'À propos de nous',
            'title': 'À propos de Test Store',
            'content': 'Notre entreprise est spécialisée dans la vente de produits électroniques de haute qualité.',
            'handle': 'about'
        }
        
        # Générer les métadonnées
        metadata = self.seo_generator.generate_metadata(page_data, self.shop_info, 'general')
        
        # Vérifier que le titre et la description sont générés correctement
        self.assertIn('À propos', metadata['title'])
        self.assertIn(self.shop_info['name'], metadata['title'])
        self.assertIn('Notre entreprise', metadata['description'])
        
        # Vérifier que l'URL canonique est correcte
        self.assertEqual(f"https://{self.shop_info['domain']}/pages/about", metadata['canonical'])
        
        # Vérifier les données structurées
        self.assertEqual(metadata['structuredData']['@type'], 'WebPage')
    
    def test_blog_metadata_generation(self):
        """Test la génération de métadonnées pour un article de blog"""
        
        # Données d'exemple pour un article de blog
        blog_data = {
            'type': 'blog',
            'name': 'Les meilleures tendances tech de 2025',
            'content': 'Découvrez les dernières innovations technologiques qui transformeront notre quotidien en 2025.',
            'author': 'John Doe',
            'published_at': '2025-01-15T10:00:00Z',
            'updated_at': '2025-01-16T08:30:00Z',
            'handle': 'meilleures-tendances-tech-2025',
            'blog_handle': 'tech-news'
        }
        
        # Générer les métadonnées
        metadata = self.seo_generator.generate_metadata(blog_data, self.shop_info, 'electronics')
        
        # Vérifier que le titre et la description sont générés correctement
        self.assertIn('Les meilleures tendances tech', metadata['title'])
        self.assertIn('Blog', metadata['title'])
        self.assertIn('Découvrez les dernières innovations', metadata['description'])
        
        # Vérifier que l'URL canonique est correcte
        self.assertEqual(f"https://{self.shop_info['domain']}/blogs/tech-news/meilleures-tendances-tech-2025", metadata['canonical'])
        
        # Vérifier les données structurées
        self.assertEqual(metadata['structuredData']['@type'], 'BlogPosting')
        self.assertEqual(metadata['structuredData']['datePublished'], blog_data['published_at'])
        self.assertEqual(metadata['structuredData']['dateModified'], blog_data['updated_at'])
        
        # Vérifier les balises Open Graph spécifiques aux articles
        self.assertEqual(metadata['openGraph']['og:type'], 'article')
        self.assertEqual(metadata['openGraph']['article:published_time'], blog_data['published_at'])
    
    def test_title_length_limitation(self):
        """Test que le titre est correctement limité à la longueur maximale"""
        
        # Créer un produit avec un très long nom
        long_product_name = "Super Écouteurs Bluetooth Professionnels avec Réduction de Bruit Active et Autonomie Exceptionnelle de 48 Heures"
        product_data = {
            'type': 'product',
            'name': long_product_name,
            'description': 'Description du produit'
        }
        
        # Générer les métadonnées
        metadata = self.seo_generator.generate_metadata(product_data, self.shop_info, 'electronics')
        
        # Vérifier que le titre respecte la longueur maximale
        self.assertTrue(len(metadata['title']) <= self.seo_generator.config['maxTitleLength'])
        self.assertTrue(metadata['title'].endswith('...'))
    
    def test_description_length_limitation(self):
        """Test que la description est correctement limitée à la longueur maximale"""
        
        # Créer un produit avec une très longue description
        long_description = "Ces écouteurs bluetooth premium offrent une qualité sonore exceptionnelle et une autonomie de 24 heures. " * 10
        product_data = {
            'type': 'product',
            'name': 'Écouteurs Bluetooth',
            'description': long_description
        }
        
        # Générer les métadonnées
        metadata = self.seo_generator.generate_metadata(product_data, self.shop_info, 'electronics')
        
        # Vérifier que la description respecte la longueur maximale
        self.assertTrue(len(metadata['description']) <= self.seo_generator.config['maxDescriptionLength'])
        self.assertTrue(metadata['description'].endswith('...'))
    
    def test_emotional_trigger_selection(self):
        """Test la sélection des déclencheurs émotionnels selon la niche"""
        
        # Pour le test, on remplace la méthode aléatoire par une qui renvoie toujours le premier élément
        with patch('random.choice', lambda x: x[0]):
            product_data = {
                'type': 'product',
                'name': 'Produit Test',
                'description': 'Description du produit'
            }
            
            # Test avec différentes niches
            fashion_metadata = self.seo_generator.generate_metadata(product_data, self.shop_info, 'fashion')
            electronics_metadata = self.seo_generator.generate_metadata(product_data, self.shop_info, 'electronics')
            beauty_metadata = self.seo_generator.generate_metadata(product_data, self.shop_info, 'beauty')
            
            # Vérifier que les déclencheurs émotionnels sont différents selon la niche
            self.assertIn('Tendance', fashion_metadata['title'])
            self.assertIn('Innovant', electronics_metadata['title'])
            self.assertIn('Rajeunissant', beauty_metadata['title'])
    
    def test_handle_generation(self):
        """Test la génération de handle SEO-friendly"""
        
        # Tester avec différents textes
        test_cases = [
            ('Écouteurs Bluetooth', 'ecouteurs-bluetooth'),
            ('Produit avec & des caractères spéciaux !', 'produit-avec-des-caracteres-speciaux'),
            ('Très  Longue  Chaîne   Avec   Espaces', 'tres-longue-chaine-avec-espaces'),
            ('MAJUSCULES et minuscules', 'majuscules-et-minuscules')
        ]
        
        for input_text, expected_handle in test_cases:
            handle = self.seo_generator._generate_handle(input_text)
            self.assertEqual(handle, expected_handle)
    
    def test_keywords_generation(self):
        """Test la génération de mots-clés pertinents"""
        
        # Données d'exemple pour un produit
        product_data = {
            'type': 'product',
            'name': 'Écouteurs sans fil',
            'description': 'Écouteurs premium avec suppression de bruit',
            'brand': 'TechSound',
            'features': ['Bluetooth 5.0', 'Autonomie 24h', 'Résistant à l\'eau'],
            'benefits': ['Son cristallin', 'Confort optimal', 'Connexion stable']
        }
        
        # Générer les métadonnées
        metadata = self.seo_generator.generate_metadata(product_data, self.shop_info, 'electronics')
        
        # Vérifier que les mots-clés contiennent des éléments importants
        keywords = metadata['keywords']
        
        # Vérifier que le nom du produit est inclus
        self.assertTrue(any('Écouteurs sans fil' in kw for kw in keywords))
        
        # Vérifier que la marque est incluse
        self.assertTrue(any('TechSound' in kw for kw in keywords))
        
        # Vérifier que certaines caractéristiques et bénéfices sont inclus
        self.assertTrue(any('Bluetooth' in kw for kw in keywords) or 
                        any('Autonomie' in kw for kw in keywords) or
                        any('Son cristallin' in kw for kw in keywords))
        
        # Vérifier que le nombre de mots-clés est limité
        self.assertTrue(len(keywords) <= self.seo_generator.config['maxKeywords'])
    
    def test_strip_html(self):
        """Test le nettoyage des balises HTML"""
        
        # Texte HTML d'exemple
        html_text = "<p>Ceci est un <strong>paragraphe</strong> avec des <em>balises</em> HTML.</p><ul><li>Point 1</li><li>Point 2</li></ul>"
        
        # Résultat attendu
        expected_text = "Ceci est un paragraphe avec des balises HTML. Point 1 Point 2"
        
        # Tester la méthode de nettoyage
        cleaned_text = self.seo_generator._strip_html(html_text)
        
        # Vérifier que le texte est correctement nettoyé
        self.assertEqual(cleaned_text, expected_text)
    
    def test_price_valid_date(self):
        """Test la génération de la date de validité du prix"""
        
        # Générer une date de validité
        price_valid_date = self.seo_generator._generate_price_valid_date()
        
        # Vérifier le format de la date (YYYY-MM-DD)
        self.assertRegex(price_valid_date, r'^\d{4}-\d{2}-\d{2}$')
        
        # La date doit être dans le futur
        import datetime
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        self.assertGreater(price_valid_date, today)

if __name__ == '__main__':
    unittest.main()
