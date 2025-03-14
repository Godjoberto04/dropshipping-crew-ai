#!/usr/bin/env python3
"""
Modèles pour l'agent Order Manager
Fait partie du projet Dropshipping Crew AI
"""

from .order import Order, OrderStatus, OrderLineItem
from .supplier_order import SupplierOrder, SupplierOrderStatus
from .shipping import ShippingInfo, TrackingInfo

# Types de fournisseurs supportés par l'agent Order Manager
class SupplierType:
    """
    Types de fournisseurs supportés par l'agent Order Manager.
    """
    ALIEXPRESS = "aliexpress"
    CJ_DROPSHIPPING = "cjdropshipping"
    # Ajouter d'autres fournisseurs au besoin
    
    @classmethod
    def get_all(cls):
        """Retourne la liste de tous les types de fournisseurs supportés."""
        return [getattr(cls, attr) for attr in dir(cls) if not attr.startswith("_") and attr.isupper()]
