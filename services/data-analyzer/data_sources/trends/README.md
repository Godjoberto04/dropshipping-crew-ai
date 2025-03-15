# Module d'analyse des tendances Google Trends

Ce module permet d'analyser les tendances de recherche Google pour identifier les produits populaires et émergents pour le dropshipping, ainsi que pour évaluer le potentiel des produits sur le long terme.

## Fonctionnalités

- **Analyse de mots-clés** : Évaluation des tendances de recherche pour des mots-clés sur différentes périodes
- **Analyse de produits** : Évaluation complète du potentiel d'un produit avec analyses court, moyen et long terme
- **Comparaison de produits** : Comparaison directe de plusieurs produits en termes de tendances
- **Détection de produits en tendance** : Identification des produits émergents dans une catégorie spécifique
- **Détection de saisonnalité** : Analyse des motifs saisonniers pour les produits
- **Système de cache** : Optimisation des performances grâce au cache des requêtes Google Trends

## Utilisation

### Initialisation

```python
from data_sources.trends.trends_analyzer import TrendsAnalyzer

# Initialisation avec paramètres par défaut
analyzer = TrendsAnalyzer()

# Initialisation avec paramètres personnalisés
analyzer_custom = TrendsAnalyzer(
    hl='en-US',  # Langue
    tz=360,      # Fuseau horaire
    geo='US',    # Région par défaut
    proxies={'https': 'http://proxy.example.com:8080'}  # Proxy optionnel
)
```

### Analyse de mots-clés

```python
# Analyse d'un mot-clé unique
results = analyzer.analyze_keywords('smartphone')

# Analyse de plusieurs mots-clés (maximum 5)
results = analyzer.analyze_keywords(['écouteurs bluetooth', 'casque sans fil', 'montre connectée'])

# Analyse avec période personnalisée
results = analyzer.analyze_keywords('smartphone', timeframe='long_term')  # Analyse sur 12 mois

# Analyse avec région spécifique
results = analyzer.analyze_keywords('smartphone', geo='DE')  # Analyse pour l'Allemagne
```

### Analyse complète de produit

```python
# Analyse complète d'un produit
product_analysis = analyzer.analyze_product('Écouteurs Bluetooth sans fil')

# Analyse avec mots-clés associés
product_analysis = analyzer.analyze_product(
    'Écouteurs Bluetooth sans fil', 
    product_keywords=['écouteurs TWS', 'écouteurs sans fil']
)

# Accès aux données d'analyse
trend_score = product_analysis['overall_trend_score']
is_trending = product_analysis['is_trending']
seasonality = product_analysis['seasonality']
conclusion = product_analysis['conclusion']

# Recommandation du produit
recommendation = conclusion['recommendation']
```

### Comparaison de produits

```python
# Comparaison de plusieurs produits
comparison = analyzer.compare_products(['écouteurs bluetooth', 'casque sans fil', 'montre connectée'])

# Accès aux résultats de la comparaison
ranked_products = comparison['ranked_products']
top_product = comparison['top_product']
```

### Détection de produits en tendance

```python
# Détection des produits en tendance dans une catégorie
trending_products = analyzer.get_rising_products(category='electronic')

# Détection dans une région spécifique
trending_products_fr = analyzer.get_rising_products(category='fashion', geo='FR')

# Limitation du nombre de résultats
top5_trending = analyzer.get_rising_products(limit=5)
```

## Données d'intérêt et métriques

L'analyse des mots-clés retourne les données suivantes :

- **interest_over_time** : Évolution de l'intérêt dans le temps
- **related_queries** : Requêtes associées (top et en croissance)
- **related_topics** : Sujets associés (top et en croissance)
- **interest_by_region** : Répartition de l'intérêt par région
- **trend_metrics** : Métriques calculées pour chaque mot-clé
  - *current_interest* : Niveau d'intérêt actuel
  - *average_interest* : Niveau d'intérêt moyen
  - *growth_rate* : Taux de croissance
  - *volatility* : Instabilité de l'intérêt
  - *momentum* : Élan récent 
  - *is_growing* : Indicateur de croissance
  - *is_seasonal* : Indicateur de saisonnalité
  - *trend_score* : Score global d'intérêt (0-100)

## Système de cache

Le module utilise un système de cache pour optimiser les performances et limiter les requêtes à l'API Google Trends. Les résultats sont mis en cache pendant 24 heures par défaut, mais cette durée peut être modifiée.

```python
# Analyse avec cache personnalisé (48 heures)
results = analyzer.analyze_keywords('smartphone', cache_hours=48)

# Analyse sans cache
results = analyzer.analyze_keywords('smartphone', use_cache=False)
```

## Notes importantes

- Google Trends limite les requêtes à 5 mots-clés par analyse.
- Des quotas peuvent s'appliquer aux requêtes Google Trends, d'où l'importance du cache.
- Les scores générés sont relatifs et ne représentent pas des volumes de recherche absolus.
- La détection de saisonnalité nécessite au moins 1 an de données.
