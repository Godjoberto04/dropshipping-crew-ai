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
