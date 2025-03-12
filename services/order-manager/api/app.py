#!/usr/bin/env python3
"""
Configuration de l'API REST pour l'agent Order Manager
Fait partie du projet Dropshipping Crew AI
"""

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from services import OrderService
from integrations.shopify import ShopifyClient
from integrations.suppliers import SupplierCommunicator
from storage import OrderRepository
from notifications import NotificationManager
from .routers import orders, supplier_orders, health
from .utils import get_order_service

# Configuration de Loguru
logger.add(
    os.path.join(os.getenv("LOG_DIR", "logs"), "order_manager.log"),
    rotation="10 MB",
    retention="7 days",
    level="INFO"
)

# Création de l'application FastAPI
app = FastAPI(
    title="Order Manager API",
    description="API REST pour l'agent Order Manager du projet Dropshipping Crew AI",
    version="0.1.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dans un environnement de production, limitez aux origines spécifiques
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation des dépendances
@app.on_event("startup")
async def startup_event():
    """
    Initialise les services et les dépendances au démarrage de l'application.
    """
    logger.info("Démarrage de l'agent Order Manager")
    
    # Configuration du repository
    db_path = os.getenv("DB_PATH", "./data/orders.db")
    repository = OrderRepository(db_path)
    await repository.initialize()
    
    # Configuration des clients et services
    shopify_client = ShopifyClient(
        shop_url=os.getenv("SHOPIFY_SHOP_URL"),
        api_key=os.getenv("SHOPIFY_API_KEY"),
        api_password=os.getenv("SHOPIFY_API_PASSWORD")
    )
    
    supplier_communicator = SupplierCommunicator()
    
    notification_manager = NotificationManager(
        shopify_client=shopify_client,
        repository=repository
    )
    
    # Création du service principal
    order_service = OrderService(
        repository=repository,
        shopify_client=shopify_client,
        supplier_communicator=supplier_communicator,
        notification_manager=notification_manager
    )
    
    # Stockage des dépendances dans le state de l'application
    app.state.repository = repository
    app.state.shopify_client = shopify_client
    app.state.supplier_communicator = supplier_communicator
    app.state.notification_manager = notification_manager
    app.state.order_service = order_service
    
    # Démarrage du service
    await order_service.start()
    logger.info("Service Order Manager démarré avec succès")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Arrête proprement les services au shutdown de l'application.
    """
    logger.info("Arrêt de l'agent Order Manager")
    
    # Arrêt du service principal
    if hasattr(app.state, "order_service"):
        await app.state.order_service.stop()
    
    logger.info("Agent Order Manager arrêté avec succès")

# Inclusion des routeurs
app.include_router(health.router, tags=["health"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(supplier_orders.router, prefix="/supplier-orders", tags=["supplier-orders"])

# Point d'entrée principal
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
