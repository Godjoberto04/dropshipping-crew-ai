#!/usr/bin/env python3
"""
Initialisation du module d'intégration avec les fournisseurs dropshipping
Fait partie du projet Dropshipping Crew AI

Ce module fournit des classes pour interagir avec différents fournisseurs
de dropshipping comme AliExpress et CJ Dropshipping.
"""

from typing import Dict, Type
from .communicator import SupplierCommunicator
from .base import SupplierInterface, OrderResult
from .aliexpress import AliExpressSupplier
from .cjdropshipping import CJDropshippingSupplier

__all__ = [
    'SupplierCommunicator',
    'SupplierInterface',
    'OrderResult',
    'AliExpressSupplier',
    'CJDropshippingSupplier',
    'get_supplier',
    'SUPPLIERS'
]

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
