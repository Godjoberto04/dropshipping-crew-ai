# Agent Data Analyzer

## Description

L'agent Data Analyzer est responsable d'analyser le marché et les concurrents, d'identifier les produits à fort potentiel, et de générer des rapports d'analyse pour le projet Dropshipping Crew AI.

## Fonctionnalités

- Analyse de tendances produits via Google Trends
- Évaluation multicritères des produits
- Analyse de la concurrence sur les marketplaces
- Prédiction de tendances et comportements

## Structure du projet

```
data-analyzer/
├── Dockerfile               # Configuration Docker
├── requirements.txt         # Dépendances Python
├── config.py                # Configuration de l'agent
├── main.py                  # Point d'entrée de l'agent
├── data_sources/            # Sources de données
│   ├── __init__.py
│   ├── trends/              # Intégration Google Trends
│   │   ├── __init__.py
│   │   └── trends_analyzer.py
│   ├── marketplaces/        # Scrapers de marketplaces
│   │   ├── __init__.py
│   │   └── marketplace_analyzer.py
│   └── social/              # Analyse des réseaux sociaux
│       ├── __init__.py
│       └── social_analyzer.py
├── models/                  # Modèles prédictifs
│   ├── __init__.py
│   ├── scoring/             # Système de scoring
│   │   ├── __init__.py
│   │   └── product_scorer.py
│   └── forecasting/         # Prévisions
│       ├── __init__.py
│       └── trend_forecaster.py
├── tools/                   # Outils partagés
│   ├── __init__.py
│   └── api_client.py        # Client pour l'API centrale
└── tests/                   # Tests unitaires
    ├── __init__.py
    └── test_trends_analyzer.py
```

## Utilisation

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Créez un fichier `.env` basé sur `.env.example` et renseignez les variables nécessaires.

### Exécution

```bash
python main.py
```

## Tests

```bash
python -m unittest discover tests
```

## Dépendances principales

- pytrends - Interface pour Google Trends
- pandas - Manipulation et analyse de données
- scikit-learn - Algorithmes de machine learning
- asyncio - Programmation asynchrone
- aiohttp - Client HTTP asynchrone
