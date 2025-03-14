# Agent Order Manager

Module de gestion des commandes pour le système Dropshipping Crew AI.

## Description

L'agent Order Manager est responsable de la gestion complète des commandes dans le système Dropshipping Crew AI. Il assure le suivi des commandes client, communique avec les fournisseurs dropshipping (AliExpress, CJ Dropshipping), et gère les informations de suivi des expéditions.

## Fonctionnalités principales

### 1. Gestion des commandes client
- Récupération et traitement des commandes depuis Shopify
- Suivi du statut des commandes
- Envoi de notifications aux clients

### 2. Intégration des fournisseurs
- Communication avec les fournisseurs dropshipping (AliExpress, CJ Dropshipping)
- Sélection automatique du meilleur fournisseur
- Comparaison des prix, délais d'expédition et disponibilité

### 3. Gestion des expéditions
- Suivi des colis
- Mise à jour du statut de livraison
- Gestion des problèmes de livraison

## Architecture

L'agent Order Manager est construit sur une architecture modulaire qui permet de facilement ajouter de nouveaux fournisseurs ou fonctionnalités:

```
OrderManager/
├── api/                  # Interface API REST
├── integrations/         # Intégrations externes
│   ├── shopify/          # Intégration avec Shopify
│   └── suppliers/        # Intégration avec les fournisseurs
│       ├── aliexpress.py # Fournisseur AliExpress
│       ├── cjdropshipping.py # Fournisseur CJ Dropshipping
│       ├── communicator.py # Façade pour les fournisseurs
│       └── supplier_selector.py # Sélection automatique
├── models/               # Modèles de données
├── notifications/        # Système de notifications
├── services/             # Services métier
├── storage/              # Gestion des données
└── tests/                # Tests unitaires
```

## Nouvelle fonctionnalité: Sélection automatique des fournisseurs

Cette fonctionnalité permet de sélectionner automatiquement le meilleur fournisseur pour chaque produit en fonction de différents critères comme le prix, le délai d'expédition, la disponibilité, etc.

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

### API de sélection

L'API suivante est disponible pour la sélection des fournisseurs:

#### Rechercher des produits chez tous les fournisseurs

```
POST /suppliers/search
{
  "query": "smartphone accessories",
  "limit": 20,
  "supplier": "aliexpress"  // Optionnel, pour chercher chez un fournisseur spécifique
}
```

#### Sélectionner le meilleur fournisseur pour un produit

```
POST /suppliers/select
{
  "product_id": "123456789",
  "variant_id": "VAR123",  // Optionnel
  "strategy": "auto"  // "auto", "cheapest", "fastest" ou "default"
}
```

#### Comparer les fournisseurs pour plusieurs produits

```
POST /suppliers/compare
{
  "products": [
    {"product_id": "123456789", "variant_id": "VAR123"},
    {"product_id": "987654321", "variant_id": "VAR456"}
  ]
}
```

#### Obtenir la liste des fournisseurs disponibles

```
GET /suppliers/suppliers
```

## Installation

1. Assurez-vous que les variables d'environnement suivantes sont configurées:
   - `ALIEXPRESS_API_KEY`: Clé API pour AliExpress
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
python -m unittest tests.test_supplier_selector
python -m unittest tests.test_supplier_communicator
```

## Exemples d'utilisation

### Traitement d'une commande avec sélection automatique des fournisseurs

```python
from services import OrderServiceSuppliers
from storage import OrderRepository

# Initialisation du service
repository = OrderRepository("./data/orders.db")
await repository.initialize()
service = OrderServiceSuppliers(repository=repository)

# Données de la commande
order_data = {
    "id": "123456789",
    "shipping_address": {
        "name": "John Doe",
        "phone": "5551234567",
        "address1": "123 Main St",
        "city": "New York",
        "province": "NY",
        "zip": "10001",
        "country_code": "US"
    },
    "line_items": [
        {
            "product_id": "PROD1",
            "variant_id": "VAR1",
            "quantity": 2
        }
    ]
}

# Traitement de la commande avec sélection automatique des fournisseurs
result = await service.process_supplier_order(order_data, strategy="auto")

# Affichage du résultat
if result["success"]:
    print(f"Commande traitée avec succès. {len(result['orders'])} fournisseurs sélectionnés.")
    for order in result["orders"]:
        print(f"Fournisseur: {order['supplier']}, ID commande: {order['supplier_order_id']}")
else:
    print(f"Erreur: {result['error']}")
```

## Ajout d'un nouveau fournisseur

Pour ajouter un nouveau fournisseur, suivez les étapes suivantes:

1. Créez une nouvelle classe dans `integrations/suppliers/` qui hérite de `SupplierInterface`
2. Implémentez toutes les méthodes requises par l'interface
3. Ajoutez le nouveau fournisseur à la classe `SupplierType` dans `models/__init__.py`
4. Mettez à jour le communicateur pour prendre en charge le nouveau fournisseur
5. Ajoutez des tests unitaires pour le nouveau fournisseur

Consultez les fichiers `aliexpress.py` et `cjdropshipping.py` pour des exemples d'implémentation.
