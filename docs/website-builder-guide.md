# Guide de l'agent Website Builder

## Vue d'ensemble

L'agent Website Builder est responsable de la création et de la gestion automatique de la boutique Shopify. Il permet de configurer les paramètres de base, gérer les thèmes, créer la structure de navigation et ajouter des produits à la boutique.

## Fonctionnalités principales

1. **Configuration initiale de la boutique**
   - Paramètres de base (nom, devise, langue)
   - Thème et personnalisation
   - Pages standards (Accueil, À propos, Contact)
   - Structure de navigation

2. **Gestion des produits**
   - Ajout de produits à partir des recommandations du Data Analyzer
   - Configuration des variantes, prix et stock
   - Organisation en collections

3. **Personnalisation du thème**
   - Couleurs et polices
   - Sections de la page d'accueil
   - Configuration responsive

## Prérequis

### 1. Créer un compte Shopify

1. Rendez-vous sur [Shopify.com](https://www.shopify.com/)
2. Cliquez sur "Commencer l'essai gratuit"
3. Remplissez le formulaire avec vos informations
4. Choisissez un nom pour votre boutique
5. Répondez aux questions concernant votre activité
6. Sur la page "Ajouter un produit", vous pouvez ignorer cette étape pour l'instant
7. Sélectionnez un forfait (Lite ou Basique recommandé pour débuter)

### 2. Configurer l'API Shopify

1. Dans votre tableau de bord Shopify, allez dans "Applications"
2. Cliquez sur "Développer des applications"
3. Cliquez sur "Créer une application"
4. Donnez un nom à votre application (ex: "Dropshipping Crew AI")
5. Dans la section "Configuration de l'API Admin", accordez les autorisations suivantes :
   - `read_products`, `write_products`
   - `read_themes`, `write_themes`
   - `read_content`, `write_content`
   - `read_orders`, `write_orders`
   - `read_inventory`, `write_inventory`
6. Obtenez votre clé API, votre secret API et votre token d'accès

### 3. Configurer le système

Modifiez le fichier `.env` de votre projet pour inclure :

```
SHOPIFY_API_KEY=votre_api_key
SHOPIFY_API_SECRET=votre_api_secret
SHOPIFY_STORE_URL=votre-boutique.myshopify.com
SHOPIFY_ACCESS_TOKEN=votre_access_token
```

## Utilisation de l'agent Website Builder

### Configuration d'une nouvelle boutique

Pour configurer une nouvelle boutique, utilisez l'endpoint `/agents/website-builder/action` :

```bash
curl -X POST "http://votre-serveur:8000/agents/website-builder/action" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "setup_store",
    "store_config": {
      "name": "Ma Boutique Dropshipping",
      "currency": "EUR",
      "language": "fr",
      "theme": {
        "name": "Dawn",
        "colors": {
          "primary": "#3b82f6",
          "secondary": "#10b981",
          "background": "#ffffff"
        }
      },
      "navigation": {
        "main_menu": [
          {"title": "Accueil", "url": "/"},
          {"title": "Produits", "url": "/collections/all"},
          {"title": "À propos", "url": "/pages/about"},
          {"title": "Contact", "url": "/pages/contact"}
        ]
      },
      "pages": [
        {
          "title": "À propos",
          "content": "Bienvenue sur notre boutique..."
        },
        {
          "title": "Contact",
          "content": "Vous pouvez nous contacter à..."
        }
      ]
    }
  }'
```

### Ajout d'un produit

Pour ajouter un produit à la boutique :

```bash
curl -X POST "http://votre-serveur:8000/agents/website-builder/action" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add_product",
    "product_data": {
      "title": "Housse de Protection Smartphone Premium",
      "description": "Housse de protection haut de gamme pour smartphones...",
      "vendor": "TechProtect",
      "product_type": "Accessoire Smartphone",
      "tags": ["protection", "smartphone", "premium"],
      "variants": [
        {
          "price": "15.99",
          "compare_at_price": "24.99",
          "inventory_quantity": 100
        }
      ],
      "images": [
        {
          "src": "https://exemple.com/image.jpg",
          "alt": "Housse de protection"
        }
      ]
    }
  }'
```

### Suivi des tâches

Pour suivre l'état d'une tâche :

```bash
curl "http://votre-serveur:8000/tasks/{task_id}"
```

## Intégration avec l'agent Data Analyzer

L'agent Website Builder peut utiliser les résultats de l'agent Data Analyzer pour ajouter automatiquement des produits à fort potentiel à la boutique. Voici un exemple de script d'intégration :

```python
import requests
import json
import time

# Configuration
API_URL = "http://votre-serveur:8000"
THRESHOLD_SCORE = 7.5  # Score minimum pour ajouter un produit

# Étape 1 : Récupérer les derniers résultats d'analyse
response = requests.get(f"{API_URL}/analysis/results/latest")
analysis_results = response.json()

# Étape 2 : Filtrer les produits avec un bon score
recommended_products = [
    product for product in analysis_results.get("top_products", [])
    if product.get("recommendation_score", 0) >= THRESHOLD_SCORE
]

print(f"Produits recommandés trouvés : {len(recommended_products)}")

# Étape 3 et 4 : Transformer et ajouter les produits à Shopify
for product in recommended_products:
    # Transformer en format Shopify
    shopify_product = {
        "title": product["name"],
        "description": product.get("justification", ""),
        "vendor": "Dropshipping Autonome",
        "product_type": "Accessoire",
        "tags": ["automatisé", "recommandé"],
        "variants": [
            {
                "price": str(product["recommended_price"]),
                "compare_at_price": str(product["recommended_price"] * 1.2),  # +20%
                "inventory_quantity": 100
            }
        ],
        "images": []
    }
    
    # Ajouter l'image si disponible
    if product.get("image_url"):
        shopify_product["images"].append({
            "src": product["image_url"],
            "alt": product["name"]
        })
    
    # Ajouter le produit via l'agent Website Builder
    response = requests.post(
        f"{API_URL}/agents/website-builder/action",
        json={
            "action": "add_product",
            "product_data": shopify_product
        }
    )
    
    if response.status_code == 200:
        print(f"Produit ajouté : {product['name']}")
        task_id = response.json().get("task_id")
        
        # Attendre que la tâche soit terminée (optionnel)
        for _ in range(10):  # Maximum 10 tentatives
            time.sleep(5)  # Attendre 5 secondes
            status_response = requests.get(f"{API_URL}/tasks/{task_id}")
            status = status_response.json().get("status")
            if status in ["completed", "failed"]:
                print(f"Tâche {task_id} terminée avec statut : {status}")
                break
    else:
        print(f"Erreur lors de l'ajout du produit : {response.text}")
```

## Prochaines étapes

Pour continuer le développement de l'agent Website Builder :

1. **Améliorer la personnalisation des thèmes**
   - Ajouter plus d'options pour les couleurs et les polices
   - Configurer les sections de la page d'accueil

2. **Développer la gestion des collections**
   - Créer des collections automatiques basées sur les tags
   - Organiser les produits en catégories logiques

3. **Configurer les méthodes de paiement et d'expédition**
   - Intégrer Stripe/PayPal
   - Configurer les zones d'expédition
   - Définir les tarifs d'expédition

4. **Passer à l'agent Content Generator**
   - Générer des descriptions de produits optimisées SEO
   - Créer des pages catégories avec du contenu pertinent
   - Rédiger des articles de blog liés aux produits
