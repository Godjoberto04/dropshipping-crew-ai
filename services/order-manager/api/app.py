"""
Point d'entrée principal pour l'API de l'agent Order Manager.
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Créer l'application FastAPI
app = FastAPI(
    title="Order Manager API",
    description="API pour la gestion des commandes de dropshipping",
    version="0.1.0"
)

# Ajouter CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # A définir plus précisément en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importer les routeurs après initialisation de l'app
from api.routers import health

# Ajouter les routeurs à l'application
app.include_router(health.router, tags=["health"])

# Point d'entrée pour démarrer l'application directement
if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8080"))
    uvicorn.run("api.app:app", host=host, port=port, reload=True)
