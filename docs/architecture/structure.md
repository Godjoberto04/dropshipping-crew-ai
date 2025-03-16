# Structure du projet

Ce document présente l'organisation des fichiers et dossiers du projet, expliquant la logique derrière cette structure et les conventions utilisées.

## Vue d'ensemble

Le projet est organisé selon une architecture modulaire, où chaque agent est implémenté comme un service distinct. Cette approche facilite le développement indépendant des composants, leur déploiement et leur maintenance.

```
/opt/dropship-crew-ai/          # Racine du projet en production
├── config/                     # Configuration globale
├── services/                   # Services (agents) du système
├── data/                       # Données persistantes
├── logs/                       # Logs centralisés
├── scripts/                    # Scripts utilitaires
├── .env                        # Variables d'environnement
└── docker-compose.yml          # Configuration Docker Compose
```

## Structure détaillée

### Dossier /config/

Contient les fichiers de configuration globaux qui s'appliquent à l'ensemble du système.

```
/config/
├── prometheus/                 # Configuration Prometheus
│   └── prometheus.yml
└── nginx/                      # Configuration Nginx
    ├── nginx.conf
    └── sites-enabled/
        └── default.conf
```

### Dossier /services/

Contient chacun des services (agents) du système, ainsi que l'API centrale et le dashboard.

```
/services/
├── api/                        # API centralisée
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # Point d'entrée de l'application
│       ├── models/             # Modèles de données Pydantic
│       ├── routers/            # Routeurs FastAPI
│       ├── dependencies/       # Dépendances partagées
│       ├── core/               # Fonctionnalités centrales
│       │   ├── config.py       # Configuration de l'application
│       │   ├── security.py     # Gestion de l'authentification
│       │   └── events.py       # Système d'événements
│       ├── workflows/          # Moteur de workflows
│       └── services/           # Services partagés
│
├── data-analyzer/              # Agent Data Analyzer
│   ├── Dockerfile
│   ├── main.py                 # Point d'entrée
│   ├── config.py               # Configuration
│   ├── requirements.txt        # Dépendances
│   ├── data_sources/           # Sources de données
│   │   ├── __init__.py
│   │   ├── trends/             # Module d'analyse de tendances
│   │   │   ├── __init__.py
│   │   │   └── trends_analyzer.py
│   │   ├── marketplaces/       # Analyse des marketplaces
│   │   │   ├── __init__.py
│   │   │   ├── amazon.py
│   │   │   └── aliexpress.py
│   │   ├── seo/                # Analyse SEO
│   │   │   ├── __init__.py
│   │   │   └── semrush_analyzer.py
│   │   └── social/             # Analyse des réseaux sociaux
│   │       ├── __init__.py
│   │       └── social_analyzer.py
│   ├── models/                 # Modèles et algorithmes
│   │   ├── __init__.py
│   │   ├── scoring/            # Système de scoring
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── multicriteria.py
│   │   │   └── criteria/       # Critères d'évaluation
│   │   │       ├── market.py
│   │   │       ├── competition.py
│   │   │       └── trend.py
│   │   ├── complementary/      # Analyse de complémentarité
│   │   │   ├── __init__.py
│   │   │   ├── association_rules.py
│   │   │   └── complementary_analyzer.py
│   │   └── forecasting.py      # Prédictions et forecasting
│   ├── tests/                  # Tests unitaires
│   │   ├── __init__.py
│   │   ├── test_trends_analyzer.py
│   │   └── test_complementary_analyzer.py
│   └── tools/                  # Outils utilitaires
│       ├── __init__.py
│       ├── cache_manager.py
│       └── data_visualization.py
│
├── website-builder/            # Agent Website Builder
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── tools/
│       ├── __init__.py
│       ├── api_client.py       # Client pour l'API centralisée
│       ├── shopify_api.py      # Client pour l'API Shopify
│       ├── theme_manager.py    # Gestion des thèmes
│       ├── store_setup.py      # Configuration de la boutique
│       └── navigation.py       # Gestion de la navigation
│
├── content-generator/          # Agent Content Generator
│   ├── Dockerfile
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── generators/             # Générateurs de contenu
│   │   ├── __init__.py
│   │   └── product_description.py
│   ├── optimizers/             # Optimisation SEO
│   │   ├── __init__.py
│   │   └── seo_optimizer.py
│   ├── templates/              # Templates de contenu
│   │   ├── __init__.py
│   │   └── product_templates.py
│   ├── tools/                  # Outils utilitaires
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   └── claude_client.py    # Client pour l'API Claude
│   ├── integrations/           # Intégrations avec autres agents
│   │   ├── __init__.py
│   │   ├── data_analyzer.py
│   │   └── shopify.py
│   └── tests/                  # Tests unitaires
│       ├── __init__.py
│       └── test_product_description.py
│
├── order-manager/              # Agent Order Manager
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── api/                    # API REST interne
│   │   ├── __init__.py
│   │   ├── app.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── health.py
│   │       ├── orders.py
│   │       └── supplier_orders.py
│   ├── integrations/           # Intégrations externes
│   │   ├── __init__.py
│   │   ├── shopify/            # Intégration Shopify
│   │   │   ├── __init__.py
│   │   │   └── client.py
│   │   └── suppliers/          # Intégrations fournisseurs
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── communicator.py
│   │       ├── aliexpress.py
│   │       └── cjdropshipping.py
│   ├── models/                 # Modèles de données
│   │   ├── __init__.py
│   │   ├── order.py
│   │   ├── supplier_order.py
│   │   └── shipping.py
│   ├── services/               # Services métier
│   │   ├── __init__.py
│   │   ├── order_service.py
│   │   ├── order_service_suppliers.py
│   │   └── order_service_delivery.py
│   ├── storage/                # Couche de persistance
│   │   ├── __init__.py
│   │   └── order_repository.py
│   ├── notifications/          # Système de notifications
│   │   ├── __init__.py
│   │   └── notification_manager.py
│   └── tests/                  # Tests unitaires
│       ├── __init__.py
│       ├── test_aliexpress_supplier.py
│       └── test_cjdropshipping_supplier.py
│
└── dashboard/                  # Dashboard d'administration
    ├── css/
    │   └── style.css
    ├── js/
    │   └── dashboard.js
    └── index.html
```

### Dossier /data/

Contient les données persistantes utilisées par le système.

```
/data/
├── postgres/                   # Données PostgreSQL
├── redis/                      # Données Redis
└── cache/                      # Cache système
    ├── data-analyzer/
    └── content-generator/
```

### Dossier /logs/

Contient les logs centralisés du système.

```
/logs/
├── api/
├── data-analyzer/
├── website-builder/
├── content-generator/
├── order-manager/
└── nginx/
```

### Dossier /scripts/

Contient les scripts utilitaires pour le déploiement, la maintenance et l'administration.

```
/scripts/
├── deploy_dashboard.sh         # Déploiement du dashboard
├── optimize_nginx.sh           # Optimisation de la configuration Nginx
└── backup.sh                   # Script de sauvegarde
```

### Fichiers racine

- **docker-compose.yml**: Configuration des services Docker
- **.env**: Variables d'environnement pour le projet
- **.env.example**: Exemple de fichier .env
- **README.md**: Documentation principale du projet

## Conventions de nommage

### Fichiers Python

- **snake_case** pour les modules et packages: `data_analyzer.py`, `shopify_api.py`
- **PascalCase** pour les classes: `TrendsAnalyzer`, `OrderService`
- **snake_case** pour les fonctions et méthodes: `analyze_trends()`, `process_order()`
- **UPPERCASE** pour les constantes: `MAX_RETRIES`, `DEFAULT_TIMEOUT`

### API Endpoints

- Utilisation de noms pluriels pour les ressources: `/orders`, `/products`
- Verbes HTTP appropriés: GET, POST, PUT, DELETE
- Format: `/api/v1/{resource}/{id?}/{action?}`

### Docker

- Images nommées selon le format: `dropship-crew-ai/{service-name}`
- Ports exposés standardisés: API (8000), services (8001-8005)

## Structure des dépendances

Le projet utilise une architecture avec des dépendances claires entre les composants:

1. **API** : Point central, sans dépendance sur les autres services
2. **Agents** : Dépendent uniquement de l'API centrale
3. **Dashboard** : Dépend de l'API centrale

Cette structure évite les dépendances circulaires et facilite le déploiement indépendant des composants.

## Extensions et Plugins

Le système est conçu pour être extensible via des plugins:

- **data-analyzer/plugins/**: Extensions pour l'analyse de données
- **content-generator/templates/**: Templates personnalisables
- **order-manager/integrations/suppliers/**: Intégrations de nouveaux fournisseurs

## Gestion des versions

- Versionnage sémantique (SemVer) pour les releases
- Branches Git organisées selon GitFlow:
  - `main`: Code de production
  - `develop`: Développement actif
  - `feature/*`: Nouvelles fonctionnalités
  - `release/*`: Préparation des releases
  - `hotfix/*`: Corrections urgentes

## Bonnes pratiques et standards de code

- PEP 8 pour le style de code Python
- Documentation des fonctions et classes avec docstrings
- Tests unitaires pour chaque module
- Hooks de pre-commit pour vérifier le style et les tests
- Révision de code obligatoire pour les PR
