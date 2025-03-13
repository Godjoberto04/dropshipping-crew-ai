# Guide de l'agent Order Manager

Ce guide présente l'utilisation et les fonctionnalités de l'agent Order Manager, qui gère les commandes et les fournisseurs dans le système Dropshipping Crew AI.

## Fonctionnalités

L'agent Order Manager offre les fonctionnalités suivantes :

- Gestion complète des commandes client (suivi, mise à jour de statut)
- Intégration avec plusieurs fournisseurs dropshipping (AliExpress, CJ Dropshipping)
- Synchronisation bidirectionnelle avec Shopify
- API REST complète pour toutes les opérations
- Système de notification pour les changements de statut
- Architecture extensible pour ajouter facilement de nouveaux fournisseurs

## Configuration

### Variables d'environnement

Pour utiliser l'agent Order Manager, configurez les variables d'environnement suivantes dans votre fichier `.env` :

```
# Configuration générale
ORDER_MANAGER_PORT=8002
ORDER_MANAGER_HOST=0.0.0.0
ORDER_MANAGER_API_KEY=votre_clé_api_secrète
ORDER_MANAGER_LOG_LEVEL=INFO

# Configuration base de données
DB_CONNECTION_STRING=postgresql://username:password@db:5432/orderdb

# Configuration Shopify
SHOPIFY_SHOP_URL=votre-boutique.myshopify.com
SHOPIFY_API_KEY=votre_api_key_shopify
SHOPIFY_API_SECRET=votre_api_secret_shopify
SHOPIFY_API_VERSION=2024-01

# Configuration AliExpress
ALIEXPRESS_API_KEY=votre_api_key_aliexpress
ALIEXPRESS_SECRET=votre_secret_aliexpress

# Configuration CJ Dropshipping
CJ_DROPSHIPPING_API_KEY=votre_api_key_cj
CJ_DROPSHIPPING_EMAIL=votre_email_cj

# Configuration des notifications
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=votre_username
SMTP_PASSWORD=votre_password
EMAIL_FROM=notifications@votreboutique.com
```

### Docker Compose

L'agent Order Manager est inclus dans le fichier `docker-compose.yml` du projet principal :

```yaml
services:
  order-manager:
    build: ./services/order-manager
    container_name: order-manager
    restart: unless-stopped
    ports:
      - "8002:8000"
    env_file:
      - .env
    volumes:
      - ./services/order-manager:/app
    depends_on:
      - db
      - redis
```

## API REST

L'agent Order Manager expose une API REST complète pour interagir avec toutes ses fonctionnalités.

### Points d'API principaux

#### Gestion des commandes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/orders` | Liste toutes les commandes |
| GET | `/orders/{order_id}` | Obtient les détails d'une commande |
| POST | `/orders` | Crée une nouvelle commande |
| PUT | `/orders/{order_id}` | Met à jour une commande existante |
| DELETE | `/orders/{order_id}` | Supprime une commande |

#### Gestion des commandes fournisseurs

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/supplier-orders` | Liste toutes les commandes fournisseurs |
| GET | `/supplier-orders/{supplier_order_id}` | Obtient les détails d'une commande fournisseur |
| POST | `/supplier-orders` | Crée une nouvelle commande fournisseur |
| PUT | `/supplier-orders/{supplier_order_id}` | Met à jour une commande fournisseur |
| DELETE | `/supplier-orders/{supplier_order_id}` | Annule une commande fournisseur |

#### Recherche de produits

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/search` | Recherche des produits chez un fournisseur |
| GET | `/product/{supplier}/{product_id}` | Obtient les détails d'un produit |

### Exemples d'utilisation

#### Rechercher des produits AliExpress

```bash
curl -X POST "http://votre-serveur:8002/search" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: votre_api_key" \
  -d '{
    "supplier": "aliexpress",
    "query": "smartphone accessories",
    "page": 1,
    "limit": 20
  }'
```

#### Rechercher des produits CJ Dropshipping

```bash
curl -X POST "http://votre-serveur:8002/search" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: votre_api_key" \
  -d '{
    "supplier": "cj_dropshipping",
    "query": "smartphone accessories",
    "page": 1,
    "limit": 20
  }'
```

#### Obtenir les détails d'un produit

```bash
curl -X GET "http://votre-serveur:8002/product/aliexpress/1234567890" \
  -H "X-API-Key: votre_api_key"
```

#### Créer une commande fournisseur

```bash
curl -X POST "http://votre-serveur:8002/supplier-orders" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: votre_api_key" \
  -d '{
    "order_id": "ord_12345",
    "supplier": "cj_dropshipping",
    "items": [
      {
        "sku": "SKU001",
        "quantity": 1,
        "supplier_product_id": "CJ123456",
        "properties": {"color": "blue", "size": "M"}
      }
    ],
    "shipping_address": {
      "first_name": "Jean",
      "last_name": "Dupont",
      "address1": "123 Rue Exemple",
      "city": "Paris",
      "state": "Île-de-France",
      "zip": "75001",
      "country": "FR",
      "phone": "+33123456789",
      "email": "jean.dupont@example.com"
    }
  }'
```

#### Vérifier le statut d'une commande fournisseur

```bash
curl -X GET "http://votre-serveur:8002/supplier-orders/sup_ord_123" \
  -H "X-API-Key: votre_api_key"
```

## Intégration avec Shopify

L'agent Order Manager s'intègre avec Shopify pour :

1. Récupérer automatiquement les nouvelles commandes de votre boutique
2. Mettre à jour le statut des commandes dans Shopify lorsqu'elles sont expédiées
3. Ajouter les numéros de suivi aux commandes pour permettre aux clients de suivre leurs colis

### Configuration de l'intégration Shopify

Pour configurer l'intégration avec Shopify :

1. Créez une application privée dans votre admin Shopify
2. Accordez les permissions suivantes à l'application :
   - `read_orders`, `write_orders` (pour la gestion des commandes)
   - `read_fulfillments`, `write_fulfillments` (pour les expéditions)
   - `read_products` (pour la synchronisation des produits)
3. Notez l'API Key et le Secret générés
4. Configurez les variables d'environnement `SHOPIFY_API_KEY` et `SHOPIFY_API_SECRET`

### Webhooks Shopify

Pour recevoir les notifications en temps réel de Shopify, configurez les webhooks suivants dans votre application Shopify :

| Événement | URL du webhook |
|-----------|---------------|
| `orders/create` | `http://votre-serveur:8002/webhooks/shopify/orders/create` |
| `orders/updated` | `http://votre-serveur:8002/webhooks/shopify/orders/updated` |
| `orders/cancelled` | `http://votre-serveur:8002/webhooks/shopify/orders/cancelled` |
| `fulfillments/create` | `http://votre-serveur:8002/webhooks/shopify/fulfillments/create` |

## Intégration avec les fournisseurs

### AliExpress

L'intégration avec AliExpress permet de :

1. Rechercher des produits dans le catalogue AliExpress
2. Obtenir les détails complets des produits (prix, variantes, options d'expédition)
3. Passer des commandes automatiquement
4. Suivre le statut des commandes et les informations d'expédition

Pour configurer l'accès à l'API AliExpress :

1. Inscrivez-vous au programme AliExpress Dropshipping
2. Obtenez une clé API et un secret via le portail développeur
3. Configurez les variables d'environnement dans `.env`

### CJ Dropshipping

L'intégration avec CJ Dropshipping permet de :

1. Rechercher des produits dans leur catalogue
2. Obtenir les détails complets des produits
3. Passer des commandes automatiquement
4. Suivre le statut des commandes et les informations d'expédition
5. Profiter des entrepôts internationaux pour des livraisons plus rapides

Pour configurer l'accès à l'API CJ Dropshipping :

1. Créez un compte sur CJ Dropshipping
2. Accédez à l'espace développeurs et demandez une clé API
3. Configurez les variables d'environnement `CJ_DROPSHIPPING_API_KEY` et `CJ_DROPSHIPPING_EMAIL`

## Comparaison des fournisseurs

| Caractéristique | AliExpress | CJ Dropshipping |
|----------------|------------|-----------------|
| Sélection de produits | Très large | Modérée |
| Prix | Généralement plus bas | Légèrement plus élevés |
| Délais d'expédition | 15-45 jours | 7-15 jours |
| Contrôle qualité | Minimal | Oui |
| Photos produits | Non | Service de photographie disponible |
| Entrepôts internationaux | Non | Oui |
| Dropshipping dédié | Non | Oui |
| Frais supplémentaires | Non | Certains services payants |

## Notifications aux clients

L'agent Order Manager peut envoyer automatiquement des notifications aux clients lorsque :

1. La commande est reçue et confirmée
2. La commande est expédiée par le fournisseur
3. Le colis est en transit ou a subi un retard
4. Le colis est livré

Pour activer les notifications :

1. Configurez les paramètres SMTP dans le fichier `.env`
2. Créez ou personnalisez les modèles d'emails dans le dossier `notifications/templates/`
3. Activez les notifications dans les paramètres de l'agent

## Architecture technique

L'agent Order Manager est construit selon une architecture modulaire asynchrone :

```
order-manager/
├── api/                  # API REST FastAPI
├── integrations/         # Intégrations externes
│   ├── shopify/          # Intégration avec Shopify
│   └── suppliers/        # Intégrations avec les fournisseurs
│       ├── aliexpress.py
│       └── cj_dropshipping.py
├── models/               # Modèles de données
├── services/             # Logique métier
├── storage/              # Persistance des données
└── notifications/        # Système de notifications
```

### Modèle de données

Les principaux modèles de données sont :

1. `Order` : Représente une commande client
2. `SupplierOrder` : Représente une commande passée auprès d'un fournisseur
3. `ShippingInfo` : Contient les informations d'expédition et de suivi

### Workflow de traitement des commandes

1. La commande est reçue via Shopify
2. L'agent Order Manager crée une entrée dans la base de données
3. Les produits sont répartis par fournisseur
4. Des commandes fournisseurs sont créées pour chaque fournisseur
5. Les commandes sont transmises aux fournisseurs via leurs API
6. L'agent surveille régulièrement le statut des commandes
7. Lorsqu'une commande est expédiée, l'information est mise à jour dans Shopify
8. Les clients sont notifiés des changements de statut

## Extension et personnalisation

### Ajout d'un nouveau fournisseur

Pour ajouter un nouveau fournisseur :

1. Créez une nouvelle classe qui hérite de `SupplierBase` dans le dossier `integrations/suppliers/`
2. Implémentez toutes les méthodes requises par l'interface
3. Ajoutez le fournisseur au registre dans `integrations/suppliers/__init__.py`
4. Ajoutez la configuration nécessaire dans le fichier `.env`

### Personnalisation des modèles de notification

Les modèles de notification se trouvent dans le dossier `notifications/templates/` et utilisent Jinja2 pour le rendu. Vous pouvez personnaliser ces modèles pour correspondre à l'identité de votre marque.

## Dépannage

### Problèmes courants et solutions

| Problème | Cause possible | Solution |
|----------|----------------|----------|
| "API connection error" | Problème de réseau ou API indisponible | Vérifiez votre connexion et le statut de l'API du fournisseur |
| "Authentication failed" | Clés API incorrectes ou périmées | Vérifiez vos clés API dans le fichier `.env` |
| "Product not found" | ID de produit invalide ou produit retiré | Vérifiez l'ID ou recherchez un produit similaire |
| "Order creation failed" | Données de commande incomplètes ou incorrectes | Vérifiez les informations d'adresse et de produit |
| "Webhook verification failed" | Problème de sécurité avec les webhooks Shopify | Vérifiez la configuration des webhooks dans Shopify |

### Journalisation

Les logs de l'agent se trouvent dans le dossier `logs/` du conteneur. Pour augmenter le niveau de verbosité, modifiez la variable d'environnement `ORDER_MANAGER_LOG_LEVEL` (valeurs possibles : DEBUG, INFO, WARNING, ERROR).

## Ressources additionnelles

- [Documentation API AliExpress](https://developers.aliexpress.com/)
- [Documentation API CJ Dropshipping](https://developers.cjdropshipping.com/)
- [Documentation API Shopify](https://shopify.dev/api)
- [Guide détaillé des intégrations fournisseurs](../services/order-manager/integrations/suppliers/README.md)
