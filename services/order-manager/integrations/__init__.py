#!/usr/bin/env python3
"""
Initialisation du module d'intégrations
Fait partie du projet Dropshipping Crew AI
"""

from .shopify import ShopifyClient
from .suppliers import SupplierCommunicator

__all__ = [
    'ShopifyClient',
    'SupplierCommunicator'
]
