#!/usr/bin/env python3
"""
Initialisation du module d'intégration avec les fournisseurs dropshipping
Fait partie du projet Dropshipping Crew AI
"""

from .communicator import SupplierCommunicator
from .base import SupplierInterface, OrderResult

__all__ = [
    'SupplierCommunicator',
    'SupplierInterface',
    'OrderResult'
]
