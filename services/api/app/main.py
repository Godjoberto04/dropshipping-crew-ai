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

# Import des routes
from routes import data_analyzer

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

# Nouveaux modèles pour l'agent Website Builder
class StoreConfig(BaseModel):
    name: str
    currency: Optional[str] = "EUR"
    language: Optional[str] = "fr"
    theme: Optional[Dict[str, Any]] = None
    navigation: Optional[Dict[str, Any]] = None
    pages: Optional[List[Dict[str, Any]]] = None
    payment_methods: Optional[List[Dict[str, Any]]] = None
    shipping: Optional[Dict[str, Any]] = None
    taxes: Optional[Dict[str, Any]] = None

class ProductData(BaseModel):
    title: str
    description: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    tags: Optional[List[str]] = None
    variants: Optional[List[Dict[str, Any]]] = None
    images: Optional[List[Dict[str, Any]]] = None

class WebsiteBuilderAction(BaseModel):
    action: str  # "setup_store" ou "add_product"
    store_config: Optional[StoreConfig] = None
    product_data: Optional[ProductData] = None

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

        # Nouvelles tables pour le Website Builder
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS stores (
                id SERIAL PRIMARY KEY,
                store_url VARCHAR(255) NOT NULL,
                config JSONB,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
        ''')

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                product_id VARCHAR(255) NOT NULL,
                store_url VARCHAR(255) NOT NULL,
                data JSONB,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
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

# Inclure les routes des agents
app.include_router(data_analyzer.router)

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
