# Guide de l'agent Order Manager

## Introduction

L'agent Order Manager est un composant clé du système Dropshipping Crew AI, chargé de gérer l'ensemble du cycle de vie des commandes, de leur réception depuis Shopify jusqu'à leur transmission aux fournisseurs et le suivi des livraisons. Cet agent automatise les flux de travail souvent complexes et chronophages liés à la gestion des commandes en dropshipping.

## Fonctionnalités principales

### 1. Gestion des commandes entrantes
- Réception automatique des commandes depuis Shopify via API et webhooks
- Validation et normalisation des données de commande
- Classification des commandes par priorité, région et fournisseur

### 2. Intégration avec les fournisseurs
- Transmission automatique des commandes aux fournisseurs (AliExpress actuellement supporté)
- Gestion des variantes et options de produits
- Suivi des prix et disponibilité en temps réel

### 3. Suivi des commandes et expéditions
- Surveillance des statuts de commande auprès des fournisseurs
- Mise à jour automatique du statut dans Shopify
- Génération et envoi des notifications aux clients

### 4. Gestion des exceptions
- Détection et signalement des problèmes potentiels (rupture de stock, retards, etc.)
- Procédures de résolution automatisées pour les cas simples
- Escalade vers intervention humaine pour les cas complexes

### 5. Recherche de produits
- Recherche de produits chez les fournisseurs via API
- Évaluation préliminaire des produits (prix, délai, ratings)
- Enrichissement des données pour l'agent Data Analyzer

## Architecture technique

L'agent Order Manager est construit avec une architecture moderne, modulaire et extensible :

```
order-manager/
├── api/                    # Interface REST API
│   ├── app.py              # Point d'entrée principal FastAPI
│   ├── routers/            # Organisation des endpoints par domaine
│   │   ├── health.py       # Endpoints de monitoring
│   │   ├── orders.py       # Gestion des commandes
│   │   └── supplier_orders.py # Interface avec les fournisseurs
├── integrations/           # Connecteurs avec systèmes externes
│   ├── shopify/            # Intégration avec Shopify
│   │   ├── client.py       # Client API Shopify
│   └── suppliers/          # Intégrations avec fournisseurs
│       ├── base.py         # Classe abstraite pour fournisseurs
│       ├── communicator.py # Interface commune
│       └── aliexpress.py   # Implémentation spécifique AliExpress
├── models/                 # Modèles de données
│   ├── order.py            # Représentation des commandes
│   ├── supplier_order.py   # Commandes côté fournisseurs
│   └── shipping.py         # Données d'expédition et suivi
├── services/               # Logique métier
│   ├── order_service.py    # Service principal de gestion
│   ├── order_service_suppliers.py # Interaction fournisseurs
│   └── order_service_delivery.py # Gestion livraisons
├── storage/                # Persistance des données
│   └── order_repository.py # Accès à la base de données
└── notifications/          # Système de notifications
    └── notification_manager.py # Gestion des alertes
```

## Utilisation de l'API

L'agent Order Manager expose une API REST complète pour permettre l'interaction avec d'autres systèmes et agents.

### Endpoints principaux

#### Gestion des commandes

```
GET /api/orders                 # Liste des commandes avec filtrage
GET /api/orders/{order_id}      # Détails d'une commande spécifique
POST /api/orders                # Création manuelle d'une commande
PUT /api/orders/{order_id}      # Mise à jour d'une commande
DELETE /api/orders/{order_id}   # Annulation d'une commande
```

#### Interaction avec les fournisseurs

```
GET /api/suppliers                      # Liste des fournisseurs disponibles
GET /api/suppliers/{supplier_id}/orders # Commandes chez un fournisseur
POST /api/suppliers/search              # Recherche de produits chez les fournisseurs
```

#### Gestion des expéditions

```
GET /api/shipments                    # Liste des expéditions
GET /api/shipments/{shipment_id}      # Détails d'une expédition
GET /api/shipments/{shipment_id}/track # Suivi d'une expédition
```

#### Webhooks et callbacks

```
POST /api/webhooks/shopify            # Webhook pour les événements Shopify
POST /api/webhooks/aliexpress         # Callback pour les mises à jour AliExpress
```

### Exemples d'utilisation

#### Récupérer les commandes en attente

```bash
curl -X GET "http://your-server/api/orders?status=pending" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}"
```

#### Rechercher des produits chez un fournisseur

```bash
curl -X POST "http://your-server/api/suppliers/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "supplier": "aliexpress",
    "query": "smartphone accessories",
    "limit": 20,
    "min_rating": 4.5
  }'
```

#### Transmettre une commande à AliExpress

```bash
curl -X POST "http://your-server/api/suppliers/aliexpress/orders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "order_id": "shop_12345",
    "products": [
      {
        "supplier_product_id": "AE12345678",
        "quantity": 1,
        "variant_id": "red-large",
        "unit_price": 15.99
      }
    ],
    "shipping_address": {
      "name": "Jean Dupont",
      "address1": "123 Rue des Exemples",
      "city": "Paris",
      "zip": "75001",
      "country": "France",
      "phone": "+33600000000"
    },
    "shipping_method": "standard"
  }'
```

## Configuration

L'agent Order Manager nécessite les configurations suivantes dans le fichier `.env` :

```
# Shopify
SHOPIFY_SHOP_NAME=votre-boutique.myshopify.com
SHOPIFY_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXX
SHOPIFY_API_SECRET=XXXXXXXXXXXXXXXXXXXXXXXX
SHOPIFY_API_VERSION=2025-01

# AliExpress
ALIEXPRESS_API_KEY=XXXXXXXXXXXXXXXX
ALIEXPRESS_API_SECRET=XXXXXXXXXXXXXXXX
ALIEXPRESS_AFFILIATE_ID=XXXXXXXXX

# Base de données
POSTGRES_USER=postgres
POSTGRES_PASSWORD=XXXXXXXXX
POSTGRES_DB=order_manager
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis (cache et queue)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=XXXXXXXXX

# Sécurité API
API_SECRET_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## Intégration avec Shopify

### Configuration des webhooks

Pour recevoir automatiquement les commandes de Shopify, vous devez configurer les webhooks suivants dans votre panneau d'administration Shopify :

1. Allez dans Paramètres > Notifications > Webhooks
2. Ajoutez un webhook pour "Création de commande" pointant vers `https://votre-serveur.com/api/webhooks/shopify`
3. Répétez pour "Mise à jour de commande" et "Annulation de commande"
4. Assurez-vous que le format est réglé sur "JSON"

### Permissions requises

L'application Shopify associée à votre agent Order Manager nécessite les permissions suivantes :

- `read_orders` - Pour accéder aux commandes
- `write_orders` - Pour mettre à jour les statuts
- `read_products` - Pour accéder aux informations produits
- `read_customers` - Pour accéder aux informations clients
- `read_shipping` - Pour les informations d'expédition

## Intégration avec AliExpress

L'intégration avec AliExpress utilise une combinaison de l'API officielle et de scraping lorsque nécessaire. Pour configurer l'accès :

1. Créez un compte développeur sur [AliExpress Affiliate Program](https://portals.aliexpress.com)
2. Demandez un accès à l'API Dropshipping
3. Obtenez vos clés API et insérez-les dans le fichier `.env`

## Surveillance et monitoring

L'agent Order Manager expose des métriques pour le monitoring via l'endpoint `/api/health` :

- Statut général du service
- Temps de réponse moyen
- Nombre de commandes en cours de traitement
- Taux d'erreur
- Utilisation des ressources

Ces métriques peuvent être collectées par des outils comme Prometheus et visualisées dans Grafana.

## Gestion des erreurs

En cas d'erreur lors du traitement des commandes, l'agent Order Manager adopte une approche de résilience :

1. Tentatives multiples avec backoff exponentiel pour les erreurs temporaires
2. Mise en file d'attente des commandes non transmises pour retenter ultérieurement
3. Alertes pour les erreurs critiques nécessitant une intervention
4. Journal détaillé des problèmes rencontrés pour analyse et débogage

## Limites actuelles et évolutions prévues

### Limites connues
- Support actuellement limité à AliExpress comme fournisseur
- Gestion partielle des retours et remboursements
- Capacité de traitement limitée à environ 1000 commandes/jour

### Évolutions planifiées
- Support de CJ Dropshipping et autres fournisseurs majeurs
- Gestion complète des retours et remboursements
- Optimisation pour gérer >10 000 commandes/jour
- Système avancé de gestion des anomalies et exceptions
- Interface utilisateur dédiée pour la supervision manuelle

## Résolution des problèmes courants

### L'agent ne reçoit pas les commandes Shopify
- Vérifiez la configuration des webhooks dans Shopify
- Assurez-vous que votre serveur est accessible depuis l'internet
- Vérifiez les logs d'erreur pour des problèmes d'authentification

### Échec de transmission des commandes à AliExpress
- Vérifiez les informations d'API AliExpress
- Assurez-vous que les produits sont toujours disponibles
- Vérifiez que les adresses client sont complètes et au format correct

### Problèmes de performance
- Augmentez les ressources allouées au conteneur
- Vérifiez les connexions à la base de données et au cache Redis
- Assurez-vous que la rotation des logs est correctement configurée

## Support et contribution

Pour toute question ou problème concernant l'agent Order Manager :
- Consultez la documentation détaillée dans le répertoire `/docs`
- Vérifiez les issues existantes sur GitHub
- Ouvrez une nouvelle issue si nécessaire

Pour contribuer au développement :
- Suivez les standards de code et de documentation du projet
- Créez une branche dédiée pour vos modifications
- Soumettez une Pull Request avec une description claire
