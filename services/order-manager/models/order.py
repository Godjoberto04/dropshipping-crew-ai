#!/usr/bin/env python3
"""
Modèle de données pour les commandes
Fait partie du projet Dropshipping Crew AI
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

class OrderStatus(str, Enum):
    """
    Énumération des statuts possibles pour une commande.
    """
    NEW = "new"                # Nouvelle commande
    PROCESSING = "processing"  # En cours de traitement
    SHIPPED = "shipped"        # Expédiée
    DELIVERED = "delivered"    # Livrée
    CANCELLED = "cancelled"    # Annulée
    ERROR = "error"            # Erreur

@dataclass
class Order:
    """
    Représentation d'une commande client.
    """
    id: str                                  # Identifiant unique de la commande
    shopify_id: str                         # Identifiant Shopify
    status: OrderStatus                     # Statut de la commande
    customer: Dict[str, Any]                # Informations client
    shipping_address: Dict[str, Any]        # Adresse de livraison
    line_items: List[Dict[str, Any]]        # Éléments de la commande
    total_price: float                      # Prix total
    currency: str                           # Devise
    created_at: str                         # Date de création (ISO format)
    updated_at: str                         # Date de dernière mise à jour (ISO format)
    error_message: Optional[str] = None     # Message d'erreur éventuel
