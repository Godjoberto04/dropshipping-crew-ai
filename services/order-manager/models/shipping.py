#!/usr/bin/env python3
"""
Modèle de données pour les informations d'expédition
Fait partie du projet Dropshipping Crew AI
"""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ShippingInfo:
    """
    Représentation des informations d'expédition pour une commande.
    
    Cette classe est utilisée pour compiler les informations d'expédition
    de plusieurs commandes fournisseurs associées à une même commande client.
    """
    tracking_numbers: List[str] = field(default_factory=list)  # Numéros de suivi
    carriers: List[str] = field(default_factory=list)         # Transporteurs
    estimated_delivery: Optional[str] = None                   # Date de livraison estimée (ISO format)
    tracking_urls: List[str] = field(default_factory=list)    # URLs de suivi
