# Agent Order Manager

L'agent Order Manager est responsable de la gestion des commandes dans le système Dropshipping Crew AI. Il agit comme intermédiaire entre la boutique en ligne (Shopify) et les fournisseurs dropshipping (AliExpress, CJ Dropshipping, etc.).

## Fonctionnalités

- Récupération automatique des nouvelles commandes depuis Shopify
- Répartition des produits par fournisseur et création des commandes fournisseurs
- Suivi des statuts des commandes fournisseurs
- Mise à jour du statut des commandes principales
- Notification des clients lors des changements de statut importants
- API REST pour l'interaction avec les autres agents

## Architecture

L'agent Order Manager est développé en Python et utilise les technologies suivantes :

- **FastAPI** : Framework API RESTful
- **SQLite** : Base de données pour le stockage des commandes
- **Loguru** : Système de journalisation

L'architecture de l'agent est organisée en plusieurs modules :

- **models** : Modèles de données (Order, SupplierOrder, etc.)
- **services** : Services métier (OrderService, etc.)
- **storage** : Accès aux données (OrderRepository)
- **integrations** : Intégration avec les systèmes externes (Shopify, fournisseurs)
- **notifications** : Gestion des notifications client
- **api** : API REST

## Installation

### Prérequis

- Python 3.9+
- Docker (optionnel)

### Installation avec pip

```bash
# Cloner le dépôt
git clone https://github.com/Godjoberto04/dropshipping-crew-ai.git
cd dropshipping-crew-ai/services/order-manager

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### Installation avec Docker

```bash
# Cloner le dépôt
git clone https://github.com/Godjoberto04/dropshipping-crew-ai.git
cd dropshipping-crew-ai/services/order-manager

# Construire l'image Docker
docker build -t order-manager .
```

## Configuration

Créez un fichier `.env` à la racine du projet avec les variables d'environnement suivantes :

```bash
# Configuration Shopify
SHOPIFY_SHOP_URL=your-shop.myshopify.com
SHOPIFY_API_KEY=your-api-key
SHOPIFY_API_PASSWORD=your-api-password

# Configuration des fournisseurs
ALIEXPRESS_API_KEY=your-aliexpress-key
CJ_DROPSHIPPING_API_KEY=your-cj-key

# Configuration de l'API
API_KEY=your-api-key

# Divers
ENVIRONMENT=development
DB_PATH=./data/orders.db
LOG_DIR=./logs
```

## Utilisation

### Démarrage du serveur

```bash
# Avec Python
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

# Avec Docker
docker run -p 8000:8000 --env-file .env order-manager
```

### Accès à l'API

L'API REST est accessible à l'adresse `http://localhost:8000`. La documentation Swagger est disponible à l'adresse `http://localhost:8000/docs`.

Exemples d'utilisation :

```bash
# Vérification de l'état de santé
curl http://localhost:8000/health

# Récupération des commandes
curl -H "X-API-Key: your-api-key" http://localhost:8000/orders

# Récupération d'une commande par son identifiant
curl -H "X-API-Key: your-api-key" http://localhost:8000/orders/123456789
```

## Développement

### Structure des fichiers

```
order-manager/
├── api/                  # API REST
│   ├── routers/          # Routeurs FastAPI
│   ├── app.py            # Application FastAPI
│   └── utils.py          # Utilitaires pour l'API
├── integrations/         # Intégrations avec les systèmes externes
│   ├── shopify/          # Intégration Shopify
│   └── suppliers/        # Intégration avec les fournisseurs
├── models/               # Modèles de données
├── notifications/        # Gestion des notifications
├── services/             # Services métier
├── storage/              # Accès aux données
├── Dockerfile            # Configuration Docker
└── requirements.txt      # Dépendances Python
```

### Tests

```bash
pytest tests/
```

## Intégration avec les autres agents

L'agent Order Manager est conçu pour interagir avec les autres agents du système Dropshipping Crew AI :

- **Data Analyzer** : Fournit des informations sur les produits et les fournisseurs
- **Website Builder** : Fournit des informations sur la boutique et les produits
- **Content Generator** : Peut être utilisé pour générer des messages de notification personnalisés
- **Marketing Manager** (à venir) : Utilisera les données des commandes pour optimiser les campagnes marketing

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.