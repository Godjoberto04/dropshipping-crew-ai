#!/usr/bin/env python3
"""
Modèle de données pour les commandes fournisseurs
Fait partie du projet Dropshipping Crew AI
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

class SupplierType(str, Enum):
    """
    Énumération des types de fournisseurs supportés.
    """
    ALIEXPRESS = "aliexpress"          # AliExpress
    CJ_DROPSHIPPING = "cj_dropshipping" # CJ Dropshipping

@dataclass
class SupplierOrder:
    """
    Représentation d'une commande fournisseur.
    """
    id: str                                  # Identifiant unique interne
    original_order_id: str                   # Identifiant de la commande client originale
    supplier_type: str                       # Type de fournisseur
    supplier_order_id: Optional[str]         # Identifiant attribué par le fournisseur
    status: str                              # Statut de la commande (pending, processing, shipped, delivered, error, cancelled)
    line_items: List[Dict[str, Any]]         # Éléments de la commande
    shipping_address: Dict[str, Any]         # Adresse de livraison
    tracking_info: Optional[Dict[str, Any]]  # Informations de suivi (tracking number, carrier, etc.)
    created_at: str                          # Date de création (ISO format)
    updated_at: str                          # Date de dernière mise à jour (ISO format)
    errors: List[Dict[str, Any]] = field(default_factory=list)  # Liste des erreurs rencontrées (horodatées)
