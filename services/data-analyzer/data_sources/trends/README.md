# Module d'analyse de tendances (PyTrends)

Ce module est responsable de l'analyse des tendances de produits et de mots-clés via Google Trends. Il fait partie de l'agent Data Analyzer du projet dropshipping-crew-ai.

## Fonctionnalités

- **Analyse de mots-clés** : Évalue l'intérêt pour des mots-clés sur différentes périodes et régions
- **Analyse de produits** : Analyse complète d'un produit pour déterminer son potentiel
- **Comparaison de produits** : Compare l'intérêt pour plusieurs produits
- **Détection de produits en tendance** : Identifie les produits en forte croissance
- **Détection de saisonnalité** : Détecte les motifs saisonniers dans les données

## Architecture

Le module est construit autour de la classe `TrendsAnalyzer` qui encapsule la bibliothèque PyTrends et ajoute des fonctionnalités supplémentaires :

- **Analyse avancée** : Calcul de scores de tendance, détection de saisonnalité, etc.
- **Mise en cache** : Sauvegarde et chargement des résultats pour optimiser les performances
- **Gestion des erreurs** : Robustesse face aux limitations de l'API Google Trends
- **Organisation des données** : Structuration des données pour faciliter leur exploitation

## Utilisation

```python
from data_sources.trends.trends_analyzer import TrendsAnalyzer

# Création d'une instance de l'analyseur
analyzer = TrendsAnalyzer(hl="fr", geo="FR")

# Analyse de mots-clés
keywords_results = analyzer.analyze_keywords(
    keywords=["smartphone", "tablette"],
    timeframe="medium_term"
)

# Analyse complète d'un produit
product_analysis = analyzer.analyze_product(
    product_name="écouteurs bluetooth",
    product_keywords=["écouteurs sans fil", "casque audio"],
    timeframes=["short_term", "medium_term", "long_term"]
)

# Récupération des produits en tendance
trending_products = analyzer.get_rising_products(category=0, geo="FR")
```

## Métriques calculées

Le module calcule plusieurs métriques pour chaque mot-clé ou produit :

- **Intérêt actuel** : Niveau d'intérêt actuel (0-100)
- **Taux de croissance** : Évolution de l'intérêt en pourcentage
- **Momentum** : Dynamique récente (comparaison des dernières périodes)
- **Volatilité** : Stabilité de l'intérêt dans le temps
- **Score de tendance** : Score global (0-100) combinant les métriques précédentes
- **Saisonnalité** : Détection et quantification des motifs saisonniers

## Configuration

Le module utilise les paramètres suivants (configurables dans `.env`) :

- **PYTRENDS_HL** : Langue pour Google Trends (fr, en-US, etc.)
- **PYTRENDS_TZ** : Fuseau horaire (-360 à 360)
- **PYTRENDS_GEO** : Pays par défaut (FR, US, etc.)
- **PROXY_ENABLED** : Activer l'utilisation d'un proxy (True/False)
- **PROXY_URL** : URL du proxy (http://user:pass@host:port)

## Tests

Le module est couvert par des tests unitaires complets :

```bash
# Exécution des tests pour le module TrendsAnalyzer
python -m unittest tests.test_trends_analyzer
```

## Limites et considérations

- L'API Google Trends impose des limites sur le nombre de requêtes
- Les données sont relatives et non absolues
- La précision varie selon la popularité des termes recherchés
- Un système de cache est implémenté pour éviter les requêtes redondantes
