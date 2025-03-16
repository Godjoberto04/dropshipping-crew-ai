# Guide d'utilisation de l'agent Data Analyzer

L'agent Data Analyzer est un composant essentiel du système autonome de dropshipping, responsable de l'analyse de marché, de l'identification des produits à fort potentiel et de la génération d'insights stratégiques pour optimiser le catalogue et les ventes.

## Table des matières
1. [Fonctionnalités principales](#fonctionnalités-principales)
2. [Architecture et modules](#architecture-et-modules)
3. [Utilisation via l'API](#utilisation-via-lapi)
4. [Exemples de code](#exemples-de-code)
5. [Cas d'utilisation](#cas-dutilisation)
6. [Conseils d'optimisation](#conseils-doptimisation)
7. [Limitations connues](#limitations-connues)
8. [Dépannage](#dépannage)

## Fonctionnalités principales

L'agent Data Analyzer offre les fonctionnalités suivantes:

### Analyse des tendances
- Analyse des tendances Google Trends pour identifier les produits en hausse
- Détection de la saisonnalité des produits
- Prédiction des tendances futures basée sur l'historique

### Évaluation des produits
- Système de scoring multicritères pour évaluer le potentiel commercial des produits
- Analyse de la concurrence et des prix du marché
- Identification des niches sous-exploitées

### Analyse de complémentarité
- Identification des produits complémentaires pour maximiser la valeur du panier
- Suggestion de bundles intelligents de produits
- Recommandations pour les stratégies d'up-sell et cross-sell

### Optimisation du catalogue
- Analyse de la performance des produits existants
- Recommandations pour l'élargissement ou la réduction du catalogue
- Analyse de la rentabilité par catégorie de produit

## Architecture et modules

L'agent Data Analyzer est composé de plusieurs modules spécialisés:

### TrendsAnalyzer
Module responsable de l'analyse des tendances Google et autres sources de données de tendances.

### MarketplaceAnalyzer
Module qui analyse les produits similaires sur différentes plateformes e-commerce pour évaluer la concurrence et le positionnement prix.

### ScoringSystem
Système de notation qui combine plusieurs critères pour évaluer le potentiel commercial d'un produit.

### ComplementaryAnalyzer
Module qui identifie les produits complémentaires et génère des suggestions de bundles.

### CacheManager
Système d'optimisation qui met en cache les résultats d'analyse pour améliorer les performances.

## Utilisation via l'API

L'agent Data Analyzer expose ses fonctionnalités via l'API REST centrale du système.

### Endpoints principaux

#### Analyse de produit
```
POST /api/v1/agents/data-analyzer/analyze
```

Paramètres:
```json
{
  "product_name": "Smartphone Stand",
  "keywords": ["phone holder", "desk accessory"],
  "category": "Mobile Accessories",
  "price_range": {"min": 10, "max": 30}
}
```

Réponse:
```json
{
  "product_id": "P12345",
  "analysis": {
    "trend_score": 78.5,
    "competition_score": 62.3,
    "overall_score": 73.1,
    "seasonality": {
      "peak_months": ["November", "December"],
      "low_months": ["June", "July"]
    },
    "recommendation": "Recommended product with strong potential during holiday season"
  }
}
```

#### Analyse de tendances
```
GET /api/v1/agents/data-analyzer/trends
```

Paramètres:
```
?keywords=smartphone+stand,phone+holder,desk+organizer&timeframe=12m
```

Réponse:
```json
{
  "trends": [
    {
      "keyword": "smartphone stand",
      "interest_over_time": [45, 48, 52, 58, 62, 59, 55, 70, 85, 92, 88, 76],
      "trend_direction": "up",
      "growth_rate": 15.3
    },
    {
      "keyword": "phone holder",
      "interest_over_time": [60, 62, 58, 55, 53, 50, 52, 65, 72, 78, 75, 70],
      "trend_direction": "stable",
      "growth_rate": 5.2
    }
  ],
  "insights": {
    "top_growing": "smartphone stand",
    "seasonal_pattern": true,
    "peak_period": "November-December"
  }
}
```

#### Analyse de complémentarité
```
POST /api/v1/agents/data-analyzer/complementary
```

Paramètres:
```json
{
  "product_id": "P12345",
  "category": "Mobile Accessories",
  "price_point": 24.99,
  "max_suggestions": 5
}
```

Réponse:
```json
{
  "complementary_products": [
    {
      "product_id": "P45678",
      "name": "Phone Cleaning Kit",
      "affinity_score": 82.5,
      "price_point": 12.99,
      "bundle_discount_recommendation": "15%"
    },
    {
      "product_id": "P78901",
      "name": "Wireless Charger",
      "affinity_score": 78.3,
      "price_point": 29.99,
      "bundle_discount_recommendation": "10%"
    }
  ],
  "bundle_suggestions": [
    {
      "name": "Complete Phone Accessory Kit",
      "products": ["P12345", "P45678", "P78901"],
      "total_price": 67.97,
      "recommended_bundle_price": 57.99,
      "estimated_conversion_lift": "25%"
    }
  ]
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

# Analyse d'un produit
def analyze_product(product_name, keywords, category, price_min, price_max):
    endpoint = f"{BASE_URL}/agents/data-analyzer/analyze"
    
    payload = {
        "product_name": product_name,
        "keywords": keywords,
        "category": category,
        "price_range": {"min": price_min, "max": price_max}
    }
    
    response = requests.post(endpoint, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Analyse de tendances
def get_trends(keywords, timeframe="12m"):
    keywords_param = ",".join(keywords)
    endpoint = f"{BASE_URL}/agents/data-analyzer/trends?keywords={keywords_param}&timeframe={timeframe}"
    
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Utilisation des fonctions
product_analysis = analyze_product(
    "Smartphone Stand", 
    ["phone holder", "desk accessory"], 
    "Mobile Accessories", 
    10, 
    30
)

trend_analysis = get_trends(["smartphone stand", "phone holder", "desk organizer"])

print(json.dumps(product_analysis, indent=2))
print(json.dumps(trend_analysis, indent=2))
```

### Exemple avec Curl

```bash
# Analyse d'un produit
curl -X POST "http://your-server-ip/api/v1/agents/data-analyzer/analyze" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Smartphone Stand",
    "keywords": ["phone holder", "desk accessory"],
    "category": "Mobile Accessories",
    "price_range": {"min": 10, "max": 30}
  }'

# Analyse de tendances
curl -X GET "http://your-server-ip/api/v1/agents/data-analyzer/trends?keywords=smartphone+stand,phone+holder,desk+organizer&timeframe=12m" \
  -H "Authorization: Bearer your_api_key"

# Analyse de complémentarité
curl -X POST "http://your-server-ip/api/v1/agents/data-analyzer/complementary" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "P12345",
    "category": "Mobile Accessories",
    "price_point": 24.99,
    "max_suggestions": 5
  }'
```

## Cas d'utilisation

Voici quelques cas d'utilisation typiques de l'agent Data Analyzer:

### 1. Identification de nouveaux produits à fort potentiel

Utilisez l'analyse de tendances pour identifier des produits émergents avant qu'ils ne deviennent mainstream:

1. Sélectionnez une catégorie de produits d'intérêt
2. Utilisez l'endpoint `/trends` pour analyser les tendances sur 12-24 mois
3. Filtrez les résultats par croissance positive et score de tendance > 70
4. Analysez plus en détail les produits les plus prometteurs avec l'endpoint `/analyze`

### 2. Optimisation saisonnière du catalogue

Anticipez les pics de demande saisonniers pour optimiser votre stock:

1. Analysez la saisonnalité de votre catalogue existant
2. Identifiez les produits avec des pics saisonniers nets
3. Planifiez des augmentations de stock et des campagnes marketing 1-2 mois avant les pics historiques
4. Utilisez l'analyse pour ajuster les prix pendant les périodes de forte demande

### 3. Création de bundles intelligents

Augmentez la valeur moyenne des commandes avec des bundles optimisés:

1. Sélectionnez vos produits à fort volume de vente
2. Utilisez l'endpoint `/complementary` pour identifier les meilleurs produits complémentaires
3. Créez des bundles avec les suggestions de prix et de remises générées
4. Mesurez l'impact sur la valeur du panier moyen et les taux de conversion

### 4. Évaluation de la concurrence

Comprenez votre positionnement par rapport à la concurrence:

1. Identifiez vos produits phares
2. Utilisez l'analyse de marché pour évaluer les produits similaires
3. Comparez les prix, les caractéristiques et le positionnement
4. Ajustez votre stratégie de prix et de marketing en fonction des insights

## Conseils d'optimisation

Pour tirer le meilleur parti de l'agent Data Analyzer:

### Optimisation des requêtes

- **Caching intelligent**: Les résultats d'analyse sont mis en cache pendant 24h. Évitez les appels redondants pour les mêmes données.
- **Requêtes par lots**: Pour analyser plusieurs produits, utilisez l'endpoint `/analyze/batch` plutôt que des appels individuels.
- **Utilisation des paramètres de filtrage**: Filtrez les résultats côté serveur pour réduire la taille des réponses et améliorer les performances.

### Workflow optimisé

- **Analyse périodique**: Programmez des analyses hebdomadaires de votre catalogue pour suivre l'évolution des tendances.
- **Intégration avec le decision-making**: Utilisez les scores et recommandations pour automatiser certaines décisions (ajustements de prix, réapprovisionnement).
- **Validation croisée**: Combinez les données de l'agent Data Analyzer avec d'autres sources (ventes historiques, feedback clients) pour une vision plus complète.

### Configuration recommandée

- **Seuils personnalisés**: Adaptez les seuils de score (par défaut à 70) selon votre tolérance au risque.
- **Profondeur d'analyse**: Ajustez le paramètre `analysis_depth` (1-5) selon vos besoins de précision vs. performance.
- **Fréquence d'analyse**: Pour les niches à évolution rapide, réduisez l'intervalle entre les analyses.

## Limitations connues

### Limites actuelles

- **Google Trends**: Limité à 5 mots-clés par requête pour éviter le rate limiting
- **Analyse de complémentarité**: Plus précise dans les catégories avec un historique de ventes significatif
- **Prédictions**: La précision diminue au-delà de 3 mois pour les prévisions de tendances
- **Rate limits**: Maximum 100 requêtes/heure pour l'endpoint `/analyze` et 20 requêtes/heure pour `/trends`

### Contournements possibles

- **Rate limiting**: Utilisez le mode batch et planifiez les analyses intensives pendant les heures creuses
- **Améliorations des prédictions**: Fournissez des données historiques supplémentaires via le paramètre `historical_data`
- **Analyse de complémentarité limitée**: Utilisez le paramètre `force_suggestions=true` pour générer des suggestions même avec peu de données

## Dépannage

### Problèmes courants

#### Erreur 429 (Too Many Requests)
Vous avez dépassé les rate limits de l'API.
**Solution**: Espacez vos requêtes ou utilisez le mode batch.

#### Scores anormalement bas
Peut indiquer des mots-clés trop génériques ou une catégorie saturée.
**Solution**: Affinez vos mots-clés ou explorez des niches plus spécifiques.

#### Cache incohérent
Les résultats semblent périmés ou incorrects.
**Solution**: Utilisez le paramètre `force_refresh=true` pour ignorer le cache.

#### Résultats manquants
Certains produits attendus ne sont pas inclus dans l'analyse.
**Solution**: Vérifiez les filtres appliqués et élargissez les critères de recherche.

### Obtenir de l'aide

Si vous rencontrez des problèmes persistants:

1. Consultez les logs système pour les erreurs détaillées
2. Vérifiez le statut du service via l'endpoint `/system/health`
3. Pour un support spécifique, consultez le [guide de dépannage général](../troubleshooting.md) ou ouvrez une issue sur le dépôt GitHub
