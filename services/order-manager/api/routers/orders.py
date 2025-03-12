#!/usr/bin/env python3
"""
Routeur pour les endpoints de gestion des commandes clientes
Fait partie du projet Dropshipping Crew AI
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from models import Order, OrderStatus
from services import OrderService
from ..utils import get_order_service

router = APIRouter()

# Modèles Pydantic pour les requêtes et réponses
class OrderResponse(BaseModel):
    """
    Modèle de réponse pour les commandes.
    """
    id: str
    shopify_id: str
    status: str
    customer: Dict[str, Any]
    shipping_address: Dict[str, Any]
    line_items: List[Dict[str, Any]]
    total_price: float
    currency: str
    created_at: str
    updated_at: str
    error_message: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123456789",
                "shopify_id": "123456789",
                "status": "processing",
                "customer": {
                    "id": "987654321",
                    "email": "client@example.com",
                    "first_name": "Jean",
                    "last_name": "Dupont",
                    "phone": "+33123456789"
                },
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
                "line_items": [
                    {
                        "id": "9876543210",
                        "title": "Produit exemple",
                        "quantity": 1,
                        "price": 29.99,
                        "sku": "SKU123",
                        "product_id": "12345",
                        "variant_id": "67890"
                    }
                ],
                "total_price": 29.99,
                "currency": "EUR",
                "created_at": "2023-07-12T14:30:00Z",
                "updated_at": "2023-07-12T14:35:00Z",
                "error_message": null
            }
        }

class CancelOrderRequest(BaseModel):
    """
    Modèle de requête pour l'annulation de commande.
    """
    reason: str = Field(..., description="Raison de l'annulation")
    
    class Config:
        schema_extra = {
            "example": {
                "reason": "Demande client : changement d'avis"
            }
        }

class OrderDetailResponse(BaseModel):
    """
    Modèle de réponse détaillée incluant les commandes fournisseurs.
    """
    order: OrderResponse
    supplier_orders: List[Dict[str, Any]]
    
    class Config:
        schema_extra = {
            "example": {
                "order": {
                    "id": "123456789",
                    "shopify_id": "123456789",
                    "status": "processing",
                    "customer": {
                        "id": "987654321",
                        "email": "client@example.com",
                        "first_name": "Jean",
                        "last_name": "Dupont",
                        "phone": "+33123456789"
                    },
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
                    "line_items": [
                        {
                            "id": "9876543210",
                            "title": "Produit exemple",
                            "quantity": 1,
                            "price": 29.99,
                            "sku": "SKU123",
                            "product_id": "12345",
                            "variant_id": "67890"
                        }
                    ],
                    "total_price": 29.99,
                    "currency": "EUR",
                    "created_at": "2023-07-12T14:30:00Z",
                    "updated_at": "2023-07-12T14:35:00Z",
                    "error_message": null
                },
                "supplier_orders": [
                    {
                        "id": "abc123",
                        "supplier_type": "aliexpress",
                        "status": "processing",
                        "created_at": "2023-07-12T14:36:00Z"
                    }
                ]
            }
        }

# Endpoints

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    status: Optional[str] = Query(None, description="Filtrer par statut"),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Récupère la liste des commandes, avec filtrage optionnel par statut.
    """
    if status:
        try:
            # Vérification que le statut est valide
            order_status = OrderStatus(status)
            orders = await order_service.get_orders_by_status(order_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Statut invalide: {status}"
            )
    else:
        # Récupération de toutes les commandes
        orders = await order_service.get_all_orders()
    
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Récupère une commande spécifique par son identifiant.
    """
    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commande {order_id} introuvable"
        )
    
    return order

@router.get("/{order_id}/detail", response_model=OrderDetailResponse)
async def get_order_detail(
    order_id: str,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Récupère les détails d'une commande avec ses commandes fournisseurs associées.
    """
    order, supplier_orders = await order_service.get_order_with_suppliers(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commande {order_id} introuvable"
        )
    
    return {
        "order": order,
        "supplier_orders": supplier_orders
    }

@router.post("/{order_id}/retry", response_model=dict)
async def retry_order(
    order_id: str,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Retente le traitement d'une commande en échec.
    """
    success = await order_service.retry_failed_order(order_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Impossible de retenter la commande {order_id}"
        )
    
    return {"status": "success", "message": f"Commande {order_id} relancée avec succès"}

@router.post("/{order_id}/cancel", response_model=dict)
async def cancel_order(
    order_id: str,
    cancel_request: CancelOrderRequest,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Annule une commande et ses commandes fournisseurs associées.
    """
    success = await order_service.cancel_order(order_id, cancel_request.reason)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Impossible d'annuler la commande {order_id}"
        )
    
    return {"status": "success", "message": f"Commande {order_id} annulée avec succès"}