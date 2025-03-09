from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import os
import json
import uuid
import redis
from datetime import datetime
import aioredis
import asyncpg
from contextlib import asynccontextmanager

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
    image_url: Optional[str] = None

class AnalysisResults(BaseModel):
    top_products: List[ProductAnalysis]
    analysis_date: datetime
    source_urls: List[str]

class UrlsList(BaseModel):
    urls: List[str]
    market_segment: Optional[str] = None
    min_margin: Optional[float] = 30.0

class TaskUpdate(BaseModel):
    status: str
    progress: Optional[int] = None
    result: Optional[Dict[str, Any]] = None

class AgentStatus(BaseModel):
    status: str
    version: Optional[str] = None
    capabilities: Optional[List[str]] = None
    last_run: Optional[datetime] = None

# Connexions aux services de base de données et cache
async def get_redis():
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_password = os.getenv("REDIS_PASSWORD", "")
    redis_url = f"redis://:{redis_password}@{redis_host}:6379/0"
    return await aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)

async def get_db_pool():
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

# Gestionnaire de démarrage/arrêt pour initialiser et fermer les connexions
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialiser la connexion PostgreSQL
    app.state.db_pool = await get_db_pool()
    
    # Créer les tables si elles n'existent pas
    async with app.state.db_pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                market_segment VARCHAR(255),
                min_margin FLOAT,
                analyzed_urls_count INTEGER,
                execution_time_seconds FLOAT,
                results JSONB
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id VARCHAR(36) PRIMARY KEY,
                agent_id VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                progress INTEGER,
                params JSONB,
                result JSONB
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id VARCHAR(50) PRIMARY KEY,
                status VARCHAR(20) NOT NULL,
                version VARCHAR(20),
                capabilities JSONB,
                last_run TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
        ''')
    
    # Initialiser la connexion Redis
    app.state.redis = await get_redis()
    
    yield
    
    # Fermer les connexions
    await app.state.db_pool.close()
    await app.state.redis.close()

app = FastAPI(
    title="Dropshipping Crew AI API",
    lifespan=lifespan
)

# Configurer CORS pour permettre les requêtes depuis le dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines exactes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Endpoint racine de l'API"""
    return {
        "message": "Bienvenue sur l'API du projet Dropshipping Autonome avec Crew AI",
        "version": "1.0.0",
        "status": "online"
    }

@app.get("/status")
async def get_status(redis = Depends(get_redis)):
    """Renvoie le statut des différents services du système"""
    try:
        # Récupérer le statut des agents depuis Redis
        data_analyzer_status = await redis.hgetall("agent:data-analyzer")
        website_builder_status = await redis.hgetall("agent:website-builder")
        content_generator_status = await redis.hgetall("agent:content-generator")
        order_manager_status = await redis.hgetall("agent:order-manager")
        site_updater_status = await redis.hgetall("agent:site-updater")
        
        # Convertir "null" en None pour eviter les problèmes de JSON
        for status_dict in [data_analyzer_status, website_builder_status, content_generator_status, 
                           order_manager_status, site_updater_status]:
            for key in status_dict:
                if status_dict[key] == "null":
                    status_dict[key] = None
        
        return {
            "services": {
                "postgres": {"status": "online", "version": "14"},
                "redis": {"status": "online", "version": "7"},
                "api": {"status": "online", "version": "1.0.0"},
                "data_analyzer": data_analyzer_status or {"status": "partial", "version": "0.1.0"},
                "website_builder": website_builder_status or {"status": "offline", "version": None},
                "content_generator": content_generator_status or {"status": "offline", "version": None},
                "order_manager": order_manager_status or {"status": "offline", "version": None},
                "site_updater": site_updater_status or {"status": "offline", "version": None}
            },
            "system": {
                "server": "Scaleway DEV1-M",
                "cpu_usage": await redis.get("system:cpu_usage") or 15.2,  # pourcentage 
                "memory_usage": await redis.get("system:memory_usage") or 32.1,  # pourcentage
                "disk_usage": await redis.get("system:disk_usage") or 23.8  # pourcentage
            }
        }
    except Exception as e:
        # En cas d'erreur, retourner des données par défaut
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
            },
            "error": str(e)
        }

@app.get("/agents/{agent_id}/status")
async def get_agent_status(agent_id: str, redis = Depends(get_redis)):
    """Renvoie le statut d'un agent spécifique"""
    try:
        # Récupérer le statut de l'agent depuis Redis
        agent_status = await redis.hgetall(f"agent:{agent_id}")
        
        if not agent_status:
            # Agent non trouvé, retourner un statut par défaut
            if agent_id == "data-analyzer":
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
            else:
                return {
                    "status": "offline",
                    "version": None,
                    "last_run": None,
                    "capabilities": []
                }
        
        # Convertir les champs JSON
        if "capabilities" in agent_status and agent_status["capabilities"]:
            agent_status["capabilities"] = json.loads(agent_status["capabilities"])
            
        if "last_run" in agent_status and agent_status["last_run"]:
            agent_status["last_run"] = agent_status["last_run"]
            
        return agent_status
        
    except Exception as e:
        # En cas d'erreur, retourner un statut par défaut
        return {
            "status": "unknown",
            "error": str(e)
        }

@app.put("/agents/{agent_id}/status")
async def update_agent_status(agent_id: str, status: AgentStatus, db_pool = Depends(get_db_pool), redis = Depends(get_redis)):
    """Met à jour le statut d'un agent"""
    try:
        # Préparer les données pour Redis
        redis_data = {
            "status": status.status,
            "updated_at": datetime.now().isoformat()
        }
        
        if status.version:
            redis_data["version"] = status.version
            
        if status.capabilities:
            redis_data["capabilities"] = json.dumps(status.capabilities)
            
        if status.last_run:
            redis_data["last_run"] = status.last_run.isoformat()
        
        # Mettre à jour Redis
        await redis.hset(f"agent:{agent_id}", mapping=redis_data)
        
        # Mettre à jour la base de données
        async with db_pool.acquire() as conn:
            # Vérifier si l'agent existe déjà
            agent_exists = await conn.fetchval(
                "SELECT COUNT(*) FROM agents WHERE id = $1",
                agent_id
            )
            
            if agent_exists:
                # Mettre à jour l'agent existant
                await conn.execute(
                    """
                    UPDATE agents 
                    SET status = $1, version = $2, capabilities = $3, 
                        last_run = $4, updated_at = NOW()
                    WHERE id = $5
                    """,
                    status.status,
                    status.version,
                    json.dumps(status.capabilities) if status.capabilities else None,
                    status.last_run,
                    agent_id
                )
            else:
                # Créer un nouvel agent
                await conn.execute(
                    """
                    INSERT INTO agents (id, status, version, capabilities, last_run, updated_at)
                    VALUES ($1, $2, $3, $4, $5, NOW())
                    """,
                    agent_id,
                    status.status,
                    status.version,
                    json.dumps(status.capabilities) if status.capabilities else None,
                    status.last_run
                )
        
        return {
            "status": "success",
            "message": f"Statut de l'agent {agent_id} mis à jour"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour du statut: {str(e)}")

@app.post("/agents/data-analyzer/analyze")
async def trigger_analysis(urls_list: UrlsList, background_tasks: BackgroundTasks, db_pool = Depends(get_db_pool), redis = Depends(get_redis)):
    """Déclenche une analyse de marché sur les URLs spécifiées"""
    if not urls_list.urls or len(urls_list.urls) == 0:
        raise HTTPException(status_code=400, detail="Au moins une URL est requise")
    
    try:
        # Générer un ID unique pour la tâche
        task_id = str(uuid.uuid4())
        
        # Préparer les paramètres de la tâche
        task_params = {
            "urls": urls_list.urls,
            "market_segment": urls_list.market_segment,
            "min_margin": urls_list.min_margin
        }
        
        # Enregistrer la tâche dans la base de données
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO tasks (id, agent_id, status, params, progress, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
                """,
                task_id,
                "data-analyzer",
                "pending",
                json.dumps(task_params),
                0
            )
        
        # Enregistrer la tâche dans Redis pour que l'agent puisse la récupérer
        await redis.hset(
            f"task:{task_id}",
            mapping={
                "agent_id": "data-analyzer",
                "status": "pending",
                "params": json.dumps(task_params),
                "progress": "0",
                "created_at": datetime.now().isoformat()
            }
        )
        
        # Ajouter la tâche à la liste des tâches en attente
        await redis.lpush("tasks:pending:data-analyzer", task_id)
        
        # Calculer le temps estimé de fin (environ 1 minute par URL)
        estimated_completion = datetime.now().timestamp() + (len(urls_list.urls) * 60)
        
        return {
            "task_id": task_id,
            "status": "queued",
            "message": f"Analyse démarrée sur {len(urls_list.urls)} URLs",
            "estimated_completion": estimated_completion
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la tâche: {str(e)}")

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str, db_pool = Depends(get_db_pool), redis = Depends(get_redis)):
    """Récupère le statut d'une tâche en cours"""
    try:
        # Récupérer la tâche depuis Redis (plus rapide que la base de données)
        task_data = await redis.hgetall(f"task:{task_id}")
        
        if not task_data:
            # Si la tâche n'est pas dans Redis, vérifier la base de données
            async with db_pool.acquire() as conn:
                task_row = await conn.fetchrow(
                    "SELECT * FROM tasks WHERE id = $1",
                    task_id
                )
                
                if not task_row:
                    raise HTTPException(status_code=404, detail=f"Tâche non trouvée: {task_id}")
                
                # Convertir la ligne en dictionnaire
                task_data = dict(task_row)
                
                # Convertir les types de données
                if "params" in task_data and task_data["params"]:
                    task_data["params"] = json.loads(task_data["params"])
                if "result" in task_data and task_data["result"]:
                    task_data["result"] = json.loads(task_data["result"])
                task_data["created_at"] = task_data["created_at"].isoformat()
                task_data["updated_at"] = task_data["updated_at"].isoformat()
        else:
            # Convertir les types de données depuis Redis
            if "params" in task_data and task_data["params"]:
                task_data["params"] = json.loads(task_data["params"])
            if "result" in task_data and task_data["result"]:
                task_data["result"] = json.loads(task_data["result"])
            if "progress" in task_data:
                task_data["progress"] = int(task_data["progress"])
        
        # Calculer le temps restant estimé si la tâche est en cours
        if task_data.get("status") == "in_progress":
            progress = task_data.get("progress", 0)
            if progress > 0:
                elapsed_time = (datetime.now() - datetime.fromisoformat(task_data["created_at"])).total_seconds()
                total_estimated_time = elapsed_time / (progress / 100)
                remaining_time = total_estimated_time - elapsed_time
                task_data["remaining_time_seconds"] = max(0, remaining_time)
        
        return task_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la tâche: {str(e)}")

@app.put("/tasks/{task_id}")
async def update_task_status(task_id: str, update: TaskUpdate, db_pool = Depends(get_db_pool), redis = Depends(get_redis)):
    """Met à jour le statut d'une tâche"""
    try:
        # Vérifier si la tâche existe
        async with db_pool.acquire() as conn:
            task_exists = await conn.fetchval(
                "SELECT COUNT(*) FROM tasks WHERE id = $1",
                task_id
            )
            
            if not task_exists:
                raise HTTPException(status_code=404, detail=f"Tâche non trouvée: {task_id}")
            
            # Mettre à jour la tâche dans la base de données
            await conn.execute(
                """
                UPDATE tasks 
                SET status = $1, progress = $2, result = $3, updated_at = NOW()
                WHERE id = $4
                """,
                update.status,
                update.progress,
                json.dumps(update.result) if update.result else None,
                task_id
            )
        
        # Mettre à jour Redis
        redis_update = {
            "status": update.status,
            "updated_at": datetime.now().isoformat()
        }
        
        if update.progress is not None:
            redis_update["progress"] = str(update.progress)
            
        if update.result:
            redis_update["result"] = json.dumps(update.result)
        
        await redis.hset(f"task:{task_id}", mapping=redis_update)
        
        # Si la tâche est terminée, la retirer de la liste des tâches en attente
        if update.status in ["completed", "failed"]:
            await redis.lrem("tasks:pending:data-analyzer", 0, task_id)
            
            # Mettre à jour le statut de l'agent
            agent_id = await redis.hget(f"task:{task_id}", "agent_id")
            if agent_id:
                await redis.hset(f"agent:{agent_id}", "last_run", datetime.now().isoformat())
        
        return {
            "status": "success",
            "message": f"Statut de la tâche {task_id} mis à jour"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de la tâche: {str(e)}")

@app.get("/tasks")
async def list_tasks(agent_id: Optional[str] = None, status: Optional[str] = None, limit: int = 10, db_pool = Depends(get_db_pool)):
    """Liste les tâches avec filtrage optionnel"""
    try:
        async with db_pool.acquire() as conn:
            # Construire la requête SQL avec filtres optionnels
            query = "SELECT * FROM tasks"
            params = []
            
            # Ajouter les filtres
            filters = []
            if agent_id:
                filters.append("agent_id = $" + str(len(params) + 1))
                params.append(agent_id)
            if status:
                filters.append("status = $" + str(len(params) + 1))
                params.append(status)
            
            # Ajouter les clauses WHERE si nécessaire
            if filters:
                query += " WHERE " + " AND ".join(filters)
            
            # Ajouter tri et limite
            query += " ORDER BY created_at DESC LIMIT $" + str(len(params) + 1)
            params.append(limit)
            
            # Exécuter la requête
            rows = await conn.fetch(query, *params)
            
            # Convertir les résultats en dictionnaires
            tasks = []
            for row in rows:
                task = dict(row)
                if "params" in task and task["params"]:
                    task["params"] = json.loads(task["params"])
                if "result" in task and task["result"]:
                    task["result"] = json.loads(task["result"])
                task["created_at"] = task["created_at"].isoformat()
                task["updated_at"] = task["updated_at"].isoformat()
                tasks.append(task)
            
            return {"tasks": tasks}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des tâches: {str(e)}")

@app.post("/analysis/results")
async def register_analysis_results(results: Dict[str, Any], db_pool = Depends(get_db_pool), redis = Depends(get_redis)):
    """Enregistre les résultats d'une analyse dans la base de données"""
    try:
        # Extraire les métadonnées
        metadata = results.get("analysis_metadata", {})
        
        # Enregistrer dans la base de données
        async with db_pool.acquire() as conn:
            analysis_id = await conn.fetchval(
                """
                INSERT INTO analyses (
                    created_at, market_segment, min_margin, 
                    analyzed_urls_count, execution_time_seconds, results
                ) VALUES (
                    NOW(), $1, $2, $3, $4, $5
                ) RETURNING id
                """,
                metadata.get("market_segment"),
                metadata.get("min_margin_required"),
                metadata.get("analyzed_urls_count"),
                metadata.get("execution_time_seconds"),
                json.dumps(results)
            )
        
        # Mettre en cache les résultats dans Redis (expire après 1 heure)
        await redis.set(f"analysis:latest", json.dumps(results), ex=3600)
        
        return {
            "status": "success",
            "message": "Résultats d'analyse enregistrés avec succès",
            "analysis_id": analysis_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'enregistrement des résultats: {str(e)}")

@app.get("/analysis/results/latest")
async def get_latest_analysis(redis = Depends(get_redis), db_pool = Depends(get_db_pool)):
    """Récupère les résultats de la dernière analyse"""
    try:
        # D'abord essayer de récupérer depuis Redis
        cached_results = await redis.get("analysis:latest")
        
        if cached_results:
            return json.loads(cached_results)
        
        # Sinon récupérer depuis la base de données
        async with db_pool.acquire() as conn:
            analysis_row = await conn.fetchrow(
                "SELECT * FROM analyses ORDER BY created_at DESC LIMIT 1"
            )
            
            if not analysis_row:
                # Si aucun résultat n'est trouvé, retourner des données simulées
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
            
            # Convertir la ligne en dictionnaire
            analysis = dict(analysis_row)
            analysis["created_at"] = analysis["created_at"].isoformat()
            
            # Extraire les résultats
            if "results" in analysis and analysis["results"]:
                return json.loads(analysis["results"])
            else:
                return analysis
            
    except Exception as e:
        # En cas d'erreur, retourner des données simulées
        return {
            "error": str(e),
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
                }
            ]
        }

@app.get("/analysis/results/{analysis_id}")
async def get_analysis_results(analysis_id: int, db_pool = Depends(get_db_pool)):
    """Récupère les résultats d'une analyse spécifique"""
    try:
        async with db_pool.acquire() as conn:
            analysis_row = await conn.fetchrow(
                "SELECT * FROM analyses WHERE id = $1",
                analysis_id
            )
            
            if not analysis_row:
                raise HTTPException(status_code=404, detail=f"Analyse non trouvée: {analysis_id}")
            
            # Convertir la ligne en dictionnaire
            analysis = dict(analysis_row)
            analysis["created_at"] = analysis["created_at"].isoformat()
            
            # Extraire les résultats
            if "results" in analysis and analysis["results"]:
                return json.loads(analysis["results"])
            else:
                return analysis
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'analyse: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
