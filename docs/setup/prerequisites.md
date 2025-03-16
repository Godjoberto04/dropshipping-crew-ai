# Prérequis pour l'installation

Ce document détaille les prérequis nécessaires pour installer et exécuter le système autonome de dropshipping. Assurez-vous que toutes ces conditions sont remplies avant de procéder à l'installation.

## Matériel recommandé

Pour exécuter le système dans son ensemble, nous recommandons les configurations minimales suivantes:

### Environnement de production
- **CPU**: Au moins 2 vCPUs (4 vCPUs recommandés)
- **RAM**: Minimum 4 GB (8 GB recommandés)
- **Stockage**: Minimum 40 GB SSD
- **Bande passante**: 100 Mbps avec transfert mensuel de données illimité

### Environnement de développement
- **CPU**: 2 vCPUs
- **RAM**: Minimum 4 GB
- **Stockage**: Minimum 20 GB

## Système d'exploitation

Le système a été principalement développé et testé sur:
- Ubuntu Server 22.04 LTS (recommandé)
- Debian 11 ou plus récent

Autres systèmes compatibles:
- CentOS 8 ou plus récent
- macOS (pour développement uniquement)
- Windows avec WSL2 (pour développement uniquement)

## Dépendances logicielles

### Requis
- **Docker**: version 24.0.5 ou plus récente
- **docker-compose**: version 2.20.2 ou plus récente
- **Git**: version 2.30.0 ou plus récente
- **Python**: version 3.11 ou plus récente (pour les scripts utilitaires)
- **pip**: version 23.0 ou plus récente
- **Nginx**: version 1.20 ou plus récente (si non utilisé via Docker)

### Configuration réseau
- Ports requis ouverts: 80, 443, 8000, 5432 (si accès distant à PostgreSQL)
- Accès Internet sortant pour les API externes
- Idéalement, une adresse IP statique et un nom de domaine

## Comptes externes requis

### API obligatoires
- **Compte Claude AI API**: Accès à l'API Claude pour les fonctionnalités d'IA
- **Compte Shopify Partner**: Pour créer et gérer des boutiques Shopify
- **Compte développeur Shopify**: Pour accéder à l'API Shopify

### API recommandées (optionnelles)
- **AliExpress Dropshipping Center**: Pour l'intégration avec AliExpress
- **CJ Dropshipping**: Pour l'intégration avec CJ Dropshipping
- **Google Cloud Platform**: Pour des fonctionnalités avancées d'analyse et stockage (optionnel)

## Clés API et configuration

Préparez les informations suivantes pour la configuration:

### Clés API requises
- **API Key Claude**: Obtenue depuis votre compte Claude
- **API Key Shopify**: Obtenue depuis votre compte développeur Shopify
- **Shopify Store URL**: URL de votre boutique Shopify
- **Clés API pour fournisseurs dropshipping**: AliExpress, CJ Dropshipping, etc.

### Configuration de base de données
- Nom d'utilisateur et mot de passe PostgreSQL
- Nom de la base de données

## Compétences techniques recommandées

Pour installer et gérer le système, il est recommandé d'avoir des connaissances de base dans:

- Commandes Linux et shell scripting
- Configuration et utilisation de Docker et docker-compose
- Utilisation de Git pour la gestion de version
- Compréhension des API REST et formats JSON
- Notions de sécurité réseau et configuration de pare-feu
- Compréhension des concepts de base du e-commerce et dropshipping

## Ressources système

Le système utilise les ressources de la manière suivante:

| Composant | Utilisation CPU | Utilisation RAM | Stockage |
|-----------|----------------|-----------------|-----------|
| API centrale | 5-10% | 200-300 MB | 500 MB |
| Data Analyzer | 10-50% | 500-800 MB | 1-2 GB |
| Website Builder | 5-15% | 200-400 MB | 500 MB |
| Content Generator | 20-40% | 400-700 MB | 500 MB |
| Order Manager | 5-15% | 200-400 MB | 1 GB |
| PostgreSQL | 10-30% | 500-1000 MB | 10-20 GB |
| Redis | 5-10% | 100-200 MB | 1-2 GB |
| Nginx | 1-5% | 50-100 MB | 100-200 MB |

## Prochaines étapes

Une fois que vous avez vérifié que toutes ces conditions sont remplies, vous pouvez procéder à l'[installation](installation.md) du système.

## Ressources supplémentaires

- [Guide officiel d'installation de Docker](https://docs.docker.com/engine/install/)
- [Guide d'installation de docker-compose](https://docs.docker.com/compose/install/)
- [Documentation de l'API Shopify](https://shopify.dev/docs/api)
- [Documentation de l'API Claude](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
