# Guide du générateur de métadonnées SEO

## Introduction

Le générateur de métadonnées SEO est un composant du Website Builder qui permet de générer automatiquement des balises meta optimisées pour les différents types de pages d'une boutique de dropshipping. Ce module génère des métadonnées SEO basées sur les données de la page, la niche, et les meilleures pratiques de référencement pour les sites e-commerce.

## Fonctionnalités

Le générateur de métadonnées SEO offre les fonctionnalités suivantes :

1. **Génération de métadonnées optimisées** pour différents types de pages :
   - Pages de produits
   - Pages de collections
   - Pages statiques (À propos, Contact, etc.)
   - Articles de blog

2. **Optimisation contextuelle** en fonction de la niche de la boutique, avec des déclencheurs émotionnels spécifiques pour :
   - Mode (Fashion)
   - Électronique
   - Décoration d'intérieur
   - Beauté
   - Fitness

3. **Génération complète de toutes les balises SEO essentielles** :
   - Titre de page (`<title>`)
   - Description meta (`<meta name="description">`)
   - URL canonique (`<link rel="canonical">`)
   - Balises Open Graph pour le partage social
   - Balises Twitter Card
   - Données structurées Schema.org (JSON-LD)
   - Mots-clés pertinents

4. **Personnalisation avancée** via des configurations flexibles pour adapter la génération selon vos besoins

## Intégration dans le Website Builder

Le générateur de métadonnées SEO est intégré au Website Builder et est utilisé automatiquement lors de :

1. **La configuration initiale de la boutique** pour optimiser la page d'accueil
2. **L'ajout de nouveaux produits** pour générer des métadonnées optimisées pour les fiches produits
3. **La création de collections** pour optimiser les pages de catégories
4. **La génération de contenu** pour les pages statiques et les articles de blog

## Utilisation via l'API

Vous pouvez également utiliser directement le générateur de métadonnées SEO via l'API du Website Builder :

```bash
# Générer des métadonnées SEO pour une page
curl -X POST "http://votre-serveur:8000/agents/website-builder/action" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "generate_seo",
    "page_data": {
      "type": "product",
      "name": "Écouteurs Bluetooth Pro",
      "description": "Ces écouteurs bluetooth premium offrent une qualité sonore exceptionnelle et une autonomie de 24 heures.",
      "price": 89.99,
      "currency": "EUR",
      "images": ["https://example.com/image1.jpg"],
      "brand": "TechSound",
      "features": ["Autonomie 24h", "Suppression active du bruit", "Résistant à l\'eau"],
      "benefits": ["Son cristallin", "Confort optimal", "Connexion stable"]
    },
    "niche": "electronics"
  }'
```

## Exemples de métadonnées générées

### Exemple pour une page produit

```json
{
  "title": "Innovant Écouteurs Bluetooth Pro | Ma Boutique",
  "description": "Découvrez notre innovant écouteurs bluetooth pro. Son cristallin et confort optimal. Livraison rapide, paiement sécurisé, satisfaction garantie !",
  "canonical": "https://ma-boutique.myshopify.com/products/ecouteurs-bluetooth-pro",
  "keywords": ["électronique", "tech", "gadget", "innovation", "connecté", "Écouteurs Bluetooth Pro", "TechSound", "Son cristallin"],
  "structuredData": {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "Écouteurs Bluetooth Pro",
    "description": "Ces écouteurs bluetooth premium offrent une qualité sonore exceptionnelle et une autonomie de 24 heures.",
    "brand": {
      "@type": "Brand",
      "name": "TechSound"
    },
    "offers": {
      "@type": "Offer",
      "price": 89.99,
      "priceCurrency": "EUR",
      "availability": "https://schema.org/InStock"
    }
  },
  "openGraph": {
    "og:title": "Innovant Écouteurs Bluetooth Pro | Ma Boutique",
    "og:description": "Découvrez notre innovant écouteurs bluetooth pro. Son cristallin et confort optimal. Livraison rapide, paiement sécurisé, satisfaction garantie !",
    "og:type": "product",
    "og:url": "https://ma-boutique.myshopify.com/products/ecouteurs-bluetooth-pro",
    "og:image": "https://example.com/image1.jpg",
    "og:site_name": "Ma Boutique",
    "product:price:amount": "89.99",
    "product:price:currency": "EUR"
  },
  "twitterCard": {
    "twitter:card": "summary_large_image",
    "twitter:title": "Innovant Écouteurs Bluetooth Pro | Ma Boutique",
    "twitter:description": "Découvrez notre innovant écouteurs bluetooth pro. Son cristallin et confort optimal. Livraison rapide, paiement sécurisé, satisfaction garantie !",
    "twitter:image": "https://example.com/image1.jpg"
  }
}
```

## Personnalisation

Vous pouvez personnaliser le comportement du générateur de métadonnées SEO en modifiant sa configuration :

```python
from tools.seo_generator import SEOMetaGenerator

# Initialisation avec configuration personnalisée
seo_generator = SEOMetaGenerator(config={
    'shop_name': 'Ma Boutique Personnalisée',
    'maxTitleLength': 70,           # Longueur maximale du titre
    'maxDescriptionLength': 155,    # Longueur maximale de la description
    'includeBrand': True,           # Inclure la marque dans les métadonnées
    'includePrice': True,           # Inclure le prix dans le titre
    'includeBenefits': True,        # Inclure les avantages dans le titre/description
    'includeEmotionalTriggers': True,  # Utiliser des déclencheurs émotionnels
    'maxKeywords': 8                # Nombre maximum de mots-clés
})
```

## Bonnes pratiques pour de meilleurs résultats

Pour obtenir les meilleurs résultats avec le générateur de métadonnées SEO, suivez ces conseils :

1. **Fournissez toujours une niche précise** pour votre boutique ou votre produit afin d'obtenir des métadonnées contextuellement pertinentes

2. **Enrichissez vos données produits** avec :
   - Des descriptions détaillées
   - Une liste de caractéristiques (features)
   - Une liste d'avantages (benefits)
   - Des images de qualité
   - La marque du produit

3. **Structurez correctement vos données** en spécifiant clairement le type de page (product, collection, page, blog)

4. **Complétez les informations de votre boutique** pour des résultats plus pertinents :
   - Nom de la boutique
   - Domaine
   - Identifiants de réseaux sociaux

## Conclusion

Le générateur de métadonnées SEO est un outil puissant pour optimiser automatiquement le référencement de votre boutique de dropshipping. En générant des métadonnées optimisées pour chaque page, il améliore la visibilité de votre site dans les moteurs de recherche et sur les réseaux sociaux, ce qui peut conduire à plus de trafic organique et, potentiellement, à plus de ventes.
