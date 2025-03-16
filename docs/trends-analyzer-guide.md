# Guide d'utilisation du module TrendsAnalyzer

## Introduction

Le module `TrendsAnalyzer` est un composant clé de l'agent Data Analyzer dans le projet dropshipping-crew-ai. Il permet d'analyser des produits et mots-clés via Google Trends pour identifier les tendances, évaluer le potentiel de marché et découvrir des opportunités de dropshipping prometteuses.

Ce guide détaille les fonctionnalités du module, comment l'utiliser efficacement et les différentes métriques qu'il fournit.

## Table des matières

1. [Installation et prérequis](#installation-et-prérequis)
2. [Initialisation du module](#initialisation-du-module)
3. [Fonctionnalités principales](#fonctionnalités-principales)
   - [Analyse de mots-clés](#analyse-de-mots-clés)
   - [Analyse de produits](#analyse-de-produits)
   - [Comparaison de produits](#comparaison-de-produits)
   - [Identification de produits en tendance](#identification-de-produits-en-tendance)
4. [Comprendre les métriques](#comprendre-les-métriques)
   - [Score de tendance](#score-de-tendance)
   - [Détection de saisonnalité](#détection-de-saisonnalité)
   - [Analyse de croissance](#analyse-de-croissance)
5. [Système de cache](#système-de-cache)
6. [Exemples d'utilisation](#exemples-dutilisation)
7. [Bonnes pratiques](#bonnes-pratiques)
8. [Dépannage](#dépannage)

## Installation et prérequis

Le module `TrendsAnalyzer` dépend principalement de la bibliothèque PyTrends, une interface Python non officielle pour Google Trends.

### Dépendances

- Python 3.8+
- pandas
- numpy
- pytrends
- requests

### Installation des dépendances

```bash
pip install pandas numpy pytrends requests
```

## Initialisation du module

Pour utiliser le module `TrendsAnalyzer`, vous devez d'abord l'importer et initialiser une instance:

```python
from data_sources.trends.trends_analyzer import TrendsAnalyzer

# Initialisation avec les paramètres par défaut
analyzer = TrendsAnalyzer()

# Initialisation avec paramètres personnalisés
analyzer = TrendsAnalyzer(
    hl='fr',           # Langue (fr, en-US, etc.)
    tz=0,              # Fuseau horaire (-360 à 360)
    geo='FR',          # Pays par défaut (FR, US, etc.)
    timeout=(10, 25),  # Timeout pour les requêtes (connect, read)
    retries=2,         # Nombre de tentatives en cas d'échec
    backoff_factor=0.1,# Facteur de recul pour les tentatives
    proxies={'https': 'http://your-proxy:port'},  # Proxy (optionnel)
    cache_dir='/path/to/cache'  # Répertoire de cache personnalisé (optionnel)
)
```

Les paramètres sont pris depuis les variables d'environnement ou la configuration par défaut si non spécifiés.

## Fonctionnalités principales

### Analyse de mots-clés

La méthode `analyze_keywords` permet d'analyser un ou plusieurs mots-clés (jusqu'à 5) pour obtenir des données de tendance détaillées:

```python
results = analyzer.analyze_keywords(
    keywords=['écouteurs bluetooth', 'casque sans fil'],
    timeframe='medium_term',  # 'short_term', 'medium_term', 'long_term', 'five_years' ou format PyTrends
    geo='FR',                 # Zone géographique
    category=0,               # ID de catégorie Google Trends (0 = toutes catégories)
    use_cache=True,           # Utiliser le cache si disponible
    cache_hours=24            # Âge maximal du cache en heures
)
```

Cette méthode retourne un dictionnaire contenant:
- `interest_over_time`: DataFrame pandas avec l'évolution de l'intérêt
- `related_queries`: Requêtes associées aux mots-clés
- `related_topics`: Sujets associés aux mots-clés
- `interest_by_region`: Intérêt par région géographique
- `trend_metrics`: Métriques calculées (score de tendance, taux de croissance, etc.)
- `summary`: Résumé et conclusions des analyses

### Analyse de produits

La méthode `analyze_product` permet d'analyser un produit de manière complète sur plusieurs périodes:

```python
product_analysis = analyzer.analyze_product(
    product_name='Écouteurs sans fil XYZ',
    product_keywords=['écouteurs bluetooth', 'true wireless'],  # Mots-clés associés (optionnel)
    timeframes=['short_term', 'medium_term', 'long_term'],      # Périodes à analyser
    geo='FR'                                                     # Zone géographique
)
```

Cette méthode retourne un dictionnaire contenant:
- `product_name`: Nom du produit analysé
- `keywords`: Mots-clés utilisés pour l'analyse
- `analysis_by_timeframe`: Résultats d'analyse pour chaque période
- `related_keywords_analysis`: Analyse des mots-clés associés
- `overall_trend_score`: Score global de tendance (0-100)
- `is_trending`: Booléen indiquant si le produit est en tendance
- `seasonality`: Informations sur la saisonnalité du produit
- `conclusion`: Conclusions générées automatiquement

### Comparaison de produits

La méthode `compare_products` permet de comparer jusqu'à 5 produits pour identifier les plus prometteurs:

```python
comparison = analyzer.compare_products(
    products=['Écouteurs Bluetooth XYZ', 'Casque sans fil ABC', 'Enceinte portable 123'],
    timeframe='medium_term',  # Période d'analyse
    geo='FR',                 # Zone géographique
    category=0,               # ID de catégorie Google Trends
    use_cache=True            # Utiliser le cache si disponible
)
```

Cette méthode retourne un dictionnaire contenant:
- `ranked_products`: Liste des produits classés par score de tendance
- `interest_over_time`: Données d'intérêt au fil du temps pour visualisation
- `analysis_period`: Période utilisée pour l'analyse
- `timestamp`: Horodatage de l'analyse
- `top_product`: Produit avec le meilleur score
- `product_trends`: Résumé des tendances pour chaque produit

### Identification de produits en tendance

La méthode `get_rising_products` permet d'identifier les produits en tendance montante dans une catégorie:

```python
rising_products = analyzer.get_rising_products(
    category='fashion',  # Catégorie de produits
    geo='FR',            # Zone géographique
    limit=10             # Nombre maximum de produits à retourner
)
```

Cette méthode retourne une liste de dictionnaires, chacun contenant:
- `name`: Nom du produit
- `trend_score`: Score de tendance (0-100)
- `growth_rate`: Taux de croissance
- `is_growing`: Booléen indiquant si le produit est en croissance
- `rising_value`: Valeur de croissance (de Google Trends)
- `category`: Catégorie du produit

## Comprendre les métriques

### Score de tendance

Le score de tendance est un indicateur synthétique sur une échelle de 0 à 100 qui évalue le potentiel d'un produit ou mot-clé. Il combine plusieurs facteurs:

- **Intérêt actuel**: Niveau d'intérêt récent (0-100)
- **Taux de croissance**: Évolution de l'intérêt en pourcentage
- **Volatilité**: Stabilité de l'intérêt (moins de volatilité = meilleur score)
- **Momentum**: Accélération récente de l'intérêt
- **Intérêt moyen**: Niveau d'intérêt moyen sur la période

Interprétation du score:
- **80-100**: Tendance très forte, excellente opportunité
- **60-79**: Bonne tendance, opportunité intéressante
- **40-59**: Tendance modérée, à surveiller
- **20-39**: Tendance faible, peu d'opportunité
- **0-19**: Pas de tendance, à éviter

### Détection de saisonnalité

Le module détecte automatiquement les tendances saisonnières dans les données historiques. Un produit est considéré comme saisonnier s'il présente des pics d'intérêt réguliers à certaines périodes de l'année.

La saisonnalité est détectée par autocorrélation des données sur des périodes de 52 semaines (annuel), 26 semaines (semestriel) ou 13 semaines (trimestriel).

La détection de saisonnalité est particulièrement utile pour:
- Planifier les stocks à l'avance
- Anticiper les campagnes marketing
- Éviter les produits très saisonniers si vous recherchez des revenus stables toute l'année

### Analyse de croissance

L'analyse de croissance comprend plusieurs indicateurs:

- **Taux de croissance**: Pourcentage d'évolution entre le début et la fin de la période
- **Momentum**: Comparaison entre l'intérêt récent et l'intérêt précédent
- **Indicateur "is_growing"**: Booléen indiquant si le produit est en croissance significative

Un produit est considéré "en tendance" s'il remplit l'un des critères suivants:
- Score de tendance court terme ≥ 70 et croissance court terme ≥ 10%
- Score de tendance moyen terme ≥ 60 et croissance moyen terme ≥ 5%
- Score court terme > score moyen terme et score court terme ≥ 65

## Système de cache

Le module `TrendsAnalyzer` intègre un système de cache qui permet de stocker les résultats d'analyse pour éviter des appels répétés à l'API Google Trends. Cela améliore les performances et évite les limitations de taux.

Le cache utilise des fichiers pickle (.pkl) stockés dans le répertoire spécifié lors de l'initialisation ou dans le répertoire par défaut (settings.CACHE_DIR/trends).

Chaque requête est associée à une clé de cache unique basée sur les paramètres de la requête (mots-clés, période, région, catégorie).

Vous pouvez contrôler l'utilisation du cache avec les paramètres:
- `use_cache=True|False`: Active ou désactive l'utilisation du cache
- `cache_hours=24`: Durée de validité du cache en heures

## Exemples d'utilisation

### Exemple 1: Analyse d'un produit spécifique

```python
from data_sources.trends.trends_analyzer import TrendsAnalyzer

analyzer = TrendsAnalyzer(geo='FR')

# Analyse complète d'un produit
product_analysis = analyzer.analyze_product(
    product_name="Écouteurs sans fil",
    product_keywords=["écouteurs bluetooth", "écouteurs true wireless", "écouteurs apple"],
    timeframes=["short_term", "medium_term", "long_term"]
)

# Afficher le score global et la conclusion
print(f"Score de tendance: {product_analysis['overall_trend_score']:.1f}/100")
print(f"En tendance: {'Oui' if product_analysis['is_trending'] else 'Non'}")
print(f"Saisonnier: {'Oui' if product_analysis['seasonality']['is_seasonal'] else 'Non'}")
print("\nConclusion:")
print(product_analysis['conclusion'])
```

### Exemple 2: Comparaison de produits concurrents

```python
# Comparaison de produits concurrents
comparison = analyzer.compare_products(
    products=[
        "Écouteurs sans fil Apple AirPods",
        "Écouteurs sans fil Sony WF-1000XM4",
        "Écouteurs sans fil Samsung Galaxy Buds"
    ],
    timeframe="medium_term"
)

# Afficher le classement
print("Classement des produits par score de tendance:")
for i, product in enumerate(comparison['ranked_products']):
    print(f"{i+1}. {product['name']} - Score: {product['trend_score']:.1f}/100")

# Afficher le produit en tête
print(f"\nProduit recommandé: {comparison['top_product']}")
```

### Exemple 3: Trouver des produits en tendance dans une catégorie

```python
# Identifier les produits en tendance dans la catégorie mode
rising_products = analyzer.get_rising_products(category="fashion", limit=5)

print("Produits en tendance montante dans la catégorie mode:")
for product in rising_products:
    print(f"- {product['name']} (Score: {product['trend_score']:.1f}, Croissance: {product['growth_rate']:.1f}%)")
```

## Bonnes pratiques

1. **Utiliser le cache intelligemment**
   - Activez le cache pour les analyses répétées
   - Ajustez la durée de validité du cache selon vos besoins (plus courte pour les tendances rapides)

2. **Combiner différentes périodes d'analyse**
   - Utilisez `short_term` pour les tendances immédiates
   - Utilisez `medium_term` pour l'équilibre entre actualité et fiabilité
   - Utilisez `long_term` pour les tendances structurelles et la saisonnalité

3. **Compléter avec d'autres sources de données**
   - Combinez les résultats avec des données de marketplaces (Amazon, AliExpress)
   - Utilisez des données SEO pour valider le potentiel
   - Analysez les réseaux sociaux pour les tendances émergentes

4. **Optimiser l'utilisation de l'API**
   - Limitez le nombre de requêtes en regroupant les analyses
   - Utilisez des proxies en rotation si vous faites beaucoup de requêtes
   - Évitez les requêtes trop fréquentes pour ne pas être bloqué par Google

5. **Interpréter les résultats avec discernement**
   - Un score élevé n'est pas toujours synonyme de succès commercial
   - Tenez compte de la saisonnalité dans votre stratégie
   - Analysez la qualité de la concurrence et pas uniquement son volume

## Dépannage

### Problèmes courants

1. **Erreur "429 Too Many Requests"**
   - Google Trends limite le nombre de requêtes par IP
   - Solution: Utilisez le cache, ajoutez des délais entre les requêtes, ou utilisez des proxies

2. **Données manquantes ou incomplètes**
   - Certains mots-clés ont peu de données dans Google Trends
   - Solution: Essayez des termes alternatifs ou plus génériques

3. **Résultats contradictoires entre périodes**
   - Les tendances peuvent varier selon l'échelle de temps
   - Solution: Privilégiez la période la plus pertinente pour votre stratégie

4. **Erreurs ou timeouts de l'API**
   - Connectivity issues with Google's servers
   - Solution: Augmentez les valeurs de timeout et retries, vérifiez votre connexion

### Conseils pour le dépannage

- Activez les logs détaillés pour identifier l'origine des problèmes
- Vérifiez que votre version de pytrends est à jour
- Pour les analyses complexes, envisagez d'utiliser des backoffs exponentiels entre les requêtes
- Nettoyez régulièrement le cache si vous rencontrez des comportements étranges

---

Pour toute question ou suggestion d'amélioration concernant ce module, veuillez ouvrir une issue sur le dépôt GitHub du projet.
