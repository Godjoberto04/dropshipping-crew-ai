"""
Application FastAPI principale pour l'agent Order Manager.
"""
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Création de l'application FastAPI
app = FastAPI(
    title="Order Manager API",
    description="API pour la gestion des commandes du système de dropshipping autonome",
    version="0.1.0"
)

# Configuration des CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # A remplacer par les origines spécifiques en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route de santé
@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé de l'API."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "agent": "order-manager"
    }

# Point d'entrée principal
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("api.app:app", host="0.0.0.0", port=port, reload=True)
