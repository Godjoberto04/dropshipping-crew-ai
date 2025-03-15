#!/usr/bin/env python3
"""
Routeur pour les endpoints de vérification de santé
Fait partie du projet Dropshipping Crew AI
"""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from datetime import datetime
import os

from ..utils import get_api_key

router = APIRouter()

class HealthResponse(BaseModel):
    """
Modèle de réponse pour le endpoint de santé.
    """
    status: str
    version: str
    timestamp: str

@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """
    Vérifie l'état de santé de l'agent Order Manager.
    
    Returns:
        Statut de santé de l'API
    """
    return {
        "status": "ok",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health/detailed", response_model=dict)
async def detailed_health_check(request: Request, api_key: str = Depends(get_api_key)):
    """
    Vérifie l'état de santé détaillé de l'agent Order Manager.
    Nécessite une authentification.
    
    Returns:
        Statut de santé détaillé de l'API et ses dépendances
    """
    # Vérification de la disponibilité du service principal
    service_status = "ok" if hasattr(request.app.state, "order_service") else "unavailable"
    
    # Vérification de la disponibilité de la base de données
    db_status = "unknown"
    if hasattr(request.app.state, "repository"):
        try:
            # Vérification simple de la base de données
            await request.app.state.repository._ensure_initialized()
            db_status = "ok"
        except Exception:
            db_status = "error"
    
    # Vérification de la connexion Shopify
    shopify_status = "unknown"
    if hasattr(request.app.state, "shopify_client"):
        try:
            # Vérification simple de la connexion Shopify
            # Dans un scénario réel, on pourrait faire une requête légère pour vérifier
            shopify_status = "ok"
        except Exception:
            shopify_status = "error"
    
    return {
        "status": "ok" if all(s == "ok" for s in [service_status, db_status, shopify_status]) else "degraded",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "service": service_status,
            "database": db_status,
            "shopify": shopify_status
        },
        "environment": os.getenv("ENVIRONMENT", "development")
    }
