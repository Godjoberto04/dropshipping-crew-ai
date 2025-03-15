# Agent Order Manager

Cet agent est responsable de la gestion complète des commandes pour le système de dropshipping autonome. Il offre une intégration native avec plusieurs fournisseurs dropshipping (AliExpress, CJ Dropshipping) et se synchronise avec Shopify pour un traitement automatisé des commandes.

## Fonctionnalités principales

### 1. Gestion des commandes client
- Récupération et traitement des commandes depuis Shopify
- Gestion complète des commandes e-commerce
- Suivi du statut des commandes
- Envoi de notifications aux clients

### 2. Intégration des fournisseurs
- Intégration avec les fournisseurs dropshipping (AliExpress, CJ Dropshipping)
- Communication avec les fournisseurs
- Sélection automatique du meilleur fournisseur
- Comparaison des prix, délais d'expédition et disponibilité

### 3. Gestion des expéditions
- Suivi des commandes et expéditions
- Mise à jour du statut de livraison
- Gestion des problèmes de livraison

### 4. API complète
- API REST complète pour la gestion des commandes
- Synchronisation avec Shopify
- Gestion des notifications client

## Architecture

L'agent Order Manager utilise une architecture modulaire avec les composants suivants :

```
OrderManager/
├── api/                  # Interface API REST
│   ├── app.py            # Point d'entrée FastAPI
│   └── routers/          # Endpoints de l'API
├── integrations/         # Intégrations externes
│   ├── shopify/          # Intégration avec Shopify
│   └── suppliers/        # Intégration avec les fournisseurs
│       ├── aliexpress.py # Fournisseur AliExpress
│       ├── cjdropshipping.py # Fournisseur CJ Dropshipping
│       ├── communicator.py # Façade pour les fournisseurs
│       └── base.py       # Interface commune des fournisseurs
├── models/               # Modèles de données
│   ├── order.py          # Modèle de commande
│   ├── supplier_order.py # Modèle de commande fournisseur
│   └── shipping.py       # Modèle d'expédition
├── notifications/        # Système de notifications
├── services/             # Services métier
│   ├── order_service.py  # Service principal
│   └── order_service_suppliers.py # Gestion des fournisseurs
├── storage/              # Gestion des données
│   └── order_repository.py # Accès aux données
└── tests/                # Tests unitaires
```

## Sélection automatique des fournisseurs

Cette fonctionnalité permet de sélectionner automatiquement le meilleur fournisseur pour chaque produit en fonction de différents critères.

### Critères de sélection

Le système utilise les critères suivants pour évaluer les fournisseurs:

- **Prix du produit** (pondération: 35%)
- **Coût d'expédition** (pondération: 20%)
- **Délai de livraison** (pondération: 15%)
- **Disponibilité en stock** (pondération: 10%)
- **Notation du vendeur** (pondération: 10%)
- **Fiabilité du fournisseur** (pondération: 10%)

### Stratégies de sélection

Plusieurs stratégies de sélection sont disponibles:

- **auto**: Sélection basée sur tous les critères pondérés
- **cheapest**: Sélection basée uniquement sur le prix total (produit + expédition)
- **fastest**: Sélection basée uniquement sur le délai de livraison
- **default**: Utilisation du fournisseur par défaut (configurable)

## Intégrations supportées

### Fournisseurs dropshipping

- **AliExpress** : Recherche de produits, création de commandes, suivi d'expédition
- **CJ Dropshipping** : Recherche de produits, création de commandes, suivi d'expédition

## Installation et configuration

Voir le fichier docker-compose.yml à la racine du projet et le .env.example pour les variables d'environnement nécessaires.

1. Assurez-vous que les variables d'environnement suivantes sont configurées:
   - `ALIEXPRESS_API_KEY`: Clé API pour AliExpress
   - `ALIEXPRESS_API_SECRET`: Secret API pour AliExpress
   - `CJ_DROPSHIPPING_API_KEY`: Clé API pour CJ Dropshipping
   - `SHOPIFY_SHOP_URL`: URL de votre boutique Shopify
   - `SHOPIFY_API_KEY`: Clé API Shopify
   - `SHOPIFY_API_PASSWORD`: Mot de passe API Shopify
   - `DEFAULT_SUPPLIER`: Fournisseur par défaut (optionnel, valeur par défaut: "aliexpress")

2. Installer les dépendances:
   ```bash
   pip install -r requirements.txt
   ```

3. Démarrer l'application:
   ```bash
   cd services/order-manager
   python -m api.app
   ```

## Tests

Pour exécuter les tests unitaires:

```bash
cd services/order-manager
python -m unittest discover -s tests
```

Pour tester spécifiquement l'intégration des fournisseurs:

```bash
python -m unittest tests.test_aliexpress_supplier
python -m unittest tests.test_cjdropshipping_supplier
```

## Ajout d'un nouveau fournisseur

Pour ajouter un nouveau fournisseur, suivez les étapes suivantes:

1. Créez une nouvelle classe dans `integrations/suppliers/` qui hérite de l'interface de base
2. Implémentez toutes les méthodes requises par l'interface
3. Ajoutez le nouveau fournisseur aux types de fournisseurs supportés
4. Mettez à jour le communicateur pour prendre en charge le nouveau fournisseur
5. Ajoutez des tests unitaires pour le nouveau fournisseur

Consultez les fichiers `aliexpress.py` et `cjdropshipping.py` pour des exemples d'implémentation.

## Documentation détaillée

Pour plus d'informations sur l'utilisation de l'agent, consultez [Guide de l'agent Order Manager](../../docs/order-manager-guide.md).
