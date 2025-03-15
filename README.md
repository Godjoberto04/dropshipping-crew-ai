# Dropshipping Autonome avec Crew AI

Système autonome de dropshipping géré par une flotte d'agents d'IA utilisant Crew AI.

## Description du projet

Ce projet vise à créer un système entièrement autonome pour gérer une boutique de dropshipping en exploitant les capacités de Claude et des agents IA. Le système est composé de 5 agents spécialisés qui travaillent ensemble pour analyser le marché, créer et gérer une boutique Shopify, générer du contenu optimisé SEO, gérer les commandes et maintenir le site à jour.

## Informations sur le déploiement actuel

- **Serveur**: Scaleway DEV1-M (Paris)
- **IP**: 163.172.160.102
- **API**: http://163.172.160.102/api/
- **Dashboard**: http://163.172.160.102/
- **Statut actuel**: Agents Data Analyzer, Website Builder, Content Generator et Order Manager opérationnels

## Architecture du système

### Agents

1. **Data Analyzer** ✅
   - Analyse le marché et les concurrents
   - Identifie les produits à fort potentiel
   - Génère des rapports d'analyse
   - Limitations actuelles: Analyse superficielle, sources de données limitées, absence de modèles prédictifs avancés

2. **Website Builder** ✅
   - Configure et personnalise le site Shopify
   - Gère la structure du site et la navigation
   - Optimise l'expérience utilisateur
   - Limitations actuelles: Fonctionnalités basiques, optimisation SEO limitée, absence d'A/B testing

3. **Content Generator** ✅
   - Crée du contenu optimisé SEO
   - Génère des descriptions de produits
   - Architecture asynchrone moderne
   - Tests unitaires complets
   - Limitations actuelles: Actuellement limité aux descriptions de produits

4. **Order Manager** ✅
   - Gestion complète des commandes e-commerce
   - Intégration avec les fournisseurs dropshipping (AliExpress, CJ Dropshipping)
   - API REST complète pour la gestion des commandes
   - Synchronisation avec Shopify
   - Suivi des commandes et expéditions
   - Tests unitaires complets pour les intégrations fournisseurs
   - Système de notification pour informer les clients des changements de statut

5. **Site Updater** 🔜 (planifié)
   - Actualise les prix selon la concurrence
   - Met à jour les stocks
   - Ajuste les paramètres du site dynamiquement

### Infrastructure technique

- **Serveur**: Scaleway DEV1-M (3 vCPUs, 4 GB RAM)
- **OS**: Ubuntu 22.04 LTS
- **Base de données**: PostgreSQL (Docker)
- **Cache**: Redis (Docker)
- **API**: FastAPI (Python, Docker)
- **Frontend**: Dashboard HTML/CSS/JS (Nginx)
- **Proxy**: Nginx (hors Docker)
- **E-commerce**: Shopify Lite
- **Orchestration**: API centralisée avec moteur de workflows en développement

### Architecture d'API centralisée

Le projet utilise une API centralisée qui comprend:
- **Endpoints REST**: Communication entre les agents et avec le dashboard
- **Gestionnaire de tâches**: Coordination des opérations complexes
- **Moteur de workflows**: Orchestration des flux entre agents (en développement)
- **Système d'événements**: Communication asynchrone entre agents (en développement)
- **Système d'authentification**: Sécurisation des opérations

## Structure du projet

```
/opt/dropship-crew-ai/
├── config/
│   ├── prometheus/
│   │   └── prometheus.yml
├── services/
│   ├── api/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app/
│   │       └── main.py
│   ├── crew-ai/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── api_client.py
│   │       ├── scraping.py
│   │       └── trend_analysis.py
│   ├── website-builder/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── api_client.py
│   │       ├── shopify_api.py
│   │       ├── theme_manager.py
│   │       ├── store_setup.py
│   │       └── navigation.py
│   ├── content-generator/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── requirements.txt
│   │   ├── generators/
│   │   │   ├── __init__.py
│   │   │   └── product_description.py
│   │   ├── optimizers/
│   │   │   ├── __init__.py
│   │   │   └── seo_optimizer.py
│   │   ├── templates/
│   │   │   ├── __init__.py
│   │   │   └── product_templates.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── api_client.py
│   │   │   └── claude_client.py
│   │   ├── integrations/
│   │   │   ├── __init__.py
│   │   │   ├── data_analyzer.py
│   │   │   └── shopify.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_api_client.py
│   │       ├── test_claude_client.py
│   │       ├── test_config.py
│   │       ├── test_main.py
│   │       ├── test_data_analyzer_integration.py
│   │       ├── test_shopify_integration.py
│   │       ├── test_product_description.py
│   │       ├── test_product_templates.py
│   │       └── test_seo_optimizer.py
│   ├── order-manager/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── app.py
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py
│   │   │   │   ├── orders.py
│   │   │   │   └── supplier_orders.py
│   │   │   └── utils.py
│   │   ├── integrations/
│   │   │   ├── __init__.py
│   │   │   ├── shopify/
│   │   │   │   ├── __init__.py
│   │   │   │   └── client.py
│   │   │   └── suppliers/
│   │   │       ├── __init__.py
│   │   │       ├── base.py
│   │   │       ├── communicator.py
│   │   │       ├── aliexpress.py
│   │   │       └── cjdropshipping.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── order.py
│   │   │   ├── supplier_order.py
│   │   │   └── shipping.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── order_service.py
│   │   │   ├── order_service_suppliers.py
│   │   │   └── order_service_delivery.py
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   └── order_repository.py
│   │   ├── notifications/
│   │   │   ├── __init__.py
│   │   │   └── notification_manager.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_aliexpress_supplier.py
│   │       └── test_cjdropshipping_supplier.py
│   └── dashboard/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── dashboard.js
│       └── index.html
├── data/
├── logs/
├── scripts/
│   ├── deploy_dashboard.sh
│   ├── optimize_nginx.sh
│   └── backup.sh
├── .env
└── docker-compose.yml
```

## Changements récents

### Mars 2025
- **NOUVEAU** 🔥 : Intégration complète de l'agent Order Manager avec support pour AliExpress et CJ Dropshipping
- **NOUVEAU** 🔥 : Tests unitaires pour les intégrations AliExpress et CJ Dropshipping
- **NOUVEAU** 🔥 : Documentation détaillée pour l'agent Order Manager et ses intégrations
- **NOUVEAU** 🔥 : Architecture modulaire pour l'intégration avec les fournisseurs dropshipping
- **NOUVEAU** 🔥 : Système de notification pour informer les clients des changements de statut des commandes
- **NOUVEAU** 🔥 : Suite complète de tests unitaires pour l'agent Content Generator (intégrations, client API, templates, etc.)
- **NOUVEAU** 🔥 : Implémentation complète de l'agent Content Generator avec capacité de génération de descriptions de produits optimisées SEO
- **NOUVEAU** 🔥 : Support pour plusieurs niches (mode, électronique, maison, beauté) avec templates spécialisés
- **NOUVEAU** 🔥 : Plans détaillés d'amélioration pour l'agent Data Analyzer (voir docs/plan-data-analyzer-amelioration.md)
- **NOUVEAU** 🔥 : Plan d'amélioration de l'API pour l'orchestration des workflows entre agents
- **NOUVEAU** 🔥 : Mise à jour du dashboard avec JavaScript amélioré et visualisations des données
- **NOUVEAU** 🔥 : Adoption d'une stratégie d'intégration de ressources communautaires de qualité pour accélérer le développement
- **NOUVEAU** 🔥 : Développement des tests unitaires pour les intégrations API et les templates de produits
- Migration de l'agent Data Analyzer des outils CrewAI/LangChain vers des classes Python standards pour une meilleure stabilité
- Implémentation de l'agent Website Builder pour Shopify avec intégration API complète
- Mise à jour de l'API pour prendre en charge les opérations du Website Builder
- Mise en place d'un système modulaire pour la gestion des thèmes, la configuration de la boutique et la navigation

## Politique d'intégration des composants communautaires

Le projet adopte désormais une approche hybride qui privilégie l'intégration et l'adaptation de composants communautaires de qualité lorsqu'ils existent, plutôt que de tout développer à partir de zéro. Cette stratégie permet :

- D'accélérer le développement des agents
- D'améliorer la robustesse en utilisant des composants éprouvés
- De concentrer nos efforts sur les aspects à valeur ajoutée

Pour plus d'informations, consultez notre [Stratégie d'intégration des ressources communautaires](docs/community-resources-integration.md) et notre [Résumé des intégrations](docs/resume-integration-composants-communautaires.md).

## Installation et déploiement

### Prérequis

- Serveur Ubuntu 22.04 LTS
- Docker et Docker Compose
- Compte Claude Pro (pour l'API LLM)
- Compte Shopify Lite (pour l'agent Website Builder)
- Comptes API AliExpress et CJ Dropshipping (pour l'agent Order Manager)

### Installation

1. Cloner ce dépôt
```bash
git clone https://github.com/Godjoberto04/dropshipping-crew-ai.git
cd dropshipping-crew-ai
```

2. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer le fichier .env avec vos paramètres (clé API Claude, crédentiels Shopify, crédentiels fournisseurs, etc.)
```

3. Déployer les services
```bash
docker-compose up -d
```

4. Installer et configurer Nginx
```bash
sudo bash scripts/deploy_dashboard.sh
```

5. Optimiser Nginx (facultatif)
```bash
sudo bash scripts/optimize_nginx.sh
```

## Comment utiliser les agents

### Agent Data Analyzer

Pour déclencher une analyse de marché :

```bash
# Exemple avec curl
curl -X POST "http://votre-serveur:8000/agents/data-analyzer/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://example-shop.com/category/accessories"],
    "market_segment": "smartphone accessories",
    "min_margin": 30.0
  }'
```

### Agent Website Builder

Pour configurer une nouvelle boutique Shopify :

```bash
# Exemple avec curl
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
          "secondary": "#10b981"
        }
      },
      "navigation": {
        "main_menu": [
          {"title": "Accueil", "url": "/"},
          {"title": "Produits", "url": "/collections/all"}
        ]
      }
    }
  }'
```

### Agent Content Generator

Pour générer une description de produit :

```bash
# Exemple avec curl
curl -X POST "http://votre-serveur:8000/agents/content-generator/action" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "generate_product_description",
    "product_data": {
      "name": "Écouteurs Bluetooth Premium",
      "features": ["Autonomie 24h", "Suppression active du bruit", "Résistant à l'eau"],
      "price": "89.99",
      "brand": "TechSound"
    },
    "tone": "persuasif",
    "niche": "electronics",
    "language": "fr",
    "auto_publish": false
  }'
```

Pour optimiser un contenu existant :

```bash
curl -X POST "http://votre-serveur:8000/agents/content-generator/action" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "optimize_content",
    "content": "Votre contenu à optimiser...",
    "content_type": "product_description",
    "keywords": ["mot-clé 1", "mot-clé 2"]
  }'
```

### Agent Order Manager

Pour gérer les commandes via l'API :

```bash
# Obtenir le statut d'une commande
curl -X GET "http://votre-serveur:8000/agents/order-manager/orders/123456789" \
  -H "Content-Type: application/json"

# Rechercher des produits sur AliExpress
curl -X POST "http://votre-serveur:8000/agents/order-manager/suppliers/search" \
  -H "Content-Type: application/json" \
  -d '{
    "supplier": "aliexpress",
    "query": "smartphone accessories",
    "page": 1,
    "limit": 20
  }'

# Rechercher des produits sur CJ Dropshipping
curl -X POST "http://votre-serveur:8000/agents/order-manager/suppliers/search" \
  -H "Content-Type: application/json" \
  -d '{
    "supplier": "cjdropshipping",
    "query": "smartphone accessories",
    "page": 1,
    "limit": 20
  }'

# Créer une commande fournisseur
curl -X POST "http://votre-serveur:8000/agents/order-manager/supplier-orders" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "shopify_12345",
    "supplier": "aliexpress",
    "product_id": "aliexpress_product_id",
    "quantity": 1,
    "shipping_address": {
      "name": "Client Test",
      "address1": "123 Test Street",
      "city": "Test City",
      "zip": "12345",
      "country": "FR"
    }
  }'

# Vérifier le statut d'expédition
curl -X GET "http://votre-serveur:8000/agents/order-manager/shipments/tracking-id" \
  -H "Content-Type: application/json"

# Annuler une commande
curl -X POST "http://votre-serveur:8000/agents/order-manager/orders/123456789/cancel" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Demande client : changement d\'avis"
  }'
```

## Tests unitaires

Le projet dispose maintenant d'une suite complète de tests unitaires pour les services Content Generator et Order Manager. Pour exécuter les tests :

```bash
# Tests de l'agent Content Generator
cd services/content-generator
python -m unittest discover -s tests

# Tests de l'agent Order Manager
cd services/order-manager
python -m unittest discover -s tests

# Exécuter un test spécifique
python -m unittest tests.test_aliexpress_supplier
python -m unittest tests.test_cjdropshipping_supplier
```

Les modules testés comprennent :
- Client API pour l'interaction avec l'API centrale
- Client Claude pour la génération de contenu
- Intégrations avec Data Analyzer et Shopify
- Générateur de descriptions produit
- Templates spécifiques par niche
- Optimiseur SEO
- Intégration AliExpress
- Intégration CJ Dropshipping

## Points d'amélioration identifiés

1. **Uniformisation des approches de programmation**
   - Disparité entre styles synchrone (Data Analyzer, Website Builder) et asynchrone (Content Generator, Order Manager)
   - Documenter les choix techniques ou uniformiser l'approche

2. **Tests unitaires à compléter**
   - Étendre les tests aux agents Data Analyzer et Website Builder

3. **Validation des données**
   - Renforcer la validation des entrées, particulièrement pour les API

4. **Système de workflow**
   - Implémenter le moteur de workflow pour améliorer la coordination entre agents

## Prochaines étapes

1. **Amélioration de l'agent Order Manager**
   - Intégration avec d'autres fournisseurs dropshipping
   - Automatisation complète du cycle de vie des commandes
   - Système avancé de notifications clients
   - Dashboard dédié pour le suivi des commandes

2. **Amélioration de l'agent Data Analyzer**
   - Implémentation du plan d'amélioration détaillé (voir [plan complet](docs/plan-data-analyzer-amelioration.md))
   - Intégration de PyTrends pour l'analyse de tendances Google
   - Développement du système de scoring multicritères pondéré
   - Ajout des mécanismes de validation et d'apprentissage

3. **Amélioration de l'agent Website Builder**
   - Implémentation du plan d'amélioration (voir [plan complet](docs/plan-website-builder-amelioration.md))
   - Génération intelligente de sites avec templates par niche
   - Optimisation SEO intégrée
   - Amélioration des éléments de conversion (CRO)

4. **Extension de l'agent Content Generator** 
   - Phase 2 : Ajout des générateurs de pages catégories et articles de blog
   - Optimisation SEO avancée et adaptateurs de niche spécialisés
   - Intégration complète avec le système de workflows

5. **Amélioration de l'API pour l'orchestration**
   - Implémentation du moteur de workflows
   - Développement du système d'événements et déclencheurs
   - Extension du tableau de bord pour le monitoring des workflows
   
6. **Développement de l'agent Site Updater**
   - Implémentation d'un système de surveillance des prix concurrents
   - Automatisation des mises à jour de stocks et de prix
   - Optimisation continue des pages produits basée sur l'analyse des performances

## Documentation

Pour plus de détails, consultez les documents suivants :

- [Guide de l'agent Order Manager](docs/order-manager-guide.md)
- [Plan de fusion de l'agent Order Manager](docs/order-manager-merge-plan.md)
- [Vérification post-fusion](docs/verification-post-fusion-order-manager.md)
- [Plan d'amélioration de l'agent Data Analyzer](docs/plan-data-analyzer-amelioration.md)
- [Plan d'amélioration de l'agent Website Builder](docs/plan-website-builder-amelioration.md)
- [Plan d'amélioration de l'API pour l'orchestration](docs/plan-amelioration-api-orchestration.md)
- [Stratégie d'intégration des ressources communautaires](docs/community-resources-integration.md)
- [Plan du Content Generator](docs/plan-content-generator.md)
- [Guide de l'agent Content Generator](docs/content-generator-guide.md)
- [Guide de l'agent Website Builder](docs/website-builder-guide.md)
- [Documentation API](docs/api-doc-suite.md)
- [Tests de l'agent Content Generator](docs/tests-content-generator.md)

## Coûts du projet

- Infrastructure Scaleway DEV1-M: ~18€/mois
- API LLM: Utilisation de l'abonnement Claude Pro existant (0€ supplémentaire)
- Shopify Lite: ~9€/mois
- APIs fournisseurs (AliExpress, CJ Dropshipping): ~0-20€/mois selon l'utilisation
- Proxies basiques: 0-10€/mois (optionnel)
- **Total**: ~27-57€/mois

## Dépannage

Si vous rencontrez des problèmes lors du déploiement :

1. **Problème d'accès à l'API**: Vérifiez que le conteneur est bien démarré avec `docker-compose logs -f api`
2. **Agent ne démarre pas**: Vérifiez les variables d'environnement dans `.env`
3. **Erreurs d'API Shopify**: Vérifiez que vos clés et tokens sont corrects et que votre compte Shopify est actif
4. **Erreurs d'API Claude**: Vérifiez votre clé API Claude et votre abonnement Claude Pro
5. **Erreurs d'API fournisseurs**: Vérifiez les clés d'API AliExpress/CJ Dropshipping dans les variables d'environnement
6. **Dépendances manquantes**: Reconstruisez les conteneurs avec `docker-compose build --no-cache`
7. **Tests unitaires qui échouent**: Vérifiez les dépendances et la configuration dans les dossiers de tests
8. **Problèmes avec Order Manager**: Vérifiez la configuration et les logs avec `docker-compose logs -f order-manager`

## Contact et support

Ce projet est développé par un passionné d'IA autonome. Pour toute question ou suggestion, ouvrez une issue sur ce dépôt ou contactez le propriétaire.

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 📢 Notes pour le prochain chat

Pour la prochaine session, voici ce qu'il reste à implémenter ou à mettre à jour :

1. Perfectionner l'intégration de l'agent Order Manager:
   - Améliorer l'interface utilisateur pour le suivi des commandes dans le dashboard
   - Ajouter l'intégration avec d'autres fournisseurs dropshipping
   - Optimiser la gestion des cas d'erreur et la reprise automatique

2. Commencer la mise en œuvre du plan d'amélioration de l'agent Data Analyzer
3. Étendre l'agent Content Generator pour les articles de blog
4. Implémenter le moteur de workflow dans l'API d'orchestration
5. Planifier l'architecture de l'agent Site Updater
