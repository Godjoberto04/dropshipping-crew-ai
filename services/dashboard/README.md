# Dashboard Centralisé pour Dropshipping-Crew-AI

Ce module fournit un dashboard centralisé pour piloter et surveiller l'ensemble des agents du système Dropshipping-Crew-AI.

## Fonctionnalités

- Vue d'ensemble de l'état du système
- Pages détaillées pour chaque agent
- Visualisation des métriques clés
- Interface de configuration centralisée
- Gestion des boutiques Shopify
- Alertes et notifications en temps réel

## Architecture

Le dashboard est développé avec les technologies suivantes :

- **Frontend** : React.js avec Tailwind CSS
- **Backend** : API REST basée sur FastAPI
- **Authentification** : Système JWT
- **Visualisation** : Recharts
- **Temps réel** : WebSockets

## Structure du module

```
dashboard/
├── frontend/              # Application React
│   ├── public/            # Fichiers statiques
│   └── src/               # Code source React
│       ├── components/    # Composants réutilisables
│       ├── pages/         # Pages du dashboard
│       ├── hooks/         # Hooks personnalisés
│       ├── services/      # Services d'API
│       ├── utils/         # Utilitaires
│       ├── context/       # Contextes React
│       └── assets/        # Images et ressources
├── backend/               # API FastAPI
│   ├── app/               # Application principale
│   │   ├── api/           # Endpoints d'API
│   │   ├── core/          # Configuration et utilitaires
│   │   ├── db/            # Modèles et connexion BDD
│   │   └── services/      # Services métier
│   └── tests/             # Tests unitaires et d'intégration
└── docker/                # Configuration Docker
    ├── frontend/          # Dockerfile pour le frontend
    └── backend/           # Dockerfile pour le backend
```

## Pages principales

1. **Page d'accueil / Vue d'ensemble**
   - Widgets de statut des agents
   - Métriques clés globales
   - Alertes et notifications
   - État des ressources système

2. **Pages détaillées par agent**
   - Data Analyzer : Analyse de marché et tendances
   - Website Builder : Gestion du site Shopify
   - Content Generator : Création et gestion du contenu
   - Order Manager : Suivi des commandes et fournisseurs
   - Site Updater : Optimisation et tests A/B

3. **Page de configuration**
   - Intégrations API (Shopify, Claude, fournisseurs)
   - Configuration par agent
   - Gestion des utilisateurs
   - Sauvegardes et restauration

4. **Page de gestion des boutiques Shopify**
   - Performance des ventes
   - Analyse du catalogue produits
   - Gestion des fournisseurs
   - Finances et rentabilité

## Installation et démarrage

### Prérequis

- Node.js 18+
- Docker et Docker Compose
- Accès aux APIs des différents agents

### Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/Godjoberto04/dropshipping-crew-ai.git
cd dropshipping-crew-ai/services/dashboard
```

2. Configuration :
```bash
cp .env.example .env
# Éditer le fichier .env avec vos paramètres
```

3. Démarrage avec Docker :
```bash
docker-compose up -d
```

4. Accès au dashboard :
```
http://localhost:3000
```

## Développement

### Frontend

```bash
cd frontend
npm install
npm start
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Roadmap de développement

Voir le [plan de développement détaillé](../../docs/roadmap/dashboard-development-plan.md) pour le calendrier complet et les fonctionnalités à venir.

## Intégration avec les agents

Le dashboard communique avec les différents agents via l'API centralisée du système. Chaque agent expose des endpoints spécifiques qui sont consommés par le dashboard pour afficher les informations pertinentes et permettre le contrôle.

## Sécurité

- Authentification JWT
- Gestion des rôles et permissions
- Protection CSRF
- Chiffrement des données sensibles
- Audit logs pour les actions importantes

## Contribution

Lors du développement de nouvelles fonctionnalités pour le dashboard, veuillez suivre les conventions de code établies et ajouter des tests unitaires appropriés.
