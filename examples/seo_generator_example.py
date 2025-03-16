#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exemple d'utilisation du générateur de métadonnées SEO
======================================================

Cet exemple montre comment utiliser le générateur de métadonnées SEO de l'agent Website Builder
pour créer des balises meta optimisées pour différents types de pages d'une boutique e-commerce.

Le générateur prend en compte le type de page (produit, collection, page statique, article de blog),
la niche du produit et utilise des déclencheurs émotionnels pour rendre les titres et descriptions
plus attrayants.
"""

import os
import json
import sys
from pathlib import Path

# Ajouter le répertoire parent au chemin Python pour pouvoir importer le module
sys.path.append(str(Path(__file__).parent.parent))

try:
    from services.website_builder.tools.seo_generator import SEOMetaGenerator
except ImportError:
    print("Erreur: Impossible d'importer le module SEOMetaGenerator.")
    print("Vérifiez que vous exécutez ce script depuis le répertoire racine du projet.")
    print("Vous pouvez utiliser: python examples/seo_generator_example.py")
    sys.exit(1)

def main():
    """
    Fonction principale de l'exemple
    """
    print("=== Démonstration du générateur de métadonnées SEO ===\n")
    
    # Configuration personnalisée du générateur
    config = {
        'shop_name': 'TechStyle Shop',
        'maxTitleLength': 60,
        'maxDescriptionLength': 160,
        'includeBrand': True,
        'includePrice': True,
        'includeBenefits': True,
        'includeEmotionalTriggers': True,
        'maxKeywords': 10
    }
    
    # Informations sur la boutique
    shop_info = {
        'name': 'TechStyle Shop',
        'domain': 'techstyleshop.com',
        'twitter_handle': '@techstyleshop'
    }
    
    # Initialisation du générateur SEO
    print("Initialisation du générateur SEO avec la configuration:")
    print(json.dumps(config, indent=2))
    print()
    
    seo_generator = SEOMetaGenerator(config=config)
    
    # === EXEMPLE 1: Page Produit ===
    print("=== EXEMPLE 1: Page Produit ===")
    
    # Données du produit
    product_data = {
        'type': 'product',
        'name': 'Montre Connectée Pro',
        'description': 'Notre montre connectée haut de gamme avec suivi d\'activité, notifications et autonomie exceptionnelle.',
        'price': 129.99,
        'currency': 'EUR',
        'images': ['https://example.com/images/smartwatch-pro.jpg'],
        'brand': 'TechWear',
        'features': [
            'Écran AMOLED 1,5 pouces',
            'Étanche jusqu\'à 50m',
            'Autonomie 14 jours',
            'Suivi du sommeil',
            'GPS intégré'
        ],
        'benefits': [
            'Suivez votre activité physique quotidienne',
            'Restez connecté en permanence',
            'Batterie longue durée pour une utilisation sans contrainte'
        ],
        'tags': 'montre, connectée, sport, technologie',
        'handle': 'montre-connectee-pro',
        'availability': True
    }
    
    # Générer les métadonnées SEO
    print("Génération des métadonnées pour un produit dans la niche 'electronics'...")
    product_metadata = seo_generator.generate_metadata(
        page_data=product_data,
        shop_info=shop_info,
        niche='electronics'
    )
    
    # Afficher les résultats
    print("\nMétadonnées générées pour le produit:")
    print(f"Titre: {product_metadata['title']}")
    print(f"Description: {product_metadata['description']}")
    print(f"URL canonique: {product_metadata['canonical']}")
    print(f"Mots-clés: {', '.join(product_metadata['keywords'])}")
    print("\nBalises Open Graph:")
    for key, value in product_metadata['openGraph'].items():
        print(f"  {key}: {value}")
    print("\nBalises Twitter Card:")
    for key, value in product_metadata['twitterCard'].items():
        print(f"  {key}: {value}")
    
    # === EXEMPLE 2: Page de Collection ===
    print("\n\n=== EXEMPLE 2: Page de Collection ===")
    
    # Données de la collection
    collection_data = {
        'type': 'collection',
        'name': 'Montres Connectées',
        'title': 'Collection de Montres Connectées',
        'description': 'Découvrez notre gamme de montres connectées pour tous les usages, du sport à la vie quotidienne.',
        'images': ['https://example.com/images/smartwatches-collection.jpg'],
        'handle': 'montres-connectees',
        'products_count': 12
    }
    
    # Générer les métadonnées SEO
    print("Génération des métadonnées pour une collection dans la niche 'electronics'...")
    collection_metadata = seo_generator.generate_metadata(
        page_data=collection_data,
        shop_info=shop_info,
        niche='electronics'
    )
    
    # Afficher les résultats
    print("\nMétadonnées générées pour la collection:")
    print(f"Titre: {collection_metadata['title']}")
    print(f"Description: {collection_metadata['description']}")
    print(f"URL canonique: {collection_metadata['canonical']}")
    print(f"Mots-clés: {', '.join(collection_metadata['keywords'])}")
    
    # === EXEMPLE 3: Article de Blog ===
    print("\n\n=== EXEMPLE 3: Article de Blog ===")
    
    # Données de l'article de blog
    blog_data = {
        'type': 'blog',
        'name': 'Comment choisir sa montre connectée en 2025',
        'title': 'Guide complet pour choisir sa montre connectée en 2025',
        'content': 'Avec tant d\'options disponibles sur le marché, choisir la bonne montre connectée peut être difficile. Dans cet article, nous passerons en revue les critères essentiels pour faire le bon choix...',
        'author': 'Marie Dubois',
        'published_at': '2025-01-15T10:00:00Z',
        'updated_at': '2025-03-10T14:30:00Z',
        'tags': ['montre connectée', 'guide d\'achat', 'technologie', '2025'],
        'image': 'https://example.com/images/smartwatch-guide-2025.jpg',
        'handle': 'comment-choisir-montre-connectee-2025',
        'blog_handle': 'tech-blog'
    }
    
    # Générer les métadonnées SEO
    print("Génération des métadonnées pour un article de blog dans la niche 'electronics'...")
    blog_metadata = seo_generator.generate_metadata(
        page_data=blog_data,
        shop_info=shop_info,
        niche='electronics'
    )
    
    # Afficher les résultats
    print("\nMétadonnées générées pour l'article de blog:")
    print(f"Titre: {blog_metadata['title']}")
    print(f"Description: {blog_metadata['description']}")
    print(f"URL canonique: {blog_metadata['canonical']}")
    print(f"Mots-clés: {', '.join(blog_metadata['keywords'])}")
    
    # === UTILISATION DANS LE CONTEXTE SHOPIFY ===
    print("\n\n=== UTILISATION DANS LE CONTEXTE SHOPIFY ===")
    print("Pour utiliser ces métadonnées dans Shopify, vous pourriez procéder ainsi:")
    
    print("""
# Exemple d'intégration avec l'API Shopify
from shopify import Product

# Récupérer un produit
product = Product.find(1234567890)

# Mettre à jour les métadonnées SEO
product.metafields_global_title_tag = product_metadata['title']
product.metafields_global_description_tag = product_metadata['description']

# Ajouter les balises (tags)
if product.tags:
    existing_tags = product.tags.split(', ')
else:
    existing_tags = []

# Fusionner avec les nouveaux mots-clés
all_tags = existing_tags + product_metadata['keywords']
# Éliminer les doublons
unique_tags = list(set([tag.lower() for tag in all_tags]))
product.tags = ', '.join(unique_tags)

# Sauvegarder les modifications
product.save()
    """)
    
    # Fin de l'exemple
    print("\n=== Fin de la démonstration ===")
    print("Pour plus d'informations, consultez la documentation dans docs/seo_generator_guide.md")

if __name__ == "__main__":
    main()
