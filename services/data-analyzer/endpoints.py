"""
Endpoints FastAPI pour l'agent Data Analyzer.
Ce module expose des endpoints pour traiter les requêtes d'analyse
du marché, des tendances et de la complémentarité de produits.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
import json
import os
import logging
import time
import asyncio
import uuid
from datetime import datetime

# Importation des modules d'analyse
from models.complementary.complementary_analyzer import ComplementaryAnalyzer
from models.complementary.association_rules import AssociationRulesMiner
from data_sources.trends.trends_analyzer import TrendsAnalyzer

# Configuration du logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Modèles de données Pydantic
class UrlsList(BaseModel):
    urls: List[str]
    market_segment: Optional[str] = None
    min_margin: Optional[float] = 30.0

class ActionRequest(BaseModel):
    action: str
    products: Optional[List[str]] = None
    product_id: Optional[str] = None
    query: Optional[str] = None
    timeframe: Optional[str] = "medium_term"
    geo: Optional[str] = None
    max_products: Optional[int] = 5
    product_ids: Optional[List[str]] = None
    max_bundles: Optional[int] = 3

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: Optional[int] = None
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

# Création de l'application FastAPI
app = FastAPI(
    title="Data Analyzer API",
    description="API pour l'agent Data Analyzer du projet Dropshipping Autonome avec Crew AI",
    version="0.1.0"
)

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stockage des tâches en cours (en mémoire pour la simplicité)
# Dans une implémentation production, utiliser Redis/BD
tasks = {}

# Initialisation de l'analyseur de complémentarité
complementary_analyzer = None
trends_analyzer = None

# Chemin vers les données d'exemple (à remplacer par de vraies données)
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "samples")

# Fonction d'initialisation des analyseurs
def init_analyzers():
    """Initialise les analyseurs avec les données disponibles."""
    global complementary_analyzer, trends_analyzer
    
    try:
        # Initialisation de l'analyseur de tendances
        trends_analyzer = TrendsAnalyzer()
        logger.info("Analyseur de tendances initialisé avec succès")
        
        # Initialisation de l'analyseur de complémentarité
        complementary_analyzer = ComplementaryAnalyzer()
        
        # Charger des données d'exemple pour l'analyseur de complémentarité
        sample_transactions_path = os.path.join(SAMPLE_DATA_DIR, "sample_transactions.json")
        sample_products_path = os.path.join(SAMPLE_DATA_DIR, "sample_products.json")
        
        if os.path.exists(sample_transactions_path) and os.path.exists(sample_products_path):
            with open(sample_transactions_path, 'r') as f:
                transactions = json.load(f)
                
            with open(sample_products_path, 'r') as f:
                products = json.load(f)
                
            complementary_analyzer.load_transaction_data(transactions)
            complementary_analyzer.load_product_metadata(products)
            logger.info("Analyseur de complémentarité initialisé avec des données d'exemple")
        else:
            # Créer des données fictives minimales pour les tests
            transactions = [
                ["product1", "product2", "product3"],
                ["product1", "product4"],
                ["product2", "product3"],
                ["product1", "product2", "product4"],
                ["product3", "product5"]
            ]
            
            products = {
                "product1": {
                    "name": "Smartphone XYZ",
                    "category": "smartphones",
                    "price": 299.99,
                    "rating": 4.2,
                    "popularity": 85
                },
                "product2": {
                    "name": "Coque de protection",
                    "category": "phone_cases",
                    "price": 19.99,
                    "rating": 4.5,
                    "popularity": 92
                },
                "product3": {
                    "name": "Chargeur rapide",
                    "category": "chargers",
                    "price": 29.99,
                    "rating": 4.0,
                    "popularity": 78
                },
                "product4": {
                    "name": "Écouteurs sans fil",
                    "category": "headphones",
                    "price": 89.99,
                    "rating": 4.7,
                    "popularity": 90
                },
                "product5": {
                    "name": "Protection d'écran",
                    "category": "screen_protectors",
                    "price": 9.99,
                    "rating": 3.8,
                    "popularity": 65
                }
            }
            
            # Définir manuellement des paires de catégories complémentaires
            category_pairs = {
                "smartphones": ["phone_cases", "screen_protectors", "chargers", "headphones"],
                "phone_cases": ["screen_protectors", "smartphones"],
                "chargers": ["smartphones", "headphones"],
                "headphones": ["smartphones", "chargers"],
                "screen_protectors": ["smartphones", "phone_cases"]
            }
            
            complementary_analyzer.load_transaction_data(transactions)
            complementary_analyzer.load_product_metadata(products)
            complementary_analyzer.set_category_pairs(category_pairs)
            logger.info("Analyseur de complémentarité initialisé avec des données fictives")
            
            # Sauvegarder ces données pour les utilisations futures
            os.makedirs(SAMPLE_DATA_DIR, exist_ok=True)
            with open(sample_transactions_path, 'w') as f:
                json.dump(transactions, f)
            with open(sample_products_path, 'w') as f:
                json.dump(products, f)
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des analyseurs: {str(e)}")
        if complementary_analyzer is None:
            complementary_analyzer = ComplementaryAnalyzer()
        if trends_analyzer is None:
            trends_analyzer = TrendsAnalyzer()

# Initialisation au démarrage
@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'application."""
    init_analyzers()
    logger.info("Application Data Analyzer démarrée")

@app.get("/")
def read_root():
    """Point d'entrée principal."""
    return {
        "name": "Data Analyzer",
        "version": "0.1.0",
        "status": "online",
        "description": "Agent d'analyse de données pour le projet Dropshipping Autonome avec Crew AI"
    }

@app.get("/health")
def health_check():
    """Vérification de l'état de santé de l'agent."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "analyzers": {
            "complementary": complementary_analyzer is not None,
            "trends": trends_analyzer is not None
        }
    }

@app.post("/analyze")
async def analyze_market(urls_list: UrlsList, background_tasks: BackgroundTasks):
    """
    Analyse le marché à partir des URLs fournies.
    Cette opération peut prendre du temps et est exécutée en arrière-plan.
    """
    task_id = str(uuid.uuid4())
    
    # Enregistrer la tâche
    tasks[task_id] = {
        "status": "pending",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "params": {
            "urls": urls_list.urls,
            "market_segment": urls_list.market_segment,
            "min_margin": urls_list.min_margin
        },
        "result": None
    }
    
    # Lancer l'analyse en arrière-plan
    background_tasks.add_task(
        perform_market_analysis,
        task_id,
        urls_list.urls,
        urls_list.market_segment,
        urls_list.min_margin
    )
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Analyse en cours. Utilisez l'endpoint /tasks/{task_id} pour suivre la progression."
    }

@app.post("/action")
async def perform_action(action_request: ActionRequest, background_tasks: BackgroundTasks):
    """
    Effectue une action spécifique en fonction de la demande.
    Certaines actions peuvent être exécutées immédiatement, d'autres en arrière-plan.
    """
    # Vérification des analyseurs
    if complementary_analyzer is None or trends_analyzer is None:
        init_analyzers()
    
    # Actions qui peuvent être traitées immédiatement
    fast_actions = [
        "get_complementary_products",
        "get_upsell_products",
        "create_bundles",
        "analyze_cart"
    ]
    
    if action_request.action in fast_actions:
        try:
            result = None
            
            # Traitement de l'action demandée
            if action_request.action == "get_complementary_products" and action_request.product_id:
                max_products = action_request.max_products or 5
                result = complementary_analyzer.get_complementary_products(
                    action_request.product_id,
                    max_products=max_products
                )
                
            elif action_request.action == "get_upsell_products" and action_request.product_id:
                max_products = action_request.max_products or 3
                result = complementary_analyzer.get_upsell_products(
                    action_request.product_id,
                    max_products=max_products
                )
                
            elif action_request.action == "create_bundles" and action_request.product_ids:
                max_bundles = action_request.max_bundles or 3
                result = complementary_analyzer.bundle_products(
                    action_request.product_ids,
                    max_bundles=max_bundles
                )
                
            elif action_request.action == "analyze_cart" and action_request.product_ids:
                result = complementary_analyzer.analyze_cart(action_request.product_ids)
                
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Paramètres invalides pour l'action {action_request.action}"
                )
            
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de l'action {action_request.action}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de l'exécution de l'action: {str(e)}"
            )
    
    # Pour les actions plus longues, créer une tâche en arrière-plan
    task_id = str(uuid.uuid4())
    
    # Enregistrer la tâche
    tasks[task_id] = {
        "status": "pending",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "params": action_request.dict(),
        "result": None
    }
    
    # Lancer l'action en arrière-plan
    background_tasks.add_task(
        perform_background_action,
        task_id,
        action_request
    )
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": f"Action {action_request.action} en cours. Utilisez l'endpoint /tasks/{task_id} pour suivre la progression."
    }

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    """Récupère le statut d'une tâche spécifique."""
    if task_id not in tasks:
        raise HTTPException(
            status_code=404,
            detail=f"Tâche avec l'ID {task_id} non trouvée"
        )
    
    task = tasks[task_id]
    
    return {
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "created_at": task["created_at"],
        "result": task.get("result")
    }

# Fonctions d'arrière-plan pour les tâches longues
async def perform_market_analysis(task_id: str, urls: List[str], market_segment: Optional[str], min_margin: Optional[float]):
    """Effectue l'analyse de marché en arrière-plan."""
    try:
        # Mise à jour du statut
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 10
        
        # Simulation de traitement (à remplacer par une véritable analyse)
        await asyncio.sleep(2)  # Simulation du temps de traitement
        tasks[task_id]["progress"] = 30
        
        # Analyse des tendances
        await asyncio.sleep(2)
        tasks[task_id]["progress"] = 50
        
        # Analyse de la concurrence
        await asyncio.sleep(2)
        tasks[task_id]["progress"] = 70
        
        # Génération des recommandations
        await asyncio.sleep(2)
        tasks[task_id]["progress"] = 90
        
        # Résultats fictifs (à remplacer par de véritables résultats)
        result = {
            "top_products": [
                {
                    "name": f"Produit A ({urls[0]})",
                    "supplier_price": 15.99,
                    "recommended_price": 39.99,
                    "potential_margin_percent": 60.0,
                    "competition_level": "Moyen",
                    "trend_direction": "Hausse",
                    "recommendation_score": 8.7,
                    "justification": "Forte tendance à la hausse avec une concurrence modérée"
                },
                {
                    "name": f"Produit B ({urls[0]})",
                    "supplier_price": 10.50,
                    "recommended_price": 29.99,
                    "potential_margin_percent": 65.0,
                    "competition_level": "Faible",
                    "trend_direction": "Stable",
                    "recommendation_score": 7.9,
                    "justification": "Bonne marge avec peu de concurrence"
                }
            ],
            "analysis_date": datetime.now().isoformat(),
            "source_urls": urls,
            "market_segment": market_segment or "Non spécifié",
            "min_margin": min_margin or 30.0
        }
        
        # Mise à jour finale
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["result"] = result
        tasks[task_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de marché: {str(e)}")
        # Mise à jour en cas d'erreur
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

async def perform_background_action(task_id: str, action_request: ActionRequest):
    """Effectue une action en arrière-plan."""
    try:
        # Mise à jour du statut
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 10
        
        # Traitement selon l'action
        if action_request.action == "compare_products" and action_request.products:
            # Simulation de comparaison de produits (à remplacer par une vraie analyse)
            await asyncio.sleep(2)
            tasks[task_id]["progress"] = 50
            
            # Résultat fictif
            result = {
                "products": action_request.products,
                "timeframe": action_request.timeframe or "medium_term",
                "geo": action_request.geo,
                "comparisons": [
                    {
                        "product": product,
                        "trend_score": round(50 + 30 * (0.5 - (i / len(action_request.products))), 1),
                        "interest_over_time": {
                            "current": round(50 + 30 * (0.5 - (i / len(action_request.products))), 1),
                            "change_percent": round(10 - 5 * (i / len(action_request.products)), 1)
                        },
                        "seasonal_pattern": i % 2 == 0,
                        "recommendation": "Forte demande" if i == 0 else "Demande modérée" if i == 1 else "Faible demande"
                    }
                    for i, product in enumerate(action_request.products)
                ],
                "best_product": action_request.products[0],
                "analysis_date": datetime.now().isoformat()
            }
            
            tasks[task_id]["result"] = result
            
        else:
            # Action non supportée ou paramètres manquants
            raise ValueError(f"Action non supportée ou paramètres manquants: {action_request.action}")
        
        # Mise à jour finale
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action_request.action}: {str(e)}")
        # Mise à jour en cas d'erreur
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

# Lancer le serveur directement avec uvicorn pour les tests
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
