#!/usr/bin/env python3
"""
Routeur pour les endpoints de gestion des commandes fournisseurs
Fait partie du projet Dropshipping Crew AI
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from models import SupplierOrder
from services import OrderService
from ..utils import get_order_service

router = APIRouter()

# Modèles Pydantic pour les requêtes et réponses
class SupplierOrderResponse(BaseModel):
    """
    Modèle de réponse pour les commandes fournisseurs.
    """
    id: str
    original_order_id: str
    supplier_type: str
    supplier_order_id: Optional[str]
    status: str
    line_items: List[Dict[str, Any]]
    shipping_address: Dict[str, Any]
    tracking_info: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str
    errors: List[Dict[str, Any]]
    
    class Config:
        schema_extra = {
            "example": {
                "id": "abc123",
                "original_order_id": "123456789",
                "supplier_type": "aliexpress",
                "supplier_order_id": "AE67890",
                "status": "processing",
                "line_items": [
                    {
                        "id": "9876543210",
                        "title": "Produit exemple",
                        "quantity": 1,
                        "price": 29.99,
                        "sku": "SKU123",
                        "product_id": "12345",
                        "variant_id": "67890",
                        "supplier_data": {
                            "product_id": "aliexpress_pid_123",
                            "variant_id": "aliexpress_vid_456",
                            "shipping_method": "standard"
                        }
                    }
                ],
                "shipping_address": {
                    "first_name": "Jean",
                    "last_name": "Dupont",
                    "address1": "123 Rue de Paris",
                    "address2": "Apt 4B",
                    "city": "Paris",
                    "province": "Île-de-France",
                    "country": "France",
                    "zip": "75001",
                    "phone": "+33123456789"
                },
                "tracking_info": {
                    "tracking_number": "ABC123456789",
                    "carrier": "PostNL",
                    "tracking_url": "https://track.example.com/ABC123456789",
                    "estimated_delivery_date": "2023-07-25T00:00:00Z"
                },
                "created_at": "2023-07-12T14:36:00Z",
                "updated_at": "2023-07-12T15:30:00Z",
                "errors": []
            }
        }

# Endpoints

@router.get("/", response_model=List[SupplierOrderResponse])
async def get_supplier_orders(
    status: Optional[str] = Query(None, description="Filtrer par statut"),
    order_id: Optional[str] = Query(None, description="Filtrer par commande principale"),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Récupère la liste des commandes fournisseurs, avec filtrage optionnel.
    """
    if order_id:
        # Récupération des commandes fournisseurs pour une commande spécifique
        supplier_orders = await order_service.repository.get_supplier_orders_for_order(order_id)
    elif status:
        # Récupération des commandes fournisseurs par statut
        supplier_orders = await order_service.repository.get_supplier_orders_by_status(status)
    else:
        # Récupération de toutes les commandes fournisseurs (avec limite)
        supplier_orders = await order_service.repository.get_all_supplier_orders(limit=100)
    
    return supplier_orders

@router.get("/{supplier_order_id}", response_model=SupplierOrderResponse)
async def get_supplier_order(
    supplier_order_id: str,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Récupère une commande fournisseur spécifique par son identifiant.
    """
    supplier_order = await order_service.repository.get_supplier_order(supplier_order_id)
    if not supplier_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commande fournisseur {supplier_order_id} introuvable"
        )
    
    return supplier_order

@router.post("/{supplier_order_id}/retry", response_model=dict)
async def retry_supplier_order(
    supplier_order_id: str,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Retente l'envoi d'une commande fournisseur en échec.
    """
    success = await order_service.retry_failed_supplier_order(supplier_order_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Impossible de retenter la commande fournisseur {supplier_order_id}"
        )
    
    return {"status": "success", "message": f"Commande fournisseur {supplier_order_id} relancée avec succès"}

@router.post("/{supplier_order_id}/refresh-status", response_model=dict)
async def refresh_supplier_order_status(
    supplier_order_id: str,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Force la mise à jour du statut d'une commande fournisseur.
    """
    # Récupération de la commande fournisseur
    supplier_order = await order_service.repository.get_supplier_order(supplier_order_id)
    if not supplier_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commande fournisseur {supplier_order_id} introuvable"
        )
    
    # Mise à jour du statut
    updated = await order_service._update_supplier_order_status(supplier_order)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Impossible de mettre à jour le statut de la commande fournisseur {supplier_order_id}"
        )
    
    # Récupération de la commande fournisseur mise à jour
    supplier_order = await order_service.repository.get_supplier_order(supplier_order_id)
    
    return {
        "status": "success", 
        "message": f"Statut de la commande fournisseur {supplier_order_id} mis à jour",
        "current_status": supplier_order.status
    }
