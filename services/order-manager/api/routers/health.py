"""
Routeur pour les endpoints de santé du système.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/health")

@router.get("")
async def health_check():
    """
    Vérifie la santé du service Order Manager.
    
    Returns:
        dict: État de santé du service
    """
    return {
        "status": "ok",
        "version": "0.1.0",
        "agent": "order-manager"
    }
