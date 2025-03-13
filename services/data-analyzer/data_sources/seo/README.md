# Module d'analyse SEO pour Data Analyzer

Ce module fournit des outils pour collecter et analyser des données SEO provenant de différentes sources (SEMrush, Ahrefs, etc.). Ces données permettent d'évaluer le potentiel SEO des produits et des mots-clés pour le dropshipping.

## Fonctionnalités

- **Analyse de volume de recherche** : Obtention du volume mensuel de recherche pour des mots-clés
- **Analyse de difficulté SEO** : Évaluation de la difficulté à se positionner sur des mots-clés
- **Analyse de la concurrence** : Identification des concurrents et de leurs stratégies
- **Analyse des opportunités** : Détection des mots-clés avec un bon rapport volume/difficulté
- **Tendances SEO** : Analyse de l'évolution des performances SEO des mots-clés

## Implémentation

Le module est conçu pour fonctionner avec différentes sources de données SEO, notamment :

1. **API SEMrush** : Pour les utilisateurs disposant d'une clé API SEMrush
2. **API Ahrefs** : Pour les utilisateurs disposant d'une clé API Ahrefs
3. **Scraping structuré** : Solution alternative pour les utilisateurs sans API (dans le respect des conditions d'utilisation)

## Configuration

Le module utilise les paramètres de configuration suivants (dans `.env` ou via les variables d'environnement) :

```
# Configuration SEMrush
SEMRUSH_API_KEY=your_api_key
SEMRUSH_RATE_LIMIT=5  # Requêtes par seconde
SEMRUSH_DAILY_LIMIT=500  # Limite quotidienne de requêtes

# Configuration Ahrefs (si utilisé)
AHREFS_API_KEY=your_api_key
AHREFS_RATE_LIMIT=5  # Requêtes par seconde
```

## Utilisation

```python
from data_sources.seo.semrush_analyzer import SEMrushAnalyzer

# Initialisation de l'analyseur SEMrush
analyzer = SEMrushAnalyzer(api_key="your_api_key")

# Analyse d'un mot-clé
keyword_data = analyzer.analyze_keyword(
    keyword="écouteurs bluetooth",
    database="fr"  # base de données pour la France
)

# Analyse d'un groupe de mots-clés
keywords_data = analyzer.analyze_keywords(
    keywords=["écouteurs bluetooth", "casque sans fil"],
    database="fr"
)

# Analyse des concurrents pour un mot-clé
competitors = analyzer.get_competitors(
    keyword="écouteurs bluetooth",
    database="fr"
)

# Obtention de suggestions de mots-clés
suggestions = analyzer.get_keyword_suggestions(
    keyword="écouteurs bluetooth",
    database="fr"
)
```

## Intégration avec le système de scoring

Les données SEO sont utilisées par le système de scoring multicritères pour évaluer le potentiel SEO des produits :

```python
from models.scoring.multicriteria import AdvancedProductScorer
from data_sources.seo.semrush_analyzer import SEMrushAnalyzer

# Initialisation des analyseurs
seo_analyzer = SEMrushAnalyzer()
product_scorer = AdvancedProductScorer()

# Analyse SEO d'un produit
seo_data = seo_analyzer.analyze_keyword("écouteurs bluetooth")

# Intégration des données SEO dans le scoring
product_score = product_scorer.score_product(
    product_id="12345",
    product_info={
        "name": "Écouteurs Bluetooth XYZ",
        "keywords": ["écouteurs bluetooth", "casque sans fil"],
        # Autres informations produit...
    },
    seo_data=seo_data
)
```

## Métriques collectées

Le module collecte plusieurs métriques SEO clés, notamment :

- **Volume de recherche mensuel** : Nombre moyen de recherches mensuelles
- **CPC moyen** : Coût par clic moyen en euros/dollars
- **Difficulté du mot-clé** : Score de 0 à 100 indiquant la difficulté à se positionner
- **Nombre de résultats** : Nombre de pages indexées pour le mot-clé
- **Densité de la concurrence** : Score de 0 à 1 indiquant l'intensité de la concurrence publicitaire
- **Tendance sur 12 mois** : Évolution du volume de recherche sur l'année
