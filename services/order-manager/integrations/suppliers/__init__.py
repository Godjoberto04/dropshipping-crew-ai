"""
Module contenant les intégrations avec les fournisseurs dropshipping.

Ce module fournit des classes pour interagir avec différents fournisseurs
de dropshipping comme AliExpress et CJ Dropshipping.
"""

from typing import Dict, Type
from .aliexpress import AliExpressSupplier
from .cj_dropshipping import CJDropshippingSupplier

# Registre des fournisseurs disponibles
SUPPLIERS: Dict[str, Type] = {
    "aliexpress": AliExpressSupplier,
    "cjdropshipping": CJDropshippingSupplier
}

def get_supplier(supplier_name: str, **kwargs):
    """
    Récupère une instance du fournisseur demandé.
    
    Args:
        supplier_name: Nom du fournisseur ("aliexpress", "cjdropshipping")
        **kwargs: Paramètres à passer au constructeur du fournisseur
        
    Returns:
        Instance du fournisseur
        
    Raises:
        ValueError: Si le fournisseur demandé n'existe pas
    """
    if supplier_name not in SUPPLIERS:
        raise ValueError(f"Fournisseur '{supplier_name}' non supporté. "
                         f"Options disponibles: {', '.join(SUPPLIERS.keys())}")
    
    return SUPPLIERS[supplier_name](**kwargs)
