"""
Routes pour l'agent Data Analyzer
Inclut les endpoints pour l'analyse de marché, les tendances, et la complémentarité de produits.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
import asyncio
import json
import uuid
from datetime import datetime
import aioredis
import asyncpg
import httpx
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

# Modèles de données
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

class ComplementaryProductsRequest(BaseModel):
    product_id: str
    max_products: Optional[int] = 5

class UpsellProductsRequest(BaseModel):
    product_id: str
    max_products: Optional[int] = 3

class BundleRequest(BaseModel):
    product_ids: List[str]
    max_bundles: Optional[int] = 3

class CartAnalysisRequest(BaseModel):
    product_ids: List[str]

# Création du routeur
router = APIRouter(
    prefix="/agents/data-analyzer",
    tags=["data-analyzer"],
    responses={404: {"description": "Agent non trouvé"}},
)

# Connexion à Redis
async def get_redis():
    """Récupère une connexion Redis."""
    import os
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_password = os.getenv("REDIS_PASSWORD", "")
    redis_url = f"redis://:{redis_password}@{redis_host}:6379/0"
    return await aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)

# Connexion au pool de base de données
async def get_db_pool():
    """Récupère un pool de connexions à la base de données."""
    import os
    postgres_user = os.getenv("POSTGRES_USER", "postgres")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    postgres_db = os.getenv("POSTGRES_DB", "dropshipping")
    postgres_host = os.getenv("POSTGRES_HOST", "postgres")
    
    return await asyncpg.create_pool(
        user=postgres_user,
        password=postgres_password,
        database=postgres_db,
        host=postgres_host
    )

@router.get("/status")
async def get_agent_status(redis = Depends(get_redis)):
    """Récupère le statut de l'agent Data Analyzer."""
    status = await redis.hgetall("agent:data-analyzer")
    
    if not status:
        status = {
            "status": "unknown",
            "version": "0.1.0",
            "capabilities": json.dumps(["market_analysis", "product_trends", "complementary_analysis"]),
            "last_run": None
        }
    else:
        # Conversion des chaînes JSON en objets Python
        if "capabilities" in status and status["capabilities"]:
            try:
                status["capabilities"] = json.loads(status["capabilities"])
            except json.JSONDecodeError:
                status["capabilities"] = []
    
    return status

@router.post("/analyze", status_code=202)
async def analyze_market(
    urls_list: UrlsList,
    background_tasks: BackgroundTasks,
    redis = Depends(get_redis),
    db_pool = Depends(get_db_pool)
):
    """
    Déclenche une analyse de marché basée sur les URLs fournies.
    
    Cette opération est exécutée en arrière-plan et peut prendre un certain temps.
    """
    # Générer un ID de tâche
    task_id = str(uuid.uuid4())
    
    # Enregistrer la tâche dans la base de données
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO tasks (id, agent_id, status, params)
            VALUES ($1, $2, $3, $4)
            """,
            task_id,
            "data-analyzer",
            "pending",
            json.dumps({
                "urls": urls_list.urls,
                "market_segment": urls_list.market_segment,
                "min_margin": urls_list.min_margin
            })
        )
    
    # Notifier l'agent via Redis
    await redis.publish(
        "agent:data-analyzer:tasks",
        json.dumps({
            "task_id": task_id,
            "action": "analyze_market",
            "params": {
                "urls": urls_list.urls,
                "market_segment": urls_list.market_segment,
                "min_margin": urls_list.min_margin
            }
        })
    )
    
    # Stocker l'état initial de la tâche dans Redis
    await redis.hset(
        f"task:{task_id}",
        mapping={
            "status": "pending",
            "progress": "0",
            "agent_id": "data-analyzer",
            "created_at": datetime.now().isoformat()
        }
    )
    
    # Définir une durée d'expiration pour les données Redis (1 jour)
    await redis.expire(f"task:{task_id}", 86400)
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Analyse en cours. Utilisez l'endpoint /tasks/{task_id} pour suivre la progression."
    }

@router.post("/action", status_code=200)
async def perform_action(
    action_request: ActionRequest,
    background_tasks: BackgroundTasks,
    redis = Depends(get_redis)
):
    """
    Effectue une action spécifique avec l'agent Data Analyzer.
    
    Actions supportées:
    - compare_products: Compare plusieurs produits en termes de tendances
    - get_complementary_products: Récupère des produits complémentaires pour un produit donné
    - get_upsell_products: Récupère des suggestions d'up-sell pour un produit donné
    - create_bundles: Crée des bundles de produits à partir d'une liste
    - analyze_cart: Analyse un panier pour suggérer des améliorations
    """
    # Vérifier que l'action est valide
    valid_actions = [
        "compare_products", 
        "get_complementary_products", 
        "get_upsell_products", 
        "create_bundles", 
        "analyze_cart"
    ]
    
    if action_request.action not in valid_actions:
        raise HTTPException(
            status_code=400,
            detail=f"Action non supportée. Les actions valides sont: {', '.join(valid_actions)}"
        )
    
    # Valider les paramètres selon l'action
    if action_request.action == "compare_products" and not action_request.products:
        raise HTTPException(
            status_code=400,
            detail="Le paramètre 'products' est requis pour l'action 'compare_products'"
        )
    
    if action_request.action == "get_complementary_products" and not action_request.product_id:
        raise HTTPException(
            status_code=400,
            detail="Le paramètre 'product_id' est requis pour l'action 'get_complementary_products'"
        )
    
    if action_request.action == "get_upsell_products" and not action_request.product_id:
        raise HTTPException(
            status_code=400,
            detail="Le paramètre 'product_id' est requis pour l'action 'get_upsell_products'"
        )
    
    if action_request.action == "create_bundles" and not action_request.product_ids:
        raise HTTPException(
            status_code=400,
            detail="Le paramètre 'product_ids' est requis pour l'action 'create_bundles'"
        )
    
    if action_request.action == "analyze_cart" and not action_request.product_ids:
        raise HTTPException(
            status_code=400,
            detail="Le paramètre 'product_ids' est requis pour l'action 'analyze_cart'"
        )
    
    # Créer un ID de tâche
    task_id = str(uuid.uuid4())
    
    # Préparer les paramètres pour l'agent
    params = {
        "action": action_request.action
    }
    
    if action_request.products:
        params["products"] = action_request.products
    
    if action_request.product_id:
        params["product_id"] = action_request.product_id
    
    if action_request.timeframe:
        params["timeframe"] = action_request.timeframe
    
    if action_request.geo:
        params["geo"] = action_request.geo
    
    if action_request.max_products:
        params["max_products"] = action_request.max_products
    
    if action_request.product_ids:
        params["product_ids"] = action_request.product_ids
    
    if action_request.max_bundles:
        params["max_bundles"] = action_request.max_bundles
    
    # Notifier l'agent via Redis
    await redis.publish(
        "agent:data-analyzer:tasks",
        json.dumps({
            "task_id": task_id,
            "action": action_request.action,
            "params": params
        })
    )
    
    # Stocker l'état initial de la tâche dans Redis
    await redis.hset(
        f"task:{task_id}",
        mapping={
            "status": "pending",
            "progress": "0",
            "agent_id": "data-analyzer",
            "created_at": datetime.now().isoformat()
        }
    )
    
    # Définir une durée d'expiration pour les données Redis (1 jour)
    await redis.expire(f"task:{task_id}", 86400)
    
    # Pour certaines actions, essayer de retourner un résultat immédiatement si possible
    # avec un appel direct à l'agent Data Analyzer
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://data-analyzer:8000/action",
                json=params,
                timeout=5.0  # Timeout court pour ne pas bloquer l'API
            )
            
            if response.status_code == 200:
                # Mettre à jour le statut de la tâche
                await redis.hset(
                    f"task:{task_id}",
                    mapping={
                        "status": "completed",
                        "progress": "100",
                        "result": json.dumps(response.json()),
                        "completed_at": datetime.now().isoformat()
                    }
                )
                
                return {
                    "task_id": task_id,
                    "status": "completed",
                    "result": response.json()
                }
            
    except (httpx.RequestError, asyncio.TimeoutError) as e:
        # Si l'appel direct échoue, on continue avec le traitement asynchrone
        logger.warning(f"Appel direct à l'agent Data Analyzer échoué: {str(e)}")
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Action en cours. Utilisez l'endpoint /tasks/{task_id} pour suivre la progression."
    }

@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    redis = Depends(get_redis),
    db_pool = Depends(get_db_pool)
):
    """Récupère le statut d'une tâche spécifique."""
    # Essayer d'abord de récupérer depuis Redis (plus rapide)
    task_data = await redis.hgetall(f"task:{task_id}")
    
    if task_data:
        # Convertir les données au format approprié
        if "progress" in task_data:
            try:
                task_data["progress"] = int(task_data["progress"])
            except (ValueError, TypeError):
                task_data["progress"] = 0
        
        if "result" in task_data and task_data["result"]:
            try:
                task_data["result"] = json.loads(task_data["result"])
            except json.JSONDecodeError:
                task_data["result"] = None
        
        return {
            "task_id": task_id,
            **task_data
        }
    
    # Si pas dans Redis, chercher dans la base de données
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, agent_id, status, created_at, updated_at, progress, params, result
            FROM tasks
            WHERE id = $1
            """,
            task_id
        )
    
    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Tâche avec l'ID {task_id} non trouvée"
        )
    
    # Convertir row en dictionnaire
    task_data = dict(row)
    
    # Convertir les champs JSON
    if task_data["params"]:
        task_data["params"] = json.loads(task_data["params"])
    
    if task_data["result"]:
        task_data["result"] = json.loads(task_data["result"])
    
    # Convertir les dates en chaînes ISO
    if task_data["created_at"]:
        task_data["created_at"] = task_data["created_at"].isoformat()
    
    if task_data["updated_at"]:
        task_data["updated_at"] = task_data["updated_at"].isoformat()
    
    return task_data

# Routes spécifiques pour les fonctionnalités d'analyse de complémentarité
@router.post("/complementary-products", status_code=200)
async def get_complementary_products(
    request: ComplementaryProductsRequest,
    redis = Depends(get_redis)
):
    """
    Récupère des produits complémentaires pour un produit donné.
    C'est un endpoint simplifié par rapport à l'action générale.
    """
    params = {
        "action": "get_complementary_products",
        "product_id": request.product_id,
        "max_products": request.max_products
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://data-analyzer:8000/action",
                json=params,
                timeout=5.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # Fallback si le service direct n'est pas disponible
                task_id = str(uuid.uuid4())
                
                await redis.publish(
                    "agent:data-analyzer:tasks",
                    json.dumps({
                        "task_id": task_id,
                        "action": "get_complementary_products",
                        "params": params
                    })
                )
                
                await redis.hset(
                    f"task:{task_id}",
                    mapping={
                        "status": "pending",
                        "progress": "0",
                        "agent_id": "data-analyzer",
                        "created_at": datetime.now().isoformat()
                    }
                )
                
                await redis.expire(f"task:{task_id}", 86400)
                
                return {
                    "task_id": task_id,
                    "status": "pending",
                    "message": "Analyse des produits complémentaires en cours."
                }
                
    except (httpx.RequestError, asyncio.TimeoutError):
        # Fallback si le service n'est pas disponible
        return {
            "error": "Service temporairement indisponible",
            "message": "Essayez d'utiliser l'endpoint /action avec l'action 'get_complementary_products'"
        }

@router.post("/upsell-products", status_code=200)
async def get_upsell_products(
    request: UpsellProductsRequest,
    redis = Depends(get_redis)
):
    """
    Récupère des suggestions d'up-sell pour un produit donné.
    C'est un endpoint simplifié par rapport à l'action générale.
    """
    params = {
        "action": "get_upsell_products",
        "product_id": request.product_id,
        "max_products": request.max_products
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://data-analyzer:8000/action",
                json=params,
                timeout=5.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # Fallback si le service direct n'est pas disponible
                task_id = str(uuid.uuid4())
                
                await redis.publish(
                    "agent:data-analyzer:tasks",
                    json.dumps({
                        "task_id": task_id,
                        "action": "get_upsell_products",
                        "params": params
                    })
                )
                
                await redis.hset(
                    f"task:{task_id}",
                    mapping={
                        "status": "pending",
                        "progress": "0",
                        "agent_id": "data-analyzer",
                        "created_at": datetime.now().isoformat()
                    }
                )
                
                await redis.expire(f"task:{task_id}", 86400)
                
                return {
                    "task_id": task_id,
                    "status": "pending",
                    "message": "Analyse des produits d'up-sell en cours."
                }
                
    except (httpx.RequestError, asyncio.TimeoutError):
        # Fallback si le service n'est pas disponible
        return {
            "error": "Service temporairement indisponible",
            "message": "Essayez d'utiliser l'endpoint /action avec l'action 'get_upsell_products'"
        }

@router.post("/create-bundles", status_code=200)
async def create_bundles(
    request: BundleRequest,
    redis = Depends(get_redis)
):
    """
    Crée des bundles de produits à partir d'une liste de produits.
    C'est un endpoint simplifié par rapport à l'action générale.
    """
    params = {
        "action": "create_bundles",
        "product_ids": request.product_ids,
        "max_bundles": request.max_bundles
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://data-analyzer:8000/action",
                json=params,
                timeout=5.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # Fallback si le service direct n'est pas disponible
                task_id = str(uuid.uuid4())
                
                await redis.publish(
                    "agent:data-analyzer:tasks",
                    json.dumps({
                        "task_id": task_id,
                        "action": "create_bundles",
                        "params": params
                    })
                )
                
                await redis.hset(
                    f"task:{task_id}",
                    mapping={
                        "status": "pending",
                        "progress": "0",
                        "agent_id": "data-analyzer",
                        "created_at": datetime.now().isoformat()
                    }
                )
                
                await redis.expire(f"task:{task_id}", 86400)
                
                return {
                    "task_id": task_id,
                    "status": "pending",
                    "message": "Création de bundles en cours."
                }
                
    except (httpx.RequestError, asyncio.TimeoutError):
        # Fallback si le service n'est pas disponible
        return {
            "error": "Service temporairement indisponible",
            "message": "Essayez d'utiliser l'endpoint /action avec l'action 'create_bundles'"
        }

@router.post("/analyze-cart", status_code=200)
async def analyze_cart(
    request: CartAnalysisRequest,
    redis = Depends(get_redis)
):
    """
    Analyse un panier pour suggérer des améliorations.
    C'est un endpoint simplifié par rapport à l'action générale.
    """
    params = {
        "action": "analyze_cart",
        "product_ids": request.product_ids
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://data-analyzer:8000/action",
                json=params,
                timeout=5.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # Fallback si le service direct n'est pas disponible
                task_id = str(uuid.uuid4())
                
                await redis.publish(
                    "agent:data-analyzer:tasks",
                    json.dumps({
                        "task_id": task_id,
                        "action": "analyze_cart",
                        "params": params
                    })
                )
                
                await redis.hset(
                    f"task:{task_id}",
                    mapping={
                        "status": "pending",
                        "progress": "0",
                        "agent_id": "data-analyzer",
                        "created_at": datetime.now().isoformat()
                    }
                )
                
                await redis.expire(f"task:{task_id}", 86400)
                
                return {
                    "task_id": task_id,
                    "status": "pending",
                    "message": "Analyse du panier en cours."
                }
                
    except (httpx.RequestError, asyncio.TimeoutError):
        # Fallback si le service n'est pas disponible
        return {
            "error": "Service temporairement indisponible",
            "message": "Essayez d'utiliser l'endpoint /action avec l'action 'analyze_cart'"
        }
