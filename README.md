# Dropshipping Autonome avec Crew AI

Système autonome de dropshipping géré par une flotte d'agents d'IA.

## Description du projet

Ce projet vise à créer un système entièrement autonome pour gérer une boutique de dropshipping en exploitant les capacités de Claude et des agents IA. Le système est composé de 5 agents spécialisés qui travaillent ensemble pour analyser le marché, créer et gérer une boutique Shopify, générer du contenu optimisé SEO, gérer les commandes et maintenir le site à jour.

## Informations sur le déploiement actuel

- **Serveur**: Scaleway DEV1-M (Paris)
- **IP**: 163.172.160.102
- **API**: http://163.172.160.102/api/
- **Dashboard**: http://163.172.160.102/
- **Statut actuel**: Agent Data Analyzer opérationnel, Agent Website Builder implémenté et prêt à être configuré

## Architecture du système

### Agents

1. **Data Analyzer** ✅
   - Analyse le marché et les concurrents
   - Identifie les produits à fort potentiel
   - Génère des rapports d'analyse

2. **Website Builder** ✅
   - Configure et personnalise le site Shopify
   - Gère la structure du site et la navigation
   - Optimise l'expérience utilisateur

3. **Content Generator** ⏳
   - Crée du contenu optimisé SEO
   - Génère des descriptions de produits
   - Produit des articles de blog et pages catégories

4. **Order Manager** ⏳
   - Gère les commandes entrantes
   - Communique avec les fournisseurs
   - Surveille le statut des envois

5. **Site Updater** ⏳
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

## Structure du projet

```
/opt/dropship-crew-ai/
├── config/
│   ├── prometheus/
│   │   └── prometheus.yml
├── services/
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
│   ├── api/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app/
│   │       └── main.py
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
- Migration de l'agent Data Analyzer des outils CrewAI/LangChain vers des classes Python standards pour une meilleure stabilité
- Implémentation de l'agent Website Builder pour Shopify avec intégration API complète
- Mise à jour de l'API pour prendre en charge les opérations du Website Builder
- Mise en place d'un système modulaire pour la gestion des thèmes, la configuration de la boutique et la navigation

## Installation et déploiement

### Prérequis

- Serveur Ubuntu 22.04 LTS
- Docker et Docker Compose
- Compte Claude Pro (pour l'API LLM)
- Compte Shopify Lite (pour l'agent Website Builder)

### Installation

1. Cloner ce dépôt
```bash
git clone https://github.com/Godjoberto04/dropshipping-crew-ai.git
cd dropshipping-crew-ai
```

2. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer le fichier .env avec vos paramètres (clé API Claude, crédentiels Shopify, etc.)
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

Pour ajouter un produit à la boutique :

```bash
curl -X POST "http://votre-serveur:8000/agents/website-builder/action" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add_product",
    "product_data": {
      "title": "Produit Exemple",
      "description": "Description du produit...",
      "variants": [
        {
          "price": "19.99",
          "inventory_quantity": 100
        }
      ]
    }
  }'
```

## Prochaines étapes

1. **Configuration d'un compte Shopify** 
   - Créer un compte Shopify et sélectionner un forfait (voir [guide détaillé](docs/website-builder-guide.md))
   - Obtenir les clés API et tokens nécessaires
   - Configurer les variables d'environnement Shopify dans le fichier .env

2. **Développement de l'agent Content Generator** 
   - Créer l'architecture pour l'agent suivant
   - Développer les outils de génération de contenu SEO
   - Intégrer avec les agents existants

## Documentation

Pour plus de détails, consultez les documents suivants :

- [Guide de l'agent Website Builder](docs/website-builder-guide.md) ⚠️ **Nouveau!**
- [Plan de développement de l'agent Website Builder](docs/plan-website-builder.md)
- [Documentation API](docs/api-doc.md)

## Coûts du projet

- Infrastructure Scaleway DEV1-M: ~18€/mois
- API LLM: Utilisation de l'abonnement Claude Pro existant (0€ supplémentaire)
- Shopify Lite: ~9€/mois
- Proxies basiques: 0-10€/mois (optionnel)
- **Total**: ~27-37€/mois

## Dépannage

Si vous rencontrez des problèmes lors du déploiement :

1. **Problème d'accès à l'API**: Vérifiez que le conteneur est bien démarré avec `docker-compose logs -f api`
2. **Agent Data Analyzer ou Website Builder ne démarre pas**: Vérifiez les variables d'environnement dans `.env`
3. **Erreurs d'API Shopify**: Vérifiez que vos clés et tokens sont corrects et que votre compte Shopify est actif
4. **Dépendances manquantes**: Reconstruisez les conteneurs avec `docker-compose build --no-cache`

## Contact et support

Ce projet est développé par un passionné d'IA autonome. Pour toute question ou suggestion, ouvrez une issue sur ce dépôt ou contactez le propriétaire.

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
