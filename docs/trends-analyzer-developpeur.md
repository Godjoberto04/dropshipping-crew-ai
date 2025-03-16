# Guide technique du module TrendsAnalyzer pour développeurs

Ce document fournit des informations techniques détaillées sur le module `TrendsAnalyzer` pour les développeurs qui souhaitent étendre ses fonctionnalités, le personnaliser ou l'intégrer dans d'autres composants du projet dropshipping-crew-ai.

## Table des matières

1. [Architecture du module](#architecture-du-module)
2. [Structure des données](#structure-des-données)
3. [Algorithmes clés](#algorithmes-clés)
4. [Extension du module](#extension-du-module)
5. [Intégration avec d'autres modules](#intégration-avec-dautres-modules)
6. [Optimisation des performances](#optimisation-des-performances)
7. [Tests et validation](#tests-et-validation)
8. [Bonnes pratiques de développement](#bonnes-pratiques-de-développement)

## Architecture du module

Le module `TrendsAnalyzer` est conçu selon les principes de programmation orientée objet et repose sur plusieurs composants clés :

### Structure des fichiers

```
data_sources/
├── trends/
│   ├── __init__.py
│   └── trends_analyzer.py
```

### Flux de traitement des données

1. **Collecte** : Interrogation de l'API Google Trends via PyTrends
2. **Transformation** : Conversion des données brutes en métriques analytiques
3. **Analyse** : Calcul de scores et indicateurs de tendance
4. **Interprétation** : Génération de conclusions et recommandations

### Classes et méthodes principales

La classe principale `TrendsAnalyzer` encapsule toute la logique d'analyse et expose les méthodes publiques suivantes :

```python
# Méthodes publiques principales
analyze_keywords()      # Analyse de base des mots-clés
analyze_product()       # Analyse complète d'un produit
compare_products()      # Comparaison de plusieurs produits
get_rising_products()   # Identification des produits en tendance

# Méthodes privées importantes
_calculate_trend_metrics()    # Calcul des métriques de tendance
_calculate_trend_score()      # Calcul du score de tendance global
_detect_seasonality()         # Détection de saisonnalité
_generate_summary()           # Génération de résumés
_generate_product_conclusion() # Génération de conclusions pour produits
```

## Structure des données

### Entrées

Les entrées principales du module sont des mots-clés et paramètres d'analyse spécifiés par l'utilisateur :

```python
# Exemples d'entrées
keywords = ["écouteurs bluetooth", "écouteurs sans fil"]
timeframe = "medium_term"  # ou "now 3-m" format PyTrends
geo = "FR"
category = 0
```

### Sorties

Les sorties sont des structures de données imbriquées contenant les résultats d'analyse :

#### Exemple de sortie `analyze_keywords()`

```python
{
    'interest_over_time': pandas.DataFrame,  # Évolution de l'intérêt au fil du temps
    'related_queries': {                     # Requêtes associées
        'écouteurs bluetooth': {
            'top': pandas.DataFrame,        # Requêtes principales
            'rising': pandas.DataFrame      # Requêtes en augmentation
        }
    },
    'related_topics': {                      # Sujets associés
        'écouteurs bluetooth': {
            'top': pandas.DataFrame,
            'rising': pandas.DataFrame
        }
    },
    'interest_by_region': pandas.DataFrame,  # Intérêt par région
    'trend_metrics': {                       # Métriques calculées
        'écouteurs bluetooth': {
            'current_interest': 75.0,        # Intérêt actuel (0-100)
            'average_interest': 65.2,        # Intérêt moyen
            'growth_rate': 15.3,             # Taux de croissance (%)
            'volatility': 8.7,               # Volatilité (écart-type)
            'momentum': 12.5,                # Momentum (%)
            'is_growing': True,              # En croissance ?
            'is_seasonal': False,            # Saisonnier ?
            'seasonality_score': 0.0,        # Score de saisonnalité (0-100)
            'trend_score': 78.6              # Score global (0-100)
        }
    },
    'summary': {                             # Résumé de l'analyse
        'top_keyword': 'écouteurs bluetooth',
        'avg_trend_score': 78.6,
        'trending_keywords': ['écouteurs bluetooth'],
        'conclusion': 'Texte de conclusion...'
    }
}
```

#### Exemple de sortie `analyze_product()`

```python
{
    'product_name': 'Écouteurs sans fil',
    'keywords': ['Écouteurs sans fil', 'écouteurs bluetooth', 'écouteurs true wireless'],
    'analysis_by_timeframe': {
        'short_term': { ... },  # Résultats de analyze_keywords()
        'medium_term': { ... },
        'long_term': { ... }
    },
    'related_keywords_analysis': {
        'écouteurs bluetooth': { ... },  # Résultats de analyze_keywords()
        'écouteurs true wireless': { ... }
    },
    'overall_trend_score': 82.3,         # Score global (0-100)
    'is_trending': True,                 # En tendance ?
    'seasonality': {
        'is_seasonal': False,
        'pattern': 'none',
        'peak_periods': []
    },
    'conclusion': 'Texte de conclusion...'
}
```
