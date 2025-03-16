# Guide d'utilisation de l'agent Order Manager

## Vue d'ensemble

L'agent Order Manager est un composant clé du système Dropshipping Crew AI, chargé de gérer l'ensemble du cycle de vie des commandes, de leur réception depuis Shopify jusqu'à leur transmission aux fournisseurs et le suivi des livraisons. Cet agent automatise les flux de travail souvent complexes et chronophages liés à la gestion des commandes en dropshipping.

## Fonctionnalités principales

### 1. Gestion des commandes entrantes
- Réception automatique des commandes depuis Shopify via API et webhooks
- Validation et normalisation des données de commande
- Classification des commandes par priorité, région et fournisseur
- Traitement automatique ou manuel selon des critères configurables (ex: montant)
- Vérification des informations, détection des fraudes potentielles, validation des stocks

### 2. Intégration avec les fournisseurs
- Transmission automatique des commandes aux fournisseurs (AliExpress et CJ Dropshipping actuellement supportés)
- Gestion des variantes et options de produits
- Suivi des prix et disponibilité en temps réel
- Format spécifique par fournisseur pour adapter les données de commande

### 3. Suivi des commandes et expéditions
- Surveillance des statuts de commande auprès des fournisseurs
- Mise à jour automatique du statut dans Shopify
- Génération et envoi des notifications aux clients
- Récupération des informations de suivi et des transporteurs

### 4. Gestion des exceptions
- Détection et signalement des problèmes potentiels (rupture de stock, retards, etc.)
- Procédures de résolution automatisées pour les cas simples
- Escalade vers intervention humaine pour les cas complexes
- Traitement des demandes d'annulation ou de remboursement

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
│       ├── aliexpress.py   # Implémentation spécifique AliExpress
│       └── cjdropshipping.py # Implémentation CJ Dropshipping
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

### Composants principaux

1. **OrderProcessor** : Gestionnaire central pour le traitement des commandes
2. **SupplierCommunicator** : Interface avec les différents fournisseurs
3. **ShipmentTracker** : Suivi des expéditions et mise à jour des statuts
4. **NotificationService** : Système de notifications pour les alertes et communications
5. **ConfigManager** : Gestion de la configuration et des paramètres

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
POST /api/webhooks/cjdropshipping     # Callback pour les mises à jour CJ Dropshipping
```

## Exemples d'utilisation

### Récupérer les commandes en attente

```bash
curl -X GET "http://your-server/api/orders?status=pending" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}"
```

### Rechercher des produits chez un fournisseur

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

### Transmettre une commande à AliExpress

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

### Traitement manuel d'une commande

```bash
curl -X POST "http://your-server/api/orders/12345/process" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "action": "process",
    "manual_review": true
  }'
```

### Suivi manuel d'une expédition

```bash
curl -X POST "http://your-server/api/shipments/track" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "order_id": 12345,
    "tracking_number": "TRK123456789",
    "carrier": "dhl"
  }'
```

## Configuration

L'agent Order Manager nécessite les configurations suivantes dans le fichier `.env` :

```
# Configuration API
API_BASE_URL=http://api:8000
PORT=8003
HOST=0.0.0.0
STARTUP_DELAY=5

# Shopify
SHOPIFY_SHOP_NAME=votre-boutique.myshopify.com
SHOPIFY_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXX
SHOPIFY_API_SECRET=XXXXXXXXXXXXXXXXXXXXXXXX
SHOPIFY_API_VERSION=2025-01

# AliExpress
ALIEXPRESS_API_KEY=XXXXXXXXXXXXXXXX
ALIEXPRESS_API_SECRET=XXXXXXXXXXXXXXXX
ALIEXPRESS_AFFILIATE_ID=XXXXXXXXX

# CJ Dropshipping
CJDROPSHIPPING_API_URL=https://api.cjdropshipping.com
CJDROPSHIPPING_API_KEY=XXXXXXXXXXXXXXXX

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
REDIS_DB=0

# Sécurité API
API_SECRET_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Notification
NOTIFICATION_EMAIL=your-email@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password

# Paramètres de traitement
AUTO_PROCESS_ORDERS=true
ORDER_PROCESSING_INTERVAL=15
TRACKING_UPDATE_INTERVAL=120
MANUAL_REVIEW_THRESHOLD=100.0
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

## Intégration avec les fournisseurs

### AliExpress

L'intégration avec AliExpress utilise une combinaison de l'API officielle et de scraping lorsque nécessaire. Pour configurer l'accès :

1. Créez un compte développeur sur [AliExpress Affiliate Program](https://portals.aliexpress.com)
2. Demandez un accès à l'API Dropshipping
3. Obtenez vos clés API et insérez-les dans le fichier `.env`

### CJ Dropshipping

L'intégration avec CJ Dropshipping utilise leur API officielle. Pour configurer l'accès :

1. Créez un compte sur [CJ Dropshipping](https://cjdropshipping.com)
2. Accédez au Developer Portal pour obtenir votre clé API
3. Configurez la clé dans votre fichier `.env`

## Workflow typique

1. Une nouvelle commande est reçue via le webhook Shopify
2. L'agent vérifie si la commande nécessite une revue manuelle (ex : montant élevé)
3. Si la commande peut être traitée automatiquement, l'agent détermine le fournisseur approprié
4. La commande est transmise au fournisseur dans le format attendu
5. L'agent surveille régulièrement le statut de la commande auprès du fournisseur
6. Lorsque la commande est expédiée, l'agent récupère les informations de suivi
7. L'agent surveille l'état de l'expédition jusqu'à la livraison
8. Le statut de la commande dans Shopify est mis à jour à chaque étape

## Surveillance et monitoring

L'agent Order Manager expose des métriques pour le monitoring via l'endpoint `/api/health` :

- Statut général du service
- Temps de réponse moyen
- Nombre de commandes en cours de traitement
- Taux d'erreur
- Utilisation des ressources

Ces métriques peuvent être collectées par des outils comme Prometheus et visualisées dans Grafana.

L'agent collecte également des métriques sur :
- Nombre de commandes traitées
- Taux de succès/échec des transmissions aux fournisseurs
- Temps moyen de traitement des commandes
- Délais d'expédition par fournisseur
- Taux de problèmes par fournisseur

## Gestion des erreurs

En cas d'erreur lors du traitement des commandes, l'agent Order Manager adopte une approche de résilience :

1. Tentatives multiples avec backoff exponentiel pour les erreurs temporaires
2. Mise en file d'attente des commandes non transmises pour retenter ultérieurement
3. Alertes pour les erreurs critiques nécessitant une intervention
4. Journal détaillé des problèmes rencontrés pour analyse et débogage

## Limites actuelles et évolutions prévues

### Limites connues
- Support actuellement limité à AliExpress et CJ Dropshipping comme fournisseurs
- Gestion partielle des retours et remboursements
- Capacité de traitement limitée à environ 1000 commandes/jour

### Évolutions planifiées
- Support d'autres fournisseurs dropshipping majeurs
- Gestion complète des retours et remboursements
- Optimisation pour gérer >10 000 commandes/jour
- Système avancé de gestion des anomalies et exceptions
- Interface utilisateur dédiée pour la supervision manuelle
- Algorithme intelligent de sélection de fournisseur basé sur les prix, délais et fiabilité
- Tableau de bord des commandes avec interface visuelle
- Intégration avec des services de suivi tiers (AfterShip, ShipStation, etc.)

## Résolution des problèmes courants

### L'agent ne reçoit pas les commandes Shopify
- Vérifiez la configuration des webhooks dans Shopify
- Assurez-vous que votre serveur est accessible depuis l'internet
- Vérifiez les logs d'erreur pour des problèmes d'authentification

### Échec de transmission des commandes aux fournisseurs
- Vérifiez les informations d'API des fournisseurs
- Assurez-vous que les produits sont toujours disponibles
- Vérifiez que les adresses client sont complètes et au format correct

### Problèmes de performance
- Augmentez les ressources allouées au conteneur
- Vérifiez les connexions à la base de données et au cache Redis
- Assurez-vous que la rotation des logs est correctement configurée

### Échecs d'envoi de notifications
- Vérifiez la configuration SMTP
- Vérifiez les permissions d'envoi d'emails

## Intégration avec les autres agents

### Agent Data Analyzer
L'agent Order Manager récupère des informations sur les produits et les fournisseurs auprès de l'agent Data Analyzer pour déterminer le meilleur fournisseur pour chaque produit commandé.

### Agent Website Builder
L'agent Order Manager est notifié des nouvelles commandes via les webhooks configurés par l'agent Website Builder dans Shopify.

### Agent Content Generator
L'agent Order Manager peut solliciter l'agent Content Generator pour créer des communications personnalisées avec les clients en cas de problèmes ou de retards.

## Pour aller plus loin

Pour des informations plus détaillées sur le développement et l'extension de l'agent Order Manager, consultez les ressources suivantes :

- [Tests unitaires et d'intégration](../testing/overview.md)
- [Points d'amélioration identifiés](../roadmap/improvement-points.md)
- [Prochaines étapes de développement](../roadmap/next-steps.md)
