from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import os
import json
from datetime import datetime

app = FastAPI(title="Dropshipping Crew AI API")

# Configurer CORS pour permettre les requêtes depuis le dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines exactes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles de données
class ProductAnalysis(BaseModel):
    name: str
    supplier_price: float
    recommended_price: float
    potential_margin_percent: float
    competition_level: str
    trend_direction: str
    recommendation_score: float
    justification: str

class AnalysisResults(BaseModel):
    top_products: List[ProductAnalysis]
    analysis_date: datetime
    source_urls: List[str]

class UrlsList(BaseModel):
    urls: List[str]

@app.get("/")
def read_root():
    """Endpoint racine de l'API"""
    return {
        "message": "Bienvenue sur l'API du projet Dropshipping Autonome avec Crew AI",
        "version": "1.0.0",
        "status": "online"
    }

@app.get("/status")
def get_status():
    """Renvoie le statut des différents services du système"""
    # Dans une implémentation réelle, vous interrogeriez les services
    # Ici, nous renvoyons des données simulées
    return {
        "services": {
            "postgres": {"status": "online", "version": "14"},
            "redis": {"status": "online", "version": "7"},
            "api": {"status": "online", "version": "1.0.0"},
            "data_analyzer": {"status": "partial", "version": "0.1.0"},
            "website_builder": {"status": "offline", "version": None},
            "content_generator": {"status": "offline", "version": None},
            "order_manager": {"status": "offline", "version": None},
            "site_updater": {"status": "offline", "version": None}
        },
        "system": {
            "server": "Scaleway DEV1-M",
            "cpu_usage": 15.2,  # pourcentage simulé
            "memory_usage": 32.1,  # pourcentage simulé
            "disk_usage": 23.8   # pourcentage simulé
        }
    }

@app.get("/agents/data-analyzer/status")
def get_data_analyzer_status():
    """Renvoie le statut de l'agent Data Analyzer"""
    return {
        "status": "partial",
        "version": "0.1.0",
        "last_run": datetime.now().isoformat(),
        "capabilities": [
            "Website scraping",
            "Product analysis"
        ],
        "pending_capabilities": [
            "Trend analysis",
            "Competition assessment"
        ]
    }

@app.post("/agents/data-analyzer/analyze")
async def trigger_analysis(urls_list: UrlsList):
    """Déclenche une analyse de marché sur les URLs spécifiées"""
    if not urls_list.urls or len(urls_list.urls) == 0:
        raise HTTPException(status_code=400, detail="Au moins une URL est requise")
        
    # Dans une implémentation réelle, vous déclencheriez l'agent ici
    # Pour l'instant, nous simulons une réponse
    return {
        "task_id": f"task_{int(datetime.now().timestamp())}",
        "status": "queued",
        "message": f"Analyse démarrée sur {len(urls_list.urls)} URLs",
        "estimated_completion": (datetime.now().timestamp() + 300)  # +5 minutes
    }

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Récupère le statut d'une tâche en cours"""
    # Simulation de statut de tâche
    return {
        "task_id": task_id,
        "status": "in_progress",
        "progress": 65,  # pourcentage
        "message": "Analyse des produits en cours",
        "started_at": (datetime.now().timestamp() - 150),  # -2.5 minutes
        "estimated_completion": (datetime.now().timestamp() + 150)  # +2.5 minutes
    }

@app.get("/analysis/results/latest")
async def get_latest_analysis():
    """Récupère les résultats de la dernière analyse"""
    # Simuler des résultats d'analyse
    return {
        "analysis_id": f"analysis_{int(datetime.now().timestamp())}",
        "created_at": datetime.now().isoformat(),
        "source_urls": ["https://example-shop.com/category/accessories"],
        "top_products": [
            {
                "name": "Housse de protection smartphone premium",
                "supplier_price": 3.50,
                "recommended_price": 15.99,
                "potential_margin_percent": 78.1,
                "competition_level": "Medium",
                "trend_direction": "Up",
                "recommendation_score": 8.7,
                "justification": "Forte marge, tendance à la hausse et concurrence modérée"
            },
            {
                "name": "Chargeur sans fil 15W",
                "supplier_price": 7.20,
                "recommended_price": 24.99,
                "potential_margin_percent": 71.2,
                "competition_level": "Medium",
                "trend_direction": "Up",
                "recommendation_score": 8.4,
                "justification": "Produit tendance avec bonne marge et facilité d'expédition"
            },
            {
                "name": "Support téléphone voiture magnétique",
                "supplier_price": 2.80,
                "recommended_price": 12.99,
                "potential_margin_percent": 78.4,
                "competition_level": "High",
                "trend_direction": "Stable",
                "recommendation_score": 7.8,
                "justification": "Très bonne marge mais concurrence élevée"
            }
        ]
    }

@app.get("/analysis/results/{analysis_id}")
async def get_analysis_results(analysis_id: str):
    """Récupère les résultats d'une analyse spécifique"""
    # Dans une implémentation réelle, vous récupéreriez les résultats de la base de données
    # Pour l'instant, nous renvoyons les mêmes résultats que /analysis/results/latest
    return await get_latest_analysis()

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
