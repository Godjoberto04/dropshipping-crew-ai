# Guide Utilisateur: Générateur de Métadonnées SEO

Ce guide détaille l'utilisation et les fonctionnalités du générateur de métadonnées SEO intégré à l'agent Website Builder du projet Dropshipping Crew AI.

## Vue d'ensemble

Le générateur de métadonnées SEO est un module intelligent qui crée automatiquement des balises meta optimisées pour différents types de pages d'une boutique e-commerce. Il prend en compte le type de contenu, la niche du produit, et utilise des éléments persuasifs adaptés pour maximiser l'impact SEO et social.

## Fonctionnalités principales

- Génération de titres et méta-descriptions optimisés pour le SEO
- Création de données structurées schema.org adaptées au type de contenu
- Génération de balises Open Graph pour le partage sur réseaux sociaux
- Génération de balises Twitter Card pour l'affichage sur Twitter
- Sélection intelligente de mots-clés basés sur la niche et le contenu
- Adaptation du contenu généré au type de page (produit, collection, blog, page statique)
- Utilisation de déclencheurs émotionnels spécifiques à la niche

## Types de pages supportés

Le générateur prend en charge les types de pages suivants:

1. **Produit** - Pages de produits individuels
2. **Collection** - Pages de catégories ou collections de produits
3. **Page** - Pages statiques (À propos, Contact, etc.)
4. **Blog** - Articles de blog et contenus éditoriaux

## Installation

Le module est déjà intégré à l'agent Website Builder. Il n'est pas nécessaire de l'installer séparément.

## Configuration

Le générateur peut être personnalisé via un dictionnaire de configuration lors de son initialisation:

```python
from services.website-builder.tools.seo_generator import SEOMetaGenerator

# Configuration personnalisée
config = {
    'shop_name': 'Ma Boutique',
    'maxTitleLength': 60,           # Longueur maximale des titres
    'maxDescriptionLength': 160,    # Longueur maximale des descriptions
    'includeBrand': True,           # Inclure la marque dans les métadonnées
    'includePrice': False,          # Inclure le prix dans les titres
    'includeBenefits': True,        # Inclure les bénéfices produit
    'includeEmotionalTriggers': True, # Utiliser des déclencheurs émotionnels
    'maxKeywords': 10               # Nombre maximum de mots-clés
}

# Initialisation avec configuration personnalisée
seo_generator = SEOMetaGenerator(config=config)
```

## Utilisation de base

### Génération de métadonnées pour un produit

```python
# Informations sur la boutique
shop_info = {
    'name': 'Ma Boutique',
    'domain': 'ma-boutique.com',
    'twitter_handle': '@maboutique'
}

# Données du produit
product_data = {
    'type': 'product',
    'name': 'Montre Connectée',
    'description': 'Une montre intelligente avec suivi d\'activité et notifications.',
    'price': 99.99,
    'currency': 'EUR',
    'images': ['https://example.com/montre.jpg'],
    'features': ['Écran tactile', 'Étanche', 'Batterie longue durée'],
    'benefits': ['Suivez votre activité quotidienne', 'Restez connecté en permanence'],
    'brand': 'TechWear'
}

# Générer les métadonnées SEO
metadata = seo_generator.generate_metadata(
    page_data=product_data,
    shop_info=shop_info,
    niche='electronics'
)

# Utiliser les métadonnées générées
print(f"Titre SEO: {metadata['title']}")
print(f"Description: {metadata['description']}")
print(f"URL canonique: {metadata['canonical']}")
```

### Génération de métadonnées pour une collection

```python
# Données de la collection
collection_data = {
    'type': 'collection',
    'name': 'Montres Connectées',
    'description': 'Notre collection de montres connectées pour tous les usages.',
    'images': ['https://example.com/collection-montres.jpg'],
    'products_count': 12
}

# Générer les métadonnées SEO
metadata = seo_generator.generate_metadata(
    page_data=collection_data,
    shop_info=shop_info,
    niche='electronics'
)
```

### Génération de métadonnées pour une page statique

```python
# Données de la page
page_data = {
    'type': 'page',
    'name': 'À propos',
    'content': 'Notre boutique propose les meilleurs produits électroniques...',
    'handle': 'about'
}

# Générer les métadonnées SEO
metadata = seo_generator.generate_metadata(
    page_data=page_data,
    shop_info=shop_info,
    niche='electronics'
)
```

## Intégration avec l'API

Le générateur SEO peut être utilisé via l'API centrale du projet. Voici un exemple de requête:

```python
# Exemple de requête API pour générer des métadonnées SEO
api_payload = {
    "agent": "website-builder",
    "action": "generate_seo",
    "params": {
        "page_data": {
            "type": "product",
            "name": "Écouteurs Bluetooth",
            "description": "Écouteurs sans fil avec annulation de bruit active.",
            "price": 129.99,
            "currency": "EUR",
            "features": ["Son Hi-Fi", "Annulation de bruit", "30h d'autonomie"],
            "niche": "electronics"
        }
    }
}

# La requête renvoie un task_id qui peut être utilisé pour suivre l'avancement
task_response = api_client.submit_task(api_payload)
task_id = task_response.get("task_id")

# Vérifier le résultat plus tard
task_result = api_client.get_task_result(task_id)
```

## Structure des métadonnées générées

Le générateur produit un dictionnaire contenant les éléments suivants:

```python
{
    "title": "Innovant Écouteurs Bluetooth | Ma Boutique",
    "description": "Découvrez nos innovants Écouteurs Bluetooth. Son Hi-Fi et 30h d'autonomie. Livraison rapide, paiement sécurisé, satisfaction garantie !",
    "canonical": "https://ma-boutique.com/products/ecouteurs-bluetooth",
    "structuredData": {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "Écouteurs Bluetooth",
        "description": "Écouteurs sans fil avec annulation de bruit active.",
        "offers": {
            "@type": "Offer",
            "price": 129.99,
            "priceCurrency": "EUR",
            "availability": "https://schema.org/InStock"
        }
        # Plus de données structurées...
    },
    "openGraph": {
        "og:title": "Innovant Écouteurs Bluetooth | Ma Boutique",
        "og:description": "Découvrez nos innovants Écouteurs Bluetooth. Son Hi-Fi et 30h d'autonomie. Livraison rapide, paiement sécurisé, satisfaction garantie !",
        "og:type": "product",
        "og:url": "https://ma-boutique.com/products/ecouteurs-bluetooth",
        "og:image": "https://example.com/ecouteurs.jpg",
        "product:price:amount": "129.99",
        "product:price:currency": "EUR"
    },
    "twitterCard": {
        "twitter:card": "summary_large_image",
        "twitter:title": "Innovant Écouteurs Bluetooth | Ma Boutique",
        "twitter:description": "Découvrez nos innovants Écouteurs Bluetooth. Son Hi-Fi et 30h d'autonomie. Livraison rapide, paiement sécurisé, satisfaction garantie !",
        "twitter:image": "https://example.com/ecouteurs.jpg",
        "twitter:site": "@maboutique",
        "twitter:label1": "Prix",
        "twitter:data1": "129.99 EUR"
    },
    "keywords": [
        "Écouteurs Bluetooth",
        "Ma Boutique",
        "Son Hi-Fi",
        "Annulation de bruit",
        "30h d'autonomie",
        "électronique",
        "tech",
        "gadget",
        "innovation",
        "connecté"
    ]
}
```

## Déclencheurs émotionnels par niche

Le générateur utilise des déclencheurs émotionnels adaptés à chaque niche pour rendre les titres et descriptions plus attrayants:

| Niche | Déclencheurs émotionnels |
|-------|--------------------------|
| Mode | Tendance, Élégant, Stylé, Luxueux, Incontournable |
| Électronique | Innovant, Puissant, Intelligent, High-Tech, Performant |
| Décoration | Élégant, Unique, Cosy, Moderne, Intemporel |
| Beauté | Rajeunissant, Naturel, Efficace, Professionnel, Revitalisant |
| Fitness | Performant, Efficace, Professionnel, Révolutionnaire, Énergisant |

## Tests

Pour tester le générateur de métadonnées SEO:

```bash
cd services/website-builder
python -m unittest tests.test_seo_generator
```

## Bonnes pratiques

1. **Fournissez des données détaillées** - Plus vous fournissez d'informations dans les données de page, meilleure sera la qualité des métadonnées générées
2. **Spécifiez la niche correcte** - La niche influence les déclencheurs émotionnels et mots-clés utilisés
3. **Incluez les avantages produits** - Les bénéfices du produit sont utilisés dans les descriptions et améliorent la pertinence
4. **Ajoutez des caractéristiques** - Les caractéristiques techniques sont utiles pour les mots-clés et données structurées
5. **Personnalisez la configuration** - Adaptez les paramètres du générateur selon vos besoins spécifiques

## Limites actuelles

- Le générateur ne prend pas encore en compte l'analyse concurrentielle pour les mots-clés
- Les traductions multilingues ne sont pas encore supportées
- L'analyse de pertinence des mots-clés est basique et pourrait être améliorée
- Les données structurées générées pourraient être étendues pour plus de types de contenu

## Dépannage

### Les métadonnées ne s'affichent pas dans la boutique

Vérifiez que:
- Les métadonnées sont correctement associées aux objets Shopify (produits, collections, etc.)
- Les metafields globaux sont activés dans votre thème Shopify
- Le thème affiche correctement les balises meta dans le header

### Caractères spéciaux incorrects

Si vous rencontrez des problèmes d'encodage avec les caractères spéciaux:
- Assurez-vous que toutes les chaînes de caractères sont en UTF-8
- Vérifiez que le thème gère correctement l'encodage des métadonnées

## Ressources additionnelles

- [Documentation de l'API Shopify pour les metafields](https://shopify.dev/docs/admin-api/rest/reference/metafield)
- [Guide SEO de Shopify](https://help.shopify.com/en/manual/promoting-marketing/seo)
- [Guide des données structurées schema.org](https://schema.org/docs/gs.html)
