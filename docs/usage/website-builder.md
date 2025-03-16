# Guide d'utilisation de l'agent Website Builder

L'agent Website Builder est responsable de la création et de la gestion de votre boutique Shopify. Il automatise la configuration du site, l'organisation des produits, et l'optimisation de l'expérience utilisateur pour maximiser les conversions.

## Table des matières
1. [Fonctionnalités principales](#fonctionnalités-principales)
2. [Architecture et modules](#architecture-et-modules)
3. [Utilisation via l'API](#utilisation-via-lapi)
4. [Exemples de code](#exemples-de-code)
5. [Cas d'utilisation](#cas-dutilisation)
6. [Personnalisation avancée](#personnalisation-avancée)
7. [Limitations connues](#limitations-connues)
8. [Dépannage](#dépannage)

## Fonctionnalités principales

L'agent Website Builder offre les fonctionnalités suivantes:

### Configuration de boutique
- Création et configuration initiale d'une boutique Shopify
- Paramétrage des informations générales et des préférences
- Configuration des modes de paiement et d'expédition
- Mise en place des taxes et des politiques

### Gestion de thème
- Sélection et installation de thèmes optimisés pour le dropshipping
- Personnalisation des couleurs, polices et éléments visuels
- Configuration des sections et du layout
- Adaptation pour les appareils mobiles

### Organisation du catalogue
- Création et gestion des collections de produits
- Organisation de la navigation et de la structure du site
- Optimisation de la présentation des produits
- Configuration des produits complémentaires et des ventes croisées

### Optimisation de conversion
- Implémentation des éléments UI optimisés pour la conversion
- Configuration des pages de paiement
- Mise en place des éléments de confiance
- Optimisation des appels à l'action

## Architecture et modules

L'agent Website Builder est divisé en plusieurs modules spécialisés:

### ShopifyManager
Interface principale avec l'API Shopify pour toutes les opérations de boutique.

### ThemeManager
Module dédié à la gestion et personnalisation des thèmes.

### NavigationBuilder
Responsable de la structure de navigation et de l'organisation des menus.

### ProductOrganizer
Gère l'organisation des produits en collections et catégories.

### SEOOptimizer
S'occupe de l'optimisation SEO technique des pages.

## Utilisation via l'API

L'agent Website Builder expose ses fonctionnalités via l'API REST centrale du système.

### Endpoints principaux

#### Configuration de la boutique
```
POST /api/v1/agents/website-builder/store/configure
```

Paramètres:
```json
{
  "store_name": "TechGadgetsPro",
  "contact_email": "support@techgadgetspro.com",
  "currency": "USD",
  "timezone": "America/New_York",
  "address": {
    "company": "Tech Gadgets Pro LLC",
    "address1": "123 Tech Street",
    "city": "San Francisco",
    "province": "CA",
    "zip": "94103",
    "country_code": "US",
    "phone": "+1 (555) 123-4567"
  },
  "shipping_zones": [
    {
      "name": "Domestic",
      "countries": ["US"],
      "price": 4.99,
      "free_above": 50.00
    },
    {
      "name": "International",
      "countries": ["*"],
      "price": 14.99,
      "free_above": 100.00
    }
  ],
  "payment_gateways": ["shopify_payments", "paypal"]
}
```

Réponse:
```json
{
  "status": "success",
  "store_id": "store_12345",
  "myshopify_domain": "techgadgetspro.myshopify.com",
  "configuration": {
    "store_name": "TechGadgetsPro",
    "contact_email": "support@techgadgetspro.com",
    "currency": "USD",
    "timezone": "America/New_York",
    "configured_sections": [
      "general",
      "address",
      "shipping",
      "payments"
    ]
  }
}
```

#### Gestion des thèmes
```
POST /api/v1/agents/website-builder/theme/install
```

Paramètres:
```json
{
  "theme_id": "123456789",
  "customize": {
    "colors": {
      "primary": "#3498db",
      "secondary": "#2ecc71",
      "accent": "#e74c3c",
      "background": "#f9f9f9",
      "text": "#333333"
    },
    "typography": {
      "heading_font": "Montserrat",
      "body_font": "Open Sans",
      "base_size": "16px"
    },
    "layout": {
      "logo_width": 140,
      "content_width": 1200,
      "show_announcement_bar": true
    }
  }
}
```

Réponse:
```json
{
  "status": "success",
  "theme_id": "installed_theme_123456",
  "published": true,
  "preview_url": "https://techgadgetspro.myshopify.com/?preview_theme_id=installed_theme_123456",
  "customization_status": "completed",
  "sections_configured": ["header", "footer", "home-page", "collection-page", "product-page"]
}
```

#### Organisation des collections
```
POST /api/v1/agents/website-builder/collections/create
```

Paramètres:
```json
{
  "collection": {
    "title": "Summer Essentials",
    "description": "Beat the heat with our curated selection of summer gadgets and accessories.",
    "image_url": "https://example.com/summer-collection.jpg",
    "smart_collection": true,
    "rules": [
      {
        "column": "tag",
        "relation": "equals",
        "condition": "summer"
      },
      {
        "column": "type",
        "relation": "equals",
        "condition": "Outdoor"
      }
    ],
    "sort_order": "best-selling",
    "published": true,
    "seo": {
      "title": "Summer Tech Essentials | TechGadgetsPro",
      "description": "Discover our collection of essential tech gadgets for summer. Stay cool and connected!",
      "url_handle": "summer-essentials"
    }
  }
}
```

Réponse:
```json
{
  "status": "success",
  "collection_id": "gid://shopify/Collection/12345678",
  "handle": "summer-essentials",
  "url": "https://techgadgetspro.myshopify.com/collections/summer-essentials",
  "product_count": 0,
  "published_at": "2025-03-16T14:02:45Z"
}
```

#### Navigation et menus
```
POST /api/v1/agents/website-builder/navigation/update
```

Paramètres:
```json
{
  "main_menu": [
    {
      "title": "Home",
      "url": "/"
    },
    {
      "title": "Collections",
      "url": "/collections",
      "child_links": [
        {
          "title": "New Arrivals",
          "url": "/collections/new-arrivals"
        },
        {
          "title": "Summer Essentials",
          "url": "/collections/summer-essentials"
        },
        {
          "title": "Tech Gadgets",
          "url": "/collections/tech-gadgets"
        }
      ]
    },
    {
      "title": "About Us",
      "url": "/pages/about-us"
    },
    {
      "title": "Contact",
      "url": "/pages/contact"
    }
  ],
  "footer_menu": [
    {
      "title": "Shop",
      "child_links": [
        {
          "title": "All Products",
          "url": "/collections/all"
        },
        {
          "title": "Best Sellers",
          "url": "/collections/best-sellers"
        }
      ]
    },
    {
      "title": "Information",
      "child_links": [
        {
          "title": "Shipping Policy",
          "url": "/policies/shipping-policy"
        },
        {
          "title": "Refund Policy",
          "url": "/policies/refund-policy"
        },
        {
          "title": "Privacy Policy",
          "url": "/policies/privacy-policy"
        }
      ]
    }
  ]
}
```

Réponse:
```json
{
  "status": "success",
  "main_menu_id": "gid://shopify/Menu/11111",
  "footer_menu_id": "gid://shopify/Menu/22222",
  "updated_at": "2025-03-16T14:03:15Z"
}
```

## Exemples de code

### Exemple Python

Voici comment utiliser l'API avec Python:

```python
import requests
import json

BASE_URL = "http://your-server-ip/api/v1"
API_KEY = "your_api_key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Configuration de la boutique
def configure_store(store_name, contact_email, currency="USD"):
    endpoint = f"{BASE_URL}/agents/website-builder/store/configure"
    
    payload = {
        "store_name": store_name,
        "contact_email": contact_email,
        "currency": currency,
        "timezone": "America/New_York",
        "address": {
            "company": f"{store_name} LLC",
            "address1": "123 Main Street",
            "city": "New York",
            "province": "NY",
            "zip": "10001",
            "country_code": "US",
            "phone": "+1 (555) 123-4567"
        },
        "shipping_zones": [
            {
                "name": "Domestic",
                "countries": ["US"],
                "price": 4.99,
                "free_above": 50.00
            },
            {
                "name": "International",
                "countries": ["*"],
                "price": 14.99,
                "free_above": 100.00
            }
        ],
        "payment_gateways": ["shopify_payments", "paypal"]
    }
    
    response = requests.post(endpoint, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Installation d'un thème
def install_theme(theme_id, primary_color="#3498db", secondary_color="#2ecc71"):
    endpoint = f"{BASE_URL}/agents/website-builder/theme/install"
    
    payload = {
        "theme_id": theme_id,
        "customize": {
            "colors": {
                "primary": primary_color,
                "secondary": secondary_color,
                "accent": "#e74c3c",
                "background": "#f9f9f9",
                "text": "#333333"
            },
            "typography": {
                "heading_font": "Montserrat",
                "body_font": "Open Sans",
                "base_size": "16px"
            },
            "layout": {
                "logo_width": 140,
                "content_width": 1200,
                "show_announcement_bar": True
            }
        }
    }
    
    response = requests.post(endpoint, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Création d'une collection
def create_collection(title, description, tags=None, product_type=None):
    endpoint = f"{BASE_URL}/agents/website-builder/collections/create"
    
    rules = []
    if tags:
        rules.append({
            "column": "tag",
            "relation": "equals",
            "condition": tags
        })
    
    if product_type:
        rules.append({
            "column": "type",
            "relation": "equals",
            "condition": product_type
        })
    
    payload = {
        "collection": {
            "title": title,
            "description": description,
            "smart_collection": len(rules) > 0,
            "rules": rules,
            "sort_order": "best-selling",
            "published": True,
            "seo": {
                "title": f"{title} | Your Store Name",
                "description": description[:160],
                "url_handle": title.lower().replace(" ", "-")
            }
        }
    }
    
    response = requests.post(endpoint, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Utilisation des fonctions
store_config = configure_store("TechGadgetsPro", "support@techgadgetspro.com")
theme_install = install_theme("123456789")
summer_collection = create_collection(
    "Summer Essentials", 
    "Beat the heat with our curated selection of summer gadgets and accessories.",
    tags="summer",
    product_type="Outdoor"
)

print(json.dumps(store_config, indent=2))
print(json.dumps(theme_install, indent=2))
print(json.dumps(summer_collection, indent=2))
```

### Exemple avec Curl

```bash
# Configuration de la boutique
curl -X POST "http://your-server-ip/api/v1/agents/website-builder/store/configure" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "TechGadgetsPro",
    "contact_email": "support@techgadgetspro.com",
    "currency": "USD",
    "timezone": "America/New_York",
    "address": {
      "company": "Tech Gadgets Pro LLC",
      "address1": "123 Tech Street",
      "city": "San Francisco",
      "province": "CA",
      "zip": "94103",
      "country_code": "US",
      "phone": "+1 (555) 123-4567"
    },
    "shipping_zones": [
      {
        "name": "Domestic",
        "countries": ["US"],
        "price": 4.99,
        "free_above": 50.00
      },
      {
        "name": "International",
        "countries": ["*"],
        "price": 14.99,
        "free_above": 100.00
      }
    ],
    "payment_gateways": ["shopify_payments", "paypal"]
  }'

# Installation d'un thème
curl -X POST "http://your-server-ip/api/v1/agents/website-builder/theme/install" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "theme_id": "123456789",
    "customize": {
      "colors": {
        "primary": "#3498db",
        "secondary": "#2ecc71",
        "accent": "#e74c3c",
        "background": "#f9f9f9",
        "text": "#333333"
      },
      "typography": {
        "heading_font": "Montserrat",
        "body_font": "Open Sans",
        "base_size": "16px"
      },
      "layout": {
        "logo_width": 140,
        "content_width": 1200,
        "show_announcement_bar": true
      }
    }
  }'
```

## Cas d'utilisation

Voici quelques cas d'utilisation typiques de l'agent Website Builder:

### 1. Configuration initiale d'une boutique

Le flux de travail recommandé pour configurer une nouvelle boutique:

1. Obtenir les identifiants de développement Shopify
2. Configurer les informations de base de la boutique avec `/store/configure`
3. Installer et personnaliser un thème approprié à votre niche avec `/theme/install`
4. Configurer les modalités de paiement et d'expédition
5. Créer les pages statiques (À propos, Contact, FAQ)
6. Configurer la navigation principale et le footer

### 2. Organisation du catalogue produit

Pour une structure de catalogue efficace:

1. Analyser les produits avec l'agent Data Analyzer pour identifier les catégories naturelles
2. Créer des collections manuelles pour les produits phares et promotionnels
3. Créer des collections intelligentes basées sur les tags et types de produits
4. Organiser la navigation pour mettre en avant les collections les plus rentables
5. Configurer la page d'accueil pour présenter les collections principales

### 3. Optimisation SEO

Pour optimiser le référencement de la boutique:

1. Configurer les méta-données SEO pour chaque page avec `/seo/configure`
2. Générer une structure URL propre et lisible
3. Mettre en place le sitemap et les balises canoniques
4. Configurer les redirections pour les URL obsolètes
5. Optimiser la vitesse de chargement du site

### 4. Mise en place de campagnes promotionnelles

Pour lancer une nouvelle campagne:

1. Créer une collection dédiée à la campagne
2. Configurer la bannière promotionnelle via `/theme/update-section`
3. Ajouter la campagne dans la navigation temporairement
4. Configurer les remises et codes promotionnels
5. Mettre à jour la page d'accueil pour mettre en avant la campagne

## Personnalisation avancée

### Personnalisation des templates Shopify

Pour une personnalisation plus poussée des templates, vous pouvez utiliser l'endpoint:

```
POST /api/v1/agents/website-builder/theme/template/update
```

Avec cette fonctionnalité, vous pouvez:
- Modifier les templates de produit
- Personnaliser les templates de collection
- Adapter les templates de panier et checkout
- Modifier les sections de la page d'accueil

Exemple de modification d'un template produit:

```json
{
  "template": "product",
  "sections": {
    "main": {
      "type": "product-template",
      "settings": {
        "show_quantity_selector": true,
        "show_vendor": true,
        "show_sku": true,
        "show_taxes_included": true,
        "show_product_rating": true,
        "enable_image_zoom": true,
        "enable_video_looping": false
      }
    },
    "product-recommendations": {
      "type": "product-recommendations",
      "settings": {
        "heading": "You may also like",
        "product_recommendation_limit": 4
      }
    }
  },
  "order": ["main", "product-recommendations"]
}
```

### Configuration d'analyses et pixels

Pour suivre les performances de votre boutique, configurez les outils d'analyse:

```
POST /api/v1/agents/website-builder/analytics/configure
```

Exemple de configuration:

```json
{
  "google_analytics": {
    "enabled": true,
    "tracking_id": "UA-123456789-1",
    "enhanced_ecommerce": true
  },
  "facebook_pixel": {
    "enabled": true,
    "pixel_id": "987654321098765"
  },
  "additional_scripts": [
    {
      "location": "header",
      "script": "<script>console.log('Header script loaded');</script>"
    },
    {
      "location": "footer",
      "script": "<script>console.log('Footer script loaded');</script>"
    }
  ]
}
```

## Limitations connues

### Limites actuelles

- **Personnalisation de thème**: Certains thèmes Shopify avancés peuvent avoir des options de personnalisation non supportées par l'API.
- **Checkout personnalisé**: La personnalisation complète du processus de paiement nécessite Shopify Plus.
- **Scripts avancés**: Les scripts personnalisés complexes doivent être vérifiés manuellement pour éviter les conflits.
- **Apps tierces**: L'intégration avec certaines applications Shopify tierces peut nécessiter une configuration manuelle.
- **Rate limits**: L'API Shopify impose des limites de requêtes (actuellement 2 requêtes/seconde).

### Contournements possibles

- Pour les thèmes complexes, utilisez l'endpoint `/theme/raw-customize` qui permet d'envoyer des instructions de personnalisation spécifiques au thème.
- Pour les intégrations d'applications tierces, utilisez l'endpoint `/store/install-app` qui facilite l'installation et la configuration de base.
- Pour contourner les limites de requêtes, l'agent utilise un système de file d'attente et de backoff intelligent.

## Dépannage

### Problèmes courants

#### Erreur 422 lors de la configuration de la boutique
Certains paramètres ne sont pas acceptés par l'API Shopify.
**Solution**: Vérifiez que tous les paramètres respectent les contraintes Shopify (formats d'adresse, codes pays valides).

#### Thème non publié après installation
Le thème est installé mais n'est pas défini comme thème principal.
**Solution**: Utilisez l'endpoint `/theme/publish` avec l'ID du thème installé.

#### Collections vides
Les collections sont créées mais ne contiennent pas de produits.
**Solution**: Vérifiez les règles de collection et assurez-vous que les produits ont les tags ou types correspondants.

#### Erreurs 429 (Too Many Requests)
Vous avez dépassé les limites de l'API Shopify.
**Solution**: Réduisez la fréquence des requêtes et utilisez le paramètre `batch=true` pour les opérations multiples.

### Logs et diagnostics

Pour diagnostiquer les problèmes, utilisez l'endpoint de logs:

```
GET /api/v1/agents/website-builder/logs
```

Paramètres:
```
?level=error&start_date=2025-03-15&end_date=2025-03-16
```

Cet endpoint retourne les journaux détaillés des opérations, ce qui est précieux pour identifier la source des problèmes.

### Opérations de récupération

En cas de problème grave, vous pouvez utiliser les endpoints de récupération:

- `/store/restore-backup`: Restaure la boutique à partir d'une sauvegarde
- `/theme/restore`: Restaure un thème à sa version précédente
- `/collections/repair`: Répare les collections corrompues

### Support et ressources supplémentaires

Pour une assistance plus détaillée:

1. Consultez les logs système pour les erreurs détaillées
2. Vérifiez le statut de l'agent via l'endpoint `/system/health`
3. Pour un support spécifique, consultez le [guide de dépannage général](../troubleshooting.md) ou ouvrez une issue sur le dépôt GitHub
