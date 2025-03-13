# Intégrations avec les fournisseurs dropshipping

Ce module gère les intégrations avec différents fournisseurs dropshipping comme AliExpress et CJ Dropshipping.

## Fournisseurs supportés

Actuellement, les fournisseurs suivants sont pris en charge :

1. **AliExpress** (`aliexpress`) - Permet de rechercher des produits, obtenir des détails de produits et passer des commandes auprès d'AliExpress.
2. **CJ Dropshipping** (`cj_dropshipping`) - Permet de rechercher des produits, obtenir des détails de produits et passer des commandes auprès de CJ Dropshipping.

## Structure du module

Le module est organisé comme suit :

- `base.py` - Contient la classe de base `SupplierBase` dont tous les fournisseurs héritent
- `aliexpress.py` - Implémentation pour AliExpress
- `cj_dropshipping.py` - Implémentation pour CJ Dropshipping
- `communicator.py` - Utilitaires communs pour la communication avec les fournisseurs

## Utilisation

### Configuration

Pour chaque fournisseur, vous devez configurer les variables d'environnement correspondantes :

#### AliExpress
```
ALIEXPRESS_API_KEY=your_api_key
ALIEXPRESS_SECRET=your_secret
```

#### CJ Dropshipping
```
CJ_DROPSHIPPING_API_KEY=your_api_key
CJ_DROPSHIPPING_EMAIL=your_email
```

### Exemple d'utilisation

```python
from integrations.suppliers import get_supplier

# Obtenir une instance du fournisseur AliExpress
aliexpress = get_supplier("aliexpress")

# Rechercher des produits
results = await aliexpress.search_products("smartphone accessories")

# Obtenir les détails d'un produit
product = await aliexpress.get_product_details("1234567890")

# Créer une commande
from integrations.suppliers.base import OrderDetails, ShippingAddress, OrderItem

shipping_address = ShippingAddress(
    first_name="John",
    last_name="Doe",
    address1="123 Main St",
    city="New York",
    state="NY",
    zip="10001",
    country="US",
    phone="+1234567890",
    email="john.doe@example.com"
)

items = [
    OrderItem(
        sku="SKU001",
        supplier_product_id="1234567890",
        quantity=1,
        price=19.99,
        title="Smartphone Case"
    )
]

order_details = OrderDetails(
    order_id="ord_123456",
    shipping_address=shipping_address,
    items=items
)

result = await aliexpress.create_order(order_details)
```

## Ajout d'un nouveau fournisseur

Pour ajouter un nouveau fournisseur :

1. Créez une nouvelle classe qui hérite de `SupplierBase`
2. Implémentez toutes les méthodes abstraites
3. Ajoutez la classe au registre dans `__init__.py`

Exemple :

```python
from .base import SupplierBase

class MyNewSupplier(SupplierBase):
    """Implémentation pour Mon Nouveau Fournisseur"""
    
    async def search_products(self, query, page=1, page_size=20):
        # Implémentation ici
        pass
    
    async def get_product_details(self, product_id):
        # Implémentation ici
        pass
    
    async def create_order(self, order_details):
        # Implémentation ici
        pass
    
    async def get_order_status(self, supplier_order_id):
        # Implémentation ici
        pass
    
    async def cancel_order(self, supplier_order_id, reason=None):
        # Implémentation ici
        pass
```

Et dans `__init__.py` :

```python
from .base import SupplierBase
from .aliexpress import AliExpressSupplier
from .cj_dropshipping import CJDropshippingSupplier
from .my_new_supplier import MyNewSupplier

# Registre des classes de fournisseurs disponibles
SUPPLIER_REGISTRY = {
    "aliexpress": AliExpressSupplier,
    "cj_dropshipping": CJDropshippingSupplier,
    "my_new_supplier": MyNewSupplier
}
```

## Comparaison des fournisseurs

### AliExpress

**Avantages**:
- Vaste sélection de produits
- Prix compétitifs
- API bien documentée

**Inconvénients**:
- Délais de livraison plus longs
- Support client variable
- Qualité variable des produits

### CJ Dropshipping

**Avantages**:
- Entrepôts dans plusieurs pays (délais plus courts)
- Contrôle qualité avant expédition
- Service de photographie de produits
- Support dédié aux dropshippers

**Inconvénients**:
- Sélection de produits plus limitée qu'AliExpress
- Prix légèrement plus élevés
- Frais d'adhésion pour certains services

## Tests

Les tests unitaires pour chaque intégration de fournisseur se trouvent dans le répertoire `tests/` :

- `test_aliexpress_supplier.py` - Tests pour l'intégration AliExpress
- `test_cj_dropshipping_supplier.py` - Tests pour l'intégration CJ Dropshipping

Pour exécuter les tests :

```bash
python -m unittest tests.test_aliexpress_supplier
python -m unittest tests.test_cj_dropshipping_supplier
```

## Documentation des APIs

### AliExpress

L'intégration AliExpress utilise l'API AliExpress Dropshipping. La documentation officielle est disponible à l'adresse :
https://developers.aliexpress.com/en/doc.htm

### CJ Dropshipping

L'intégration CJ Dropshipping utilise l'API CJ Dropshipping. La documentation officielle est disponible à l'adresse :
https://developers.cjdropshipping.com/api-doc/

## Dépannage

### Problèmes courants

#### "Invalid API key" ou "Authentication failed"
- Vérifiez que les variables d'environnement pour les clés API sont correctement définies
- Assurez-vous que votre compte fournisseur est actif

#### "Product not found"
- Vérifiez que l'ID du produit est correct
- Le produit peut ne plus être disponible chez le fournisseur

#### "Order creation failed"
- Vérifiez que tous les champs obligatoires sont remplis dans l'objet OrderDetails
- Assurez-vous que les produits sont disponibles en stock
- Vérifiez que l'adresse d'expédition est valide

### Journalisation

Les erreurs et événements importants sont enregistrés via le module de journalisation standard. Pour augmenter le niveau de verbosité :

```python
import logging
logging.getLogger('integrations.suppliers').setLevel(logging.DEBUG)
```
