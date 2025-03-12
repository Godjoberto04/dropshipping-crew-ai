# Dropshipping Autonome avec Crew AI

Système autonome de dropshipping géré par une flotte d'agents d'IA.

## Description du projet

Ce projet vise à créer un système entièrement autonome pour gérer une boutique de dropshipping en exploitant les capacités de Claude et des agents IA. Le système est composé de 5 agents spécialisés qui travaillent ensemble pour analyser le marché, créer et gérer une boutique Shopify, générer du contenu optimisé SEO, gérer les commandes et maintenir le site à jour.

## Informations sur le déploiement actuel

- **Serveur**: Scaleway DEV1-M (Paris)
- **IP**: 163.172.160.102
- **API**: http://163.172.160.102/api/
- **Dashboard**: http://163.172.160.102/
- **Statut actuel**: Agents Data Analyzer, Website Builder et Content Generator opérationnels, Agent Order Manager implémenté

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

3. **Content Generator** ✅
   - Crée du contenu optimisé SEO
   - Génère des descriptions de produits
   - Produit des articles de blog et pages catégories

4. **Order Manager** ✅
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
- **Orchestration**: API centralisée avec moteur de workflows ⚠️ **Nouveau!**

## Changements récents

### Mars 2025
- **NOUVEAU** 🔥 : Implémentation complète de l'agent Order Manager avec gestion des commandes, communication fournisseurs et suivi d'expédition
- **NOUVEAU** 🔥 : Suite complète de tests unitaires pour l'agent Order Manager (processeur de commandes, tracker d'expédition, communicateur fournisseurs)
- **NOUVEAU** 🔥 : Support multi-fournisseurs (AliExpress, CJ Dropshipping) avec formatage spécifique des commandes
- **NOUVEAU** 🔥 : Système de suivi d'expédition avec mise à jour automatique des statuts dans Shopify
- **NOUVEAU** 🔥 : Système de notification par email pour les événements importants (nouvelles commandes, expéditions, livraisons)
- Suite complète de tests unitaires pour l'agent Content Generator (intégrations, client API, templates, etc.)
- Implémentation complète de l'agent Content Generator avec capacité de génération de descriptions de produits optimisées SEO
- Support pour plusieurs niches (mode, électronique, maison, beauté) avec templates spécialisés
- Plan d'amélioration de l'API pour l'orchestration des workflows entre agents
- Adoption d'une stratégie d'intégration de ressources communautaires de qualité pour accélérer le développement

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

### Agent Order Manager

Pour traiter une commande :

```bash
# Exemple avec curl
curl -X POST "http://votre-serveur:8003/process-order" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 12345,
    "action": "process",
    "manual_review": true
  }'
```

Pour suivre une expédition :

```bash
# Exemple avec curl
curl -X POST "http://votre-serveur:8003/track-shipment" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 12345,
    "tracking_number": "TRK123456789", 
    "carrier": "dhl"
  }'
```

## Documentation

Pour plus de détails, consultez les documents suivants :

- [Guide de l'agent Order Manager](docs/order-manager-guide.md) ✨ **NOUVEAU** ✨
- [Plan d'amélioration de l'API pour l'orchestration](docs/plan-amelioration-api-orchestration.md)
- [Stratégie d'intégration des ressources communautaires](docs/community-resources-integration.md)
- [Plan d'amélioration de l'agent Website Builder](docs/plan-website-builder-amelioration.md)
- [Plan d'amélioration de l'agent Data Analyzer](docs/plan-data-analyzer-amelioration.md)
- [Guide de l'agent Content Generator](docs/content-generator-guide.md)
- [Guide de l'agent Website Builder](docs/website-builder-guide.md)
- [Documentation API](docs/api-doc-suite.md)

## Prochaines étapes

1. **Développement de l'agent Site Updater**
   - Création du cinquième et dernier agent du système
   - Implémentation des fonctionnalités de mise à jour automatique des prix et stocks
   - Intégration avec les outils de surveillance des concurrents

2. **Amélioration de l'API pour l'orchestration**
   - Implémentation du moteur de workflows
   - Développement du système d'événements et déclencheurs
   - Extension du tableau de bord pour le monitoring des workflows

3. **Extension de l'agent Content Generator** 
   - Phase 2 : Ajout des générateurs de pages catégories et articles de blog
   - Optimisation SEO avancée et adaptateurs de niche spécialisés
   - Intégration complète avec le système de workflows

4. **Ajout de fonctionnalités avancées pour l'agent Order Manager**
   - Système de gestion des retours et remboursements
   - Algorithmes d'optimisation des expéditions
   - Intégration avec davantage de fournisseurs dropshipping

## Coûts du projet

- Infrastructure Scaleway DEV1-M: ~18€/mois
- API LLM: Utilisation de l'abonnement Claude Pro existant (0€ supplémentaire)
- Shopify Lite: ~9€/mois
- Proxies basiques: 0-10€/mois (optionnel)
- **Total**: ~27-37€/mois

## Dépannage

Si vous rencontrez des problèmes lors du déploiement :

1. **Problème d'accès à l'API**: Vérifiez que le conteneur est bien démarré avec `docker-compose logs -f api`
2. **Erreurs d'API Shopify**: Vérifiez que vos clés et tokens sont corrects et que votre compte Shopify est actif
3. **Dépendances manquantes**: Reconstruisez les conteneurs avec `docker-compose build --no-cache`
4. **Order Manager ne traite pas les commandes**: Vérifiez les webhooks Shopify et les permissions API

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 📢 Notes pour le prochain chat

Pour la prochaine session, voici ce qu'il reste à implémenter ou à mettre à jour :

1. Commencer le développement du cinquième agent (Site Updater)
2. Étendre l'agent Content Generator avec des fonctionnalités pour les articles de blog
3. Implémenter les améliorations de l'API pour l'orchestration des workflows
