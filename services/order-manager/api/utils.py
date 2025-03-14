#!/usr/bin/env python3
"""
Utilitaires pour l'API REST de l'agent Order Manager
Fait partie du projet Dropshipping Crew AI
"""

from fastapi import Depends, HTTPException
from starlette import status

from services import OrderService, OrderServiceSuppliers
from integrations.suppliers.communicator import SupplierCommunicator


def get_order_service():
    """
    Dépendance pour obtenir le service de gestion des commandes.
    
    Returns:
        OrderService: Instance du service de gestion des commandes
    """
    # Cette fonction sera normalement appelée par FastAPI pour l'injection de dépendance
    # Dans un environnement de test, app.state ne sera pas disponible, donc nous faisons une vérification
    try:
        from api.app import app
        order_service = app.state.order_service
        if not order_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service de gestion des commandes non disponible"
            )
        return order_service
    except (ImportError, AttributeError):
        # Si nous sommes dans un environnement de test, retourner une erreur
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de gestion des commandes non disponible (environnement de test)"
        )


def get_order_service_suppliers():
    """
    Dépendance pour obtenir le service de gestion des fournisseurs.
    
    Returns:
        OrderServiceSuppliers: Instance du service de gestion des fournisseurs
    """
    try:
        from api.app import app
        
        # Si le service existe déjà, le retourner
        if hasattr(app.state, "order_service_suppliers"):
            return app.state.order_service_suppliers
        
        # Sinon, le créer à partir du repository et communicator existants
        if hasattr(app.state, "repository") and hasattr(app.state, "supplier_communicator"):
            repository = app.state.repository
            communicator = app.state.supplier_communicator
        else:
            # Si les dépendances ne sont pas disponibles, créer un communicator
            # (le repository sera nécessaire pour les opérations de base de données)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Dépendances requises non disponibles"
            )
        
        # Créer le service
        service = OrderServiceSuppliers(repository=repository, communicator=communicator)
        
        # Stocker le service pour une utilisation future
        app.state.order_service_suppliers = service
        
        return service
    except (ImportError, AttributeError):
        # Si nous sommes dans un environnement de test, retourner une erreur
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de gestion des fournisseurs non disponible (environnement de test)"
        )


def get_supplier_communicator():
    """
    Dépendance pour obtenir le communicateur avec les fournisseurs.
    
    Returns:
        SupplierCommunicator: Instance du communicateur avec les fournisseurs
    """
    try:
        from api.app import app
        
        # Si le communicator existe déjà, le retourner
        if hasattr(app.state, "supplier_communicator"):
            return app.state.supplier_communicator
        
        # Sinon, le créer
        communicator = SupplierCommunicator()
        
        # Stocker le communicator pour une utilisation future
        app.state.supplier_communicator = communicator
        
        return communicator
    except (ImportError, AttributeError):
        # Si nous sommes dans un environnement de test, retourner un nouveau communicator
        return SupplierCommunicator()
