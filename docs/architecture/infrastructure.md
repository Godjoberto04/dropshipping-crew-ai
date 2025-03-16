# Infrastructure technique

Ce document détaille l'infrastructure technique qui soutient le système autonome de dropshipping.

## Vue d'ensemble

Le système repose sur une architecture moderne, conteneurisée et évolutive, conçue pour faciliter le déploiement, la maintenance et la mise à l'échelle. L'infrastructure est composée de plusieurs couches :

1. **Serveur et hébergement**
2. **Conteneurisation et orchestration**
3. **Bases de données et stockage**
4. **API et communication**
5. **Frontend et interface utilisateur**
6. **Intégrations externes**
7. **Monitoring et logging**

## Serveur et hébergement

### Configuration actuelle
- **Fournisseur**: Scaleway
- **Type d'instance**: DEV1-M
- **Spécifications**: 3 vCPUs, 4 GB RAM
- **Stockage**: 40 GB SSD NVMe
- **Système d'exploitation**: Ubuntu 22.04 LTS
- **Localisation**: Paris, France
- **IP**: 163.172.160.102

### Sécurité
- Configuration de pare-feu avec UFW
- Connexion SSH avec clés cryptographiques uniquement
- Mises à jour automatiques des packages de sécurité
- Fail2ban pour protection contre les attaques par force brute

## Conteneurisation et orchestration

### Docker
Tous les services du système sont conteneurisés à l'aide de Docker pour assurer une isolation et une cohérence entre les environnements.

**Configuration Docker**:
- Docker version 24.0.5+
- docker-compose version 2.20.2+
- Images basées sur Python 3.11 Alpine pour minimiser la taille
- Volumes pour la persistance des données
- Réseau dédié pour la communication inter-conteneurs

### Structure des conteneurs
- **api**: FastAPI, point d'entrée central du système
- **data-analyzer**: Agent d'analyse de données
- **website-builder**: Agent de construction de site
- **content-generator**: Agent de génération de contenu
- **order-manager**: Agent de gestion des commandes
- **postgres**: Base de données PostgreSQL
- **redis**: Cache et broker de messages Redis
- **nginx**: Proxy inverse et serveur pour le dashboard

## Bases de données et stockage

### PostgreSQL
- **Version**: 15.x
- **Configuration**: Optimisée pour petite instance (max_connections=50, shared_buffers ajustés)
- **Schémas**: Séparés par agent pour l'isolation des données
- **Sauvegardes**: Quotidiennes, stockées localement et exportées

### Redis
- **Version**: 7.x
- **Utilisations**:
  - Système de cache pour les données fréquemment consultées
  - File d'attente pour les tâches asynchrones
  - Pub/Sub pour la communication entre agents
  - Stockage des sessions

### Stockage de fichiers
- Stockage local pour les fichiers statiques
- Volume Docker partagé pour les assets communs
- Futur plan: Migration vers stockage cloud (S3 compatible)

## API et communication

### FastAPI
- API REST centrale basée sur FastAPI
- Documentation OpenAPI (Swagger) automatique
- Endpoints versionnés
- Middlewares pour l'authentification, logging et CORS

### Communication inter-agents
- Communication synchrone via API REST
- Communication asynchrone via Redis Pub/Sub
- Files d'attente pour les tâches longues
- Architecture en cours d'évolution vers un système d'événements

## Frontend et interface utilisateur

### Dashboard
- **Technologie**: HTML/CSS/JS avec framework léger
- **Hébergement**: Servi par Nginx
- **Fonctionnalités**:
  - Tableau de bord pour visualiser les KPIs
  - Interface pour déclencher et surveiller les tâches
  - Visualisations des données et tendances
  - Configuration des agents

### Serveur Web
- **Nginx**:
  - Proxy inverse pour les services
  - Serveur HTTP pour le dashboard
  - Configuration avec compression gzip
  - Cache pour les assets statiques
  - SSL/TLS via Let's Encrypt

## Intégrations externes

### Shopify
- Intégration via API REST officielle
- Webhooks pour les notifications en temps réel
- Synchronisation bidirectionnelle des produits et commandes

### API Claude
- Intégration avec l'API Claude pour la génération de contenu
- Système de cache pour optimiser l'utilisation

### Fournisseurs dropshipping
- Intégration avec AliExpress via API officielle
- Intégration avec CJ Dropshipping via API officielle
- Architecture extensible pour ajouter d'autres fournisseurs

### Autres intégrations
- PyTrends pour l'analyse Google Trends
- Intégration future avec SEMrush/Ahrefs (en développement)

## Monitoring et logging

### Logging
- Logs centralisés via Docker logging driver
- Rotation des logs configurée
- Niveaux de log différenciés par environnement

### Monitoring
- Prometheus pour la collecte de métriques
- Alerting basique sur les métriques critiques
- Monitoring des ressources système et santé des conteneurs

## Déploiement et CI/CD

### Processus de déploiement
- Déploiement manuel via scripts shell
- Pull des images depuis GitHub
- Tests de santé post-déploiement

### Plan futur CI/CD
- Pipeline GitHub Actions pour tests automatisés
- Déploiement automatique après tests réussis
- Gestion des versions et des releases

## Capacité et performances

### Limites actuelles
- Capacité à gérer jusqu'à ~500 produits
- Jusqu'à ~100 commandes par jour
- Temps de réponse API < 500ms pour 95% des requêtes

### Évolutivité
- Architecture conçue pour faciliter la mise à l'échelle horizontale
- Points chauds identifiés: génération de contenu et analyse de données
- Plan futur: Migration vers une architecture Kubernetes pour une meilleure élasticité

## Résilience et sauvegarde

### Stratégies de résilience
- Tentatives automatiques pour les opérations échouées
- Circuit breakers pour éviter la surcharge des systèmes externes
- Graceful degradation en cas de composants défaillants

### Sauvegarde et récupération
- Sauvegardes quotidiennes de la base de données
- Backup des configurations et volumes Docker
- Plan de reprise d'activité documenté

## Coûts d'infrastructure

Voir le document [détail des coûts](../costs.md) pour une analyse complète des coûts d'infrastructure.
