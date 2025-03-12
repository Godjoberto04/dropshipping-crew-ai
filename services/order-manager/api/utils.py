#!/usr/bin/env python3
"""
Utilitaires pour l'API de l'agent Order Manager
Fait partie du projet Dropshipping Crew AI
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
import os

from services import OrderService

# Configuration de l'authentification par API key
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    """
    Dépendance pour vérifier l'API key.
    
    Args:
        api_key: Clé API fournie dans l'en-tête
        
    Returns:
        Clé API si valide
        
    Raises:
        HTTPException: Si la clé API est invalide ou manquante
    """
    if API_KEY is None:
        # Si pas de clé API configurée, on n'applique pas d'authentification
        return api_key
    
    if api_key is None or api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_key

async def get_order_service(api_key: str = Depends(get_api_key)) -> OrderService:
    """
    Dépendance pour obtenir le service OrderService.
    
    Args:
        api_key: Clé API valide (dépendance)
        
    Returns:
        Instance du service OrderService
        
    Raises:
        HTTPException: Si le service n'est pas disponible
    """
    from fastapi import Request
    request = Request.scope["app"]
    
    if not hasattr(request.state, "order_service"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service Order Manager non disponible",
        )
    
    return request.state.order_service
