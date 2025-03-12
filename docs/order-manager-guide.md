# Guide de l'agent Order Manager

## Introduction

L'agent Order Manager est le quatrième agent du système Dropshipping Crew AI. Il est responsable de la gestion complète des commandes, depuis leur réception jusqu'à leur livraison. Cet agent s'interface avec Shopify pour recevoir les nouvelles commandes, communique avec les fournisseurs pour transmettre les commandes, et suit les expéditions pour tenir à jour le statut des commandes.

## Fonctionnalités principales

### 1. Traitement des commandes

- **Réception des commandes** : Capture des nouvelles commandes via les webhooks Shopify
- **Traitement automatique ou manuel** : Configuration pour traiter automatiquement les commandes ou les mettre en attente pour revue manuelle selon des critères configurable (ex : montant)
- **Validation des commandes** : Vérification des informations, détection des fraudes potentielles, validation des stocks

### 2. Communication avec les fournisseurs

- **Transmission des commandes** : Envoi automatique des commandes aux fournisseurs appropriés
- **Format spécifique par fournisseur** : Adaptation des données de commande selon le format attendu par chaque fournisseur
- **Suivi des commandes fournisseur** : Interrogation des APIs fournisseurs pour connaître l'état des commandes

### 3. Suivi des expéditions

- **Récupération des informations de suivi** : Collecte des numéros de suivi et transporteurs auprès des fournisseurs
- **Mise à jour des statuts** : Suivi régulier de l'état des expéditions et mise à jour dans Shopify
- **Notifications automatiques** : Envoi d'alertes lors des changements d'état importants (ex : expédition, livraison)

### 4. Gestion des problèmes

- **Détection des anomalies** : Identification des commandes en retard ou problématiques
- **Annulations et remboursements** : Traitement des demandes d'annulation ou de remboursement
- **Communication client** : Génération de notifications pour informer les clients des changements de statut

## Architecture technique

### Composants principaux

1. **OrderProcessor** : Gestionnaire central pour le traitement des commandes
2. **SupplierCommunicator** : Interface avec les différents fournisseurs
3. **ShipmentTracker** : Suivi des expéditions et mise à jour des statuts
4. **NotificationService** : Système de notifications pour les alertes et communications
5. **ConfigManager** : Gestion de la configuration et des paramètres

### API REST

L'agent expose une API REST avec les endpoints suivants :

- `POST /webhooks/orders/create` : Réception des nouvelles commandes via webhook Shopify
- `POST /process-order` : Traitement manuel d'une commande
- `POST /track-shipment` : Déclenchement manuel du suivi d'une expédition
- `GET /orders/{order_id}/status` : Récupération du statut d'une commande
- `GET /suppliers` : Liste des fournisseurs configurés
- `GET /health` : Vérification de l'état de santé du service

## Configuration

### Variables d'environnement

```
# Configuration API
API_BASE_URL=http://api:8000
PORT=8003
HOST=0.0.0.0
STARTUP_DELAY=5

# Configuration Shopify
SHOPIFY_SHOP_URL=your-store.myshopify.com
SHOPIFY_API_KEY=your-api-key
SHOPIFY_API_PASSWORD=your-api-password

# Configuration des fournisseurs
ALIEXPRESS_API_URL=https://api.aliexpress.com
ALIEXPRESS_API_KEY=your-aliexpress-key
CJDROPSHIPPING_API_URL=https://api.cjdropshipping.com
CJDROPSHIPPING_API_KEY=your-cj-key

# Configuration des notifications
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

# Configuration Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

### Configuration des fournisseurs

Les fournisseurs sont configurés dans le fichier `config.py` ou via les variables d'environnement. Chaque fournisseur nécessite au minimum :

- Un nom
- Une URL d'API
- Une clé d'API
- Des endpoints pour les commandes et le suivi

## Intégration avec les autres agents

### Agent Data Analyzer

L'agent Order Manager récupère des informations sur les produits et les fournisseurs auprès de l'agent Data Analyzer pour déterminer le meilleur fournisseur pour chaque produit commandé.

### Agent Website Builder

L'agent Order Manager est notifié des nouvelles commandes via les webhooks configurés par l'agent Website Builder dans Shopify.

### Agent Content Generator

L'agent Order Manager peut solliciter l'agent Content Generator pour créer des communications personnalisées avec les clients en cas de problèmes ou de retards.

## Workflow typique

1. Une nouvelle commande est reçue via le webhook Shopify
2. L'agent vérifie si la commande nécessite une revue manuelle (ex : montant élevé)
3. Si la commande peut être traitée automatiquement, l'agent détermine le fournisseur approprié
4. La commande est transmise au fournisseur dans le format attendu
5. L'agent surveille régulièrement le statut de la commande auprès du fournisseur
6. Lorsque la commande est expédiée, l'agent récupère les informations de suivi
7. L'agent surveille l'état de l'expédition jusqu'à la livraison
8. Le statut de la commande dans Shopify est mis à jour à chaque étape

## Maintenance et surveillance

### Logs

L'agent génère des logs détaillés dans le dossier `/logs` avec différents niveaux de verbosité :

- **ERROR** : Problèmes critiques nécessitant une intervention
- **WARNING** : Situations anormales mais non critiques
- **INFO** : Actions normales et changements d'état
- **DEBUG** : Informations détaillées pour le débogage

### Métriques

L'agent collecte des métriques sur :

- Nombre de commandes traitées
- Taux de succès/échec des transmissions aux fournisseurs
- Temps moyen de traitement des commandes
- Délais d'expédition par fournisseur
- Taux de problèmes par fournisseur

### Résolution des problèmes courants

1. **Échec de connexion à Shopify** : Vérifier les identifiants API et les droits d'accès
2. **Échec de connexion aux fournisseurs** : Vérifier les URLs et clés API des fournisseurs
3. **Commandes bloquées** : Vérifier les logs pour identifier les raisons des blocages
4. **Échecs d'envoi de notifications** : Vérifier la configuration SMTP

## Exemple d'utilisation

### Traitement manuel d'une commande

```bash
curl -X POST "http://votre-serveur:8003/process-order" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 12345,
    "action": "process",
    "manual_review": true
  }'
```

### Suivi manuel d'une expédition

```bash
curl -X POST "http://votre-serveur:8003/track-shipment" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 12345,
    "tracking_number": "TRK123456789",
    "carrier": "dhl"
  }'
```

### Récupération du statut d'une commande

```bash
curl -X GET "http://votre-serveur:8003/orders/12345/status"
```

## Évolutions futures

1. **Intégration avec plus de fournisseurs** : Ajout de nouveaux fournisseurs dropshipping
2. **Algorithme intelligent de sélection de fournisseur** : Choix du meilleur fournisseur basé sur les prix, délais et fiabilité
3. **Gestion avancée des retours** : Traitement automatisé des demandes de retour
4. **Tableau de bord des commandes** : Interface visuelle pour surveiller et gérer les commandes
5. **Intégration avec des services de suivi tiers** : AfterShip, ShipStation, etc.

## Tests

L'agent Order Manager comprend une suite de tests unitaires pour assurer la fiabilité des fonctionnalités principales :

```bash
# Exécuter tous les tests
cd services/order-manager
python -m unittest discover -s tests

# Exécuter un test spécifique
python -m unittest tests.test_order_processor
```

---

Document créé le 12 mars 2025