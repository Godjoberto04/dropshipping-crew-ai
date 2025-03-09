# Dropshipping Autonome avec Crew AI

Système autonome de dropshipping géré par une flotte d'agents d'IA utilisant Crew AI.

## Description du projet

Ce projet vise à créer un système entièrement autonome pour gérer une boutique de dropshipping en exploitant les capacités de Crew AI. Le système est composé de 5 agents spécialisés qui travaillent ensemble pour analyser le marché, créer et gérer une boutique Shopify, générer du contenu optimisé SEO, gérer les commandes et maintenir le site à jour.

## Informations sur le déploiement actuel

- **Serveur**: Scaleway DEV1-M (Paris)
- **IP**: 163.172.160.102
- **API**: http://163.172.160.102/api/
- **Dashboard**: http://163.172.160.102/
- **Statut actuel**: Phase 4 terminée (Interface utilisateur/Dashboard), Phase 5 en cours (Finalisation de l'agent Data Analyzer)

## Architecture du système

### Agents Crew AI

1. **Data Analyzer**
   - Analyse le marché et les concurrents
   - Identifie les produits à fort potentiel
   - Génère des rapports d'analyse

2. **Website Builder**
   - Configure et personnalise le site Shopify
   - Gère la structure du site et la navigation
   - Optimise l'expérience utilisateur

3. **Content Generator**
   - Crée du contenu optimisé SEO
   - Génère des descriptions de produits
   - Produit des articles de blog et pages catégories

4. **Order Manager**
   - Gère les commandes entrantes
   - Communique avec les fournisseurs
   - Surveille le statut des envois

5. **Site Updater**
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
│   │       ├── scraping.py
│   │       ├── product_analysis.py
│   │       └── trend_identification.py
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

## Plan d'exécution optimisé

Le projet est planifié sur 8 semaines (au lieu des 3-4 mois initialement prévus) :

- **Semaine 1**: ✅ Infrastructure et mise en place initiale
- **Semaine 2**: 🔄 Finalisation du Data Analyzer et début Website Builder
- **Semaine 3**: Content Generator et premiers produits
- **Semaine 4**: Dashboard avancé et optimisations
- **Semaines 5-6**: Order Manager et gestion des commandes
- **Semaines 7-8**: Site Updater et finalisation

## Installation et déploiement

### Prérequis

- Serveur Ubuntu 22.04 LTS
- Docker et Docker Compose
- Compte Claude Pro (pour l'API LLM)
- Compte Shopify Lite

### Installation

1. Cloner ce dépôt
```bash
git clone https://github.com/Godjoberto04/dropshipping-crew-ai.git
cd dropshipping-crew-ai
```

2. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer le fichier .env avec vos propres paramètres
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

## Étapes immédiates (mars 2025)

1. **Finaliser l'agent Data Analyzer**
   ```bash
   docker-compose logs data-analyzer
   # Corriger les problèmes identifiés
   docker-compose restart data-analyzer
   ```

2. **Développer l'agent Website Builder**
   - Créer la structure de base de l'agent
   - Développer les outils d'intégration avec Shopify
   - Implémenter les fonctionnalités principales

3. **Améliorer le Dashboard**
   - Ajouter des visualisations avancées (graphiques)
   - Améliorer l'interface utilisateur
   - Ajouter plus de fonctionnalités interactives

## Documentation

Pour plus de détails, consultez les documents suivants :

- [Suivi détaillé du projet](docs/suivi-detaille.md)
- [Guide d'utilisation des agents Crew AI](docs/agents-crew-ai.md)
- [Documentation API](docs/api-doc.md)

## Coûts du projet

- Infrastructure Scaleway DEV1-M: ~18€/mois
- API LLM: Utilisation de l'abonnement Claude Pro existant (0€ supplémentaire)
- Shopify Lite: ~9€/mois (à implémenter)
- Proxies basiques: 0-10€/mois (à implémenter)
- **Total**: ~27-47€/mois

## Contact et support

Ce projet est développé par un passionné d'IA autonome. Pour toute question ou suggestion, ouvrez une issue sur ce dépôt ou contactez le propriétaire.

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
