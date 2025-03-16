# Module d'analyse de complémentarité

Ce module permet d'identifier les produits complémentaires pour optimiser les stratégies de cross-selling et d'up-selling dans un contexte e-commerce de dropshipping.

## Fonctionnalités

- **Identification de produits complémentaires** : Détection des produits fréquemment achetés ensemble
- **Suggestions d'up-sell** : Identification des produits de gamme supérieure à proposer à la place du produit original
- **Création de bundles** : Génération de bundles de produits optimisés pour maximiser la valeur du panier
- **Analyse de panier** : Évaluation du contenu d'un panier et suggestions d'amélioration
- **Plusieurs méthodes d'analyse** : Combinaison de l'analyse par règles d'association, des paires de catégories et des comportements d'achat

## Classes principales

### `ComplementaryAnalyzer`

La classe principale qui intègre toutes les fonctionnalités d'analyse de complémentarité.

```python
from models.complementary import ComplementaryAnalyzer

# Initialisation avec paramètres par défaut
analyzer = ComplementaryAnalyzer()

# Initialisation avec paramètres personnalisés
analyzer_custom = ComplementaryAnalyzer({
    'min_support': 0.02,
    'min_confidence': 0.3,
    'up_sell_price_factor': 1.5
})
```

### `AssociationRulesMiner`

Classe qui implémente l'algorithme Apriori pour extraire les règles d'association entre produits.

```python
from models.complementary import AssociationRulesMiner

# Initialisation
miner = AssociationRulesMiner(min_support=0.01, min_confidence=0.3, min_lift=1.0)

# Extraction des règles
miner.fit(transactions_data)
```

## Utilisation

### Chargement des données

```python
# Chargement des données de transactions
transactions_data = [
    ['product1', 'product2', 'product3'],
    ['product1', 'product4'],
    ['product2', 'product3', 'product5'],
    # ...
]
analyzer.load_transaction_data(transactions_data)

# Chargement des métadonnées des produits
products_data = {
    'product1': {
        'name': 'Smartphone XYZ',
        'category': 'smartphones',
        'price': 299.99,
        'rating': 4.2,
        'popularity': 85
    },
    'product2': {
        'name': 'Coque de protection',
        'category': 'phone_cases',
        'price': 19.99,
        'rating': 4.5,
        'popularity': 92
    },
    # ...
}
analyzer.load_product_metadata(products_data)
```

### Définition manuelle des catégories complémentaires

```python
# Définition manuelle des paires de catégories complémentaires
category_pairs = {
    'smartphones': ['phone_cases', 'screen_protectors', 'chargers', 'headphones'],
    'laptops': ['laptop_bags', 'external_drives', 'mice', 'laptop_stands'],
    'cameras': ['camera_bags', 'tripods', 'lenses', 'memory_cards'],
    # ...
}
analyzer.set_category_pairs(category_pairs)
```

### Obtention de produits complémentaires

```python
# Obtenir les produits complémentaires pour un produit donné
complementary_products = analyzer.get_complementary_products('product1')

# Résultat
[
    {
        'product': 'product2',
        'score': 0.85,
        'confidence': 0.75,
        'lift': 2.3,
        'source': 'association'
    },
    {
        'product': 'product3',
        'score': 0.72,
        'confidence': 0.65,
        'lift': 1.8,
        'source': 'association'
    },
    {
        'product': 'product4',
        'score': 0.63,
        'complementary_category': 'screen_protectors',
        'source': 'category'
    }
]
```

### Obtention de produits d'up-sell

```python
# Obtenir les produits d'up-sell pour un produit donné
upsell_products = analyzer.get_upsell_products('product1')

# Résultat
[
    {
        'product': 'product6',
        'score': 0.82,
        'price_difference': 150.0,
        'price_ratio': 1.5,
        'source': 'category_upsell'
    },
    {
        'product': 'product7',
        'score': 0.75,
        'price_difference': 200.0,
        'price_ratio': 1.66,
        'source': 'category_upsell'
    }
]
```

### Création de bundles

```python
# Créer des bundles à partir d'un ensemble de produits
bundles = analyzer.bundle_products(['product1', 'product2'])

# Résultat
[
    {
        'name': 'Bundle Essentiel',
        'products': ['product1', 'product2', 'product3'],
        'original_price': 359.98,
        'bundle_price': 341.98,
        'discount_percentage': 5,
        'score': 0.9
    },
    {
        'name': 'Bundle Premium',
        'products': ['product1', 'product2', 'product3', 'product4', 'product5'],
        'original_price': 459.95,
        'bundle_price': 413.96,
        'discount_percentage': 10,
        'score': 0.85
    }
]
```

### Analyse de panier

```python
# Analyser un panier pour suggérer des améliorations
cart_analysis = analyzer.analyze_cart(['product1', 'product2'])

# Résultat
{
    'cart_value': 319.98,
    'product_count': 2,
    'missing_complementary': [
        {
            'product': 'product3',
            'score': 0.85,
            'for_product': 'product1',
            'source': 'association'
        },
        # ...
    ],
    'potential_upsells': [
        {
            'product': 'product6',
            'score': 0.82,
            'for_product': 'product1',
            'source': 'category_upsell'
        }
    ],
    'bundle_opportunities': [
        # ...
    ],
    'cart_score': 65  # Plus le score est élevé, plus il y a d'opportunités d'amélioration
}
```

## Paramètres de configuration

| Paramètre | Description | Valeur par défaut |
|-----------|-------------|------------------|
| `min_support` | Support minimal pour les règles d'association | 0.01 |
| `min_confidence` | Confiance minimale pour les règles d'association | 0.2 |
| `min_lift` | Lift minimal pour les règles d'association | 1.5 |
| `up_sell_price_factor` | Facteur de prix minimal pour l'up-sell | 1.3 |
| `max_complementary_products` | Nombre maximum de produits complémentaires à retourner | 5 |
| `max_up_sell_products` | Nombre maximum de produits d'up-sell à retourner | 3 |
| `cache_enabled` | Activation du cache pour les résultats | true |
| `cache_ttl_days` | Durée de vie des données en cache (jours) | 7 |

## Intégration avec les autres composants

### Intégration avec l'agent Data Analyzer

```python
from models.complementary import ComplementaryAnalyzer
from data_sources.trends import TrendsAnalyzer

# Initialisation des analyseurs
trends_analyzer = TrendsAnalyzer()
complementary_analyzer = ComplementaryAnalyzer()

# Analyse d'un produit
trends_data = trends_analyzer.analyze_product('Écouteurs Bluetooth')

# Recherche de produits complémentaires
if trends_data['is_trending']:
    # Plus de recommandations pour les produits en tendance
    complementary_products = complementary_analyzer.get_complementary_products(
        'product_id', 
        max_products=10
    )
else:
    # Recommandations standards
    complementary_products = complementary_analyzer.get_complementary_products('product_id')
```

### Intégration avec l'API

```python
from fastapi import APIRouter, Depends
from models.complementary import ComplementaryAnalyzer

router = APIRouter()
analyzer = ComplementaryAnalyzer()

@router.post("/complementary/{product_id}")
async def get_complementary_products(product_id: str, max_products: int = 5):
    """Endpoint pour obtenir des produits complémentaires"""
    results = analyzer.get_complementary_products(product_id, max_products)
    return {"product_id": product_id, "complementary_products": results}

@router.post("/upsell/{product_id}")
async def get_upsell_products(product_id: str, max_products: int = 3):
    """Endpoint pour obtenir des produits d'up-sell"""
    results = analyzer.get_upsell_products(product_id, max_products)
    return {"product_id": product_id, "upsell_products": results}

@router.post("/bundles")
async def create_bundles(product_ids: list[str], max_bundles: int = 3):
    """Endpoint pour créer des bundles"""
    results = analyzer.bundle_products(product_ids, max_bundles)
    return {"product_ids": product_ids, "bundles": results}

@router.post("/cart/analyze")
async def analyze_cart(product_ids: list[str]):
    """Endpoint pour analyser un panier"""
    results = analyzer.analyze_cart(product_ids)
    return results
```

## Exemple de flux complet

```python
# Initialisation
analyzer = ComplementaryAnalyzer()

# Chargement des données
analyzer.load_transaction_data(transaction_history)
analyzer.load_product_metadata(product_catalog)

# Analyse d'un produit
complementary_products = analyzer.get_complementary_products('smartphone_xyz')

# Identification d'opportunités d'up-sell
upsell_options = analyzer.get_upsell_products('smartphone_xyz')

# Création de bundles pour un client avec plusieurs produits
customer_cart = ['smartphone_xyz', 'phone_case_abc']
bundle_options = analyzer.bundle_products(customer_cart)

# Analyse complète du panier
cart_analysis = analyzer.analyze_cart(customer_cart)

# Génération de recommandations personnalisées
if cart_analysis['cart_score'] > 50:
    # Panier avec opportunités d'amélioration
    recommendations = cart_analysis['missing_complementary']
    
    # Suggestions d'up-sell si pertinent
    if any(up['score'] > 0.8 for up in cart_analysis['potential_upsells']):
        premium_recommendations = cart_analysis['potential_upsells']
```

## Remarques et limitations

- L'algorithme d'association rules requiert un nombre significatif de transactions pour être efficace
- Les recommandations sont aussi bonnes que les données d'entrée
- Le système nécessite des métadonnées précises pour les produits (catégorie, prix, etc.)
- Pour optimiser les performances, utilisez le cache et ajustez les paramètres selon votre catalogue
