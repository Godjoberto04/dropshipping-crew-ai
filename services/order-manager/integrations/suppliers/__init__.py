"""
Module d'intégration avec les fournisseurs dropshipping.
"""

from typing import Dict, Type
from .base import SupplierBase
from .aliexpress import AliExpressSupplier
from .cj_dropshipping import CJDropshippingSupplier

# Registre des classes de fournisseurs disponibles
SUPPLIER_REGISTRY: Dict[str, Type[SupplierBase]] = {
    "aliexpress": AliExpressSupplier,
    "cj_dropshipping": CJDropshippingSupplier
}

def get_supplier(supplier_name: str) -> SupplierBase:
    """
    Récupère l'instance d'un fournisseur par son nom.
    
    Args:
        supplier_name (str): Nom du fournisseur
        
    Returns:
        SupplierBase: Instance de la classe du fournisseur
        
    Raises:
        ValueError: Si le fournisseur n'est pas supporté
    """
    if supplier_name.lower() not in SUPPLIER_REGISTRY:
        valid_suppliers = ", ".join(SUPPLIER_REGISTRY.keys())
        raise ValueError(f"Fournisseur '{supplier_name}' non supporté. Fournisseurs valides: {valid_suppliers}")
    
    supplier_class = SUPPLIER_REGISTRY[supplier_name.lower()]
    return supplier_class()
