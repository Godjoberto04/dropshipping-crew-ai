# Dropshipping Autonome avec Crew AI

Système autonome de dropshipping géré par une flotte d'agents d'IA.

## Description du projet

Ce projet vise à créer un système entièrement autonome pour gérer une boutique de dropshipping en exploitant les capacités de Claude et des agents IA. Le système est composé de 5 agents spécialisés qui travaillent ensemble pour analyser le marché, créer et gérer une boutique Shopify, générer du contenu optimisé SEO, gérer les commandes et maintenir le site à jour.

## Informations sur le déploiement actuel

- **Serveur**: Scaleway DEV1-M (Paris)
- **IP**: 163.172.160.102
- **API**: http://163.172.160.102/api/
- **Dashboard**: http://163.172.160.102/
- **Statut actuel**: Agent Data Analyzer entièrement opérationnel, Phase "Website Builder" à démarrer

## Architecture du système

### Agents

1. **Data Analyzer** ✅
   - Analyse le marché et les concurrents
   - Identifie les produits à fort potentiel
   - Génère des rapports d'analyse

2. **Website Builder** 🔄
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
│   │       ├── api_client.py
│   │       ├── scraping.py
│   │       └── trend_analysis.py
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
- Mise en place d'un système d'analyse en trois phases : scraping, analyse de produits, analyse de tendances
- Correction des problèmes de dépendances et de compatibilité
- Configuration de l'infrastructure avec Docker, Redis et PostgreSQL

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
# Éditer le fichier .env avec vos propres paramètres, notamment votre clé API Claude
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

## Comment utiliser l'agent Data Analyzer

Une fois le système déployé, vous pouvez utiliser l'API pour déclencher des analyses de marché :

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

L'API retournera un ID de tâche que vous pouvez utiliser pour suivre la progression :

```bash
curl "http://votre-serveur:8000/tasks/{task_id}"
```

Les résultats d'analyse seront disponibles une fois la tâche terminée :

```bash
curl "http://votre-serveur:8000/analysis/results/latest"
```

## Étapes suivantes pour le développement

1. **Développer l'agent Website Builder** 
   - Suivre le plan détaillé dans docs/plan-website-builder.md
   - Implémenter l'intégration avec l'API Shopify
   - Configurer la création automatisée de boutiques

2. **Améliorer le dashboard**
   - Ajouter des visualisations plus avancées (graphiques)
   - Développer des interfaces pour les autres agents
   - Mettre en place un système de notifications

## Documentation

Pour plus de détails, consultez les documents suivants :

- [Suivi détaillé du projet](docs/suivi-detaille.md)
- [Plan de développement de l'agent Website Builder](docs/plan-website-builder.md)
- [Documentation API](docs/api-doc.md)

## Coûts du projet

- Infrastructure Scaleway DEV1-M: ~18€/mois
- API LLM: Utilisation de l'abonnement Claude Pro existant (0€ supplémentaire)
- Shopify Lite: ~9€/mois (à implémenter)
- Proxies basiques: 0-10€/mois (à implémenter)
- **Total**: ~27-47€/mois

## Dépannage

Si vous rencontrez des problèmes lors du déploiement, voici quelques solutions :

1. **Problème d'accès à l'API**: Vérifiez que le conteneur est bien démarré avec `docker-compose logs -f api`
2. **Agent Data Analyzer ne démarre pas**: Vérifiez que votre clé API Claude est correctement configurée dans le fichier `.env`
3. **Dépendances manquantes**: Si vous rencontrez des erreurs liées aux dépendances, reconstruisez les conteneurs avec `docker-compose build --no-cache`

## Contact et support

Ce projet est développé par un passionné d'IA autonome. Pour toute question ou suggestion, ouvrez une issue sur ce dépôt ou contactez le propriétaire.

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
