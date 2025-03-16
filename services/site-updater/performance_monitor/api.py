"""
API Module pour le Performance Monitor
Ce module expose les fonctionnalités du Performance Monitor via une API FastAPI
"""

import logging
import asyncio
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Path, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl

from performance_manager import PerformanceManager
from performance_utils import ImageOptimizer, ResourceMinifier, PerformanceMetricsAnalyzer, SEOPerformanceAnalyzer

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PerformanceMonitorAPI")

# Création de l'application FastAPI
app = FastAPI(
    title="Performance Monitor API",
    description="API pour la surveillance et l'optimisation des performances des sites e-commerce",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles de données
class URLInput(BaseModel):
    url: HttpUrl = Field(..., description="URL du site à analyser")

class PerformanceThresholds(BaseModel):
    page_load_time: float = Field(3.0, description="Seuil pour le temps de chargement de page (secondes)")
    time_to_first_byte: float = Field(0.6, description="Seuil pour le TTFB (secondes)")
    first_contentful_paint: float = Field(1.8, description="Seuil pour le FCP (secondes)")
    largest_contentful_paint: float = Field(2.5, description="Seuil pour le LCP (secondes)")
    cumulative_layout_shift: float = Field(0.1, description="Seuil pour le CLS")
    first_input_delay: float = Field(0.1, description="Seuil pour le FID (secondes)")
    server_response_time: float = Field(0.5, description="Seuil pour le temps de réponse serveur (secondes)")

class OptimizationSettings(BaseModel):
    apply_automatically: bool = Field(True, description="Appliquer automatiquement les optimisations")
    minify_js_css: bool = Field(True, description="Minifier les fichiers JS et CSS")
    optimize_images: bool = Field(True, description="Optimiser les images")
    target_image_format: str = Field("webp", description="Format cible pour les images")
    compress_resources: bool = Field(True, description="Compresser les ressources")

class MonitoringSettings(BaseModel):
    url: HttpUrl = Field(..., description="URL à surveiller")
    interval_hours: int = Field(24, description="Intervalle de surveillance en heures")
    days: int = Field(7, description="Nombre de jours à surveiller")
    alert_on_regression: bool = Field(True, description="Alerter en cas de régression")
    regression_threshold: float = Field(10.0, description="Seuil de régression en pourcentage")

class ImageBatchOptimizationInput(BaseModel):
    image_urls: List[str] = Field(..., description="Liste des URLs d'images à optimiser")
    target_format: str = Field("webp", description="Format cible pour les images")

# Instance du gestionnaire de performance
performance_manager = None

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'API"""
    global performance_manager
    
    # Récupération des variables d'environnement
    api_url = os.getenv("API_URL", "http://localhost:8000/api")
    shopify_api_key = os.getenv("SHOPIFY_API_KEY", "")
    shopify_api_secret = os.getenv("SHOPIFY_API_SECRET", "")
    shopify_store_url = os.getenv("SHOPIFY_STORE_URL", "")
    
    if not all([shopify_api_key, shopify_api_secret, shopify_store_url]):
        logger.warning("Variables d'environnement Shopify manquantes, certaines fonctionnalités seront limitées")
    
    # Initialisation du gestionnaire de performance
    performance_manager = PerformanceManager(
        api_url=api_url,
        shopify_api_key=shopify_api_key,
        shopify_api_secret=shopify_api_secret,
        shopify_store_url=shopify_store_url
    )
    
    logger.info("Performance Monitor API démarrée")

@app.get("/", summary="Statut de l'API")
async def read_root():
    """Endpoint racine pour vérifier le statut de l'API"""
    return {
        "status": "online",
        "name": "Performance Monitor API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze", summary="Analyser les performances d'une URL", response_model=Dict[str, Any])
async def analyze_performance(url_input: URLInput):
    """Analyser les performances d'une URL spécifique"""
    if performance_manager is None:
        raise HTTPException(status_code=503, detail="Le gestionnaire de performance n'est pas initialisé")
        
    try:
        # Générer un rapport de performance complet
        report = await performance_manager.generate_performance_report(str(url_input.url))
        return report
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")

@app.post("/optimize", summary="Optimiser les performances d'une URL", response_model=Dict[str, Any])
async def optimize_performance(
    url_input: URLInput,
    settings: OptimizationSettings = Body(...)
):
    """Optimise les performances d'une URL spécifique avec des paramètres personnalisés"""
    if performance_manager is None:
        raise HTTPException(status_code=503, detail="Le gestionnaire de performance n'est pas initialisé")
        
    try:
        # Collecter les données de performance
        performance_data = await performance_manager.collect_performance_data(str(url_input.url))
        
        # Analyser les ressources
        resource_data = await performance_manager.analyze_resources(str(url_input.url))
        
        # Identifier les problèmes
        issues = performance_manager.identify_performance_issues(performance_data, resource_data)
        
        # Générer les suggestions d'optimisation
        suggestions = performance_manager.generate_optimization_suggestions(issues)
        
        # Filtrer les suggestions selon les paramètres
        filtered_suggestions = []
        for suggestion in suggestions:
            if not settings.minify_js_css and "minification" in suggestion["title"].lower():
                continue
            if not settings.optimize_images and "image" in suggestion["title"].lower():
                continue
            filtered_suggestions.append(suggestion)
        
        # Appliquer les optimisations si demandé
        optimization_results = {}
        if settings.apply_automatically:
            optimization_results = await performance_manager.apply_optimizations(
                str(url_input.url), filtered_suggestions)
        
        return {
            "url": str(url_input.url),
            "timestamp": datetime.now().isoformat(),
            "performance_data": performance_data,
            "issues_identified": issues,
            "optimization_suggestions": filtered_suggestions,
            "optimization_results": optimization_results if settings.apply_automatically else {"status": "not_applied"},
            "settings_used": settings.dict()
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'optimisation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'optimisation: {str(e)}")

@app.post("/monitor", summary="Configurer la surveillance des performances", response_model=Dict[str, Any])
async def setup_monitoring(
    settings: MonitoringSettings,
    background_tasks: BackgroundTasks
):
    """Configure la surveillance des performances pour une URL"""
    if performance_manager is None:
        raise HTTPException(status_code=503, detail="Le gestionnaire de performance n'est pas initialisé")
        
    try:
        # Fonction pour la surveillance en arrière-plan
        async def background_monitoring():
            try:
                await performance_manager.monitor_performance_over_time(
                    str(settings.url),
                    days=settings.days,
                    interval_hours=settings.interval_hours
                )
            except Exception as e:
                logger.error(f"Erreur dans la surveillance en arrière-plan: {str(e)}")
        
        # Ajouter la tâche en arrière-plan
        background_tasks.add_task(background_monitoring)
        
        return {
            "status": "monitoring_started",
            "url": str(settings.url),
            "interval_hours": settings.interval_hours,
            "days": settings.days,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la configuration de la surveillance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la configuration: {str(e)}")

@app.get("/trends/{url:path}", summary="Obtenir les tendances de performance", response_model=Dict[str, Any])
async def get_performance_trends(
    url: str = Path(..., description="URL encodée à analyser"),
    days: int = Query(7, description="Nombre de jours d'historique")
):
    """Récupère les tendances de performance pour une URL spécifique"""
    if performance_manager is None:
        raise HTTPException(status_code=503, detail="Le gestionnaire de performance n'est pas initialisé")
        
    try:
        # Récupérer les tendances
        decoded_url = url.replace("___", "/")  # Simple remplacement pour la compatibilité des URL
        trends = await performance_manager.monitor_performance_over_time(
            decoded_url,
            days=days,
            interval_hours=24  # Intervalle quotidien par défaut
        )
        return trends
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tendances: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des tendances: {str(e)}")

@app.post("/thresholds", summary="Mettre à jour les seuils de performance", response_model=Dict[str, Any])
async def update_thresholds(thresholds: PerformanceThresholds):
    """Met à jour les seuils de performance utilisés pour l'analyse"""
    if performance_manager is None:
        raise HTTPException(status_code=503, detail="Le gestionnaire de performance n'est pas initialisé")
        
    try:
        # Mettre à jour les seuils
        performance_manager.thresholds = thresholds.dict()
        
        return {
            "status": "thresholds_updated",
            "thresholds": performance_manager.thresholds,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des seuils: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

@app.post("/images/optimize", summary="Optimiser un lot d'images", response_model=Dict[str, Any])
async def optimize_images(input_data: ImageBatchOptimizationInput):
    """Optimise un lot d'images spécifiées par leurs URLs"""
    try:
        # Utiliser l'optimiseur d'images directement
        result = await ImageOptimizer.bulk_optimize_images(
            input_data.image_urls,
            target_format=input_data.target_format
        )
        return result
    except Exception as e:
        logger.error(f"Erreur lors de l'optimisation des images: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'optimisation: {str(e)}")

@app.post("/resources/minify/js", summary="Minifier du code JavaScript", response_model=Dict[str, Any])
async def minify_javascript(
    js_content: str = Body(..., description="Contenu JavaScript à minifier")
):
    """Minifie un contenu JavaScript fourni"""
    try:
        # Utiliser le minifieur directement
        result = await ResourceMinifier.minify_js(js_content)
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la minification JavaScript: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la minification: {str(e)}")

@app.post("/resources/minify/css", summary="Minifier du code CSS", response_model=Dict[str, Any])
async def minify_css(
    css_content: str = Body(..., description="Contenu CSS à minifier")
):
    """Minifie un contenu CSS fourni"""
    try:
        # Utiliser le minifieur directement
        result = await ResourceMinifier.minify_css(css_content)
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la minification CSS: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la minification: {str(e)}")

@app.post("/seo/analyze", summary="Analyser l'impact SEO des performances", response_model=Dict[str, Any])
async def analyze_seo_performance(url_input: URLInput):
    """Analyse l'impact des performances sur le référencement pour une URL spécifique"""
    if performance_manager is None:
        raise HTTPException(status_code=503, detail="Le gestionnaire de performance n'est pas initialisé")
        
    try:
        # Collecter les données de performance
        performance_data = await performance_manager.collect_performance_data(str(url_input.url))
        
        # Analyser l'impact SEO des Core Web Vitals
        seo_analysis = SEOPerformanceAnalyzer.analyze_core_web_vitals(performance_data)
        
        return {
            "url": str(url_input.url),
            "timestamp": datetime.now().isoformat(),
            "performance_data": performance_data,
            "seo_impact": seo_analysis,
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse SEO: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")

@app.get("/metrics/analyze", summary="Analyser la tendance d'une métrique", response_model=Dict[str, Any])
async def analyze_metric_trend(
    metric_values: str = Query(..., description="Valeurs de métrique séparées par des virgules")
):
    """Analyse la tendance d'une série de métriques fournies"""
    try:
        # Convertir la chaîne de caractères en liste de nombres
        try:
            metrics = [float(v.strip()) for v in metric_values.split(",") if v.strip()]
        except ValueError:
            raise HTTPException(status_code=400, detail="Les valeurs doivent être des nombres valides")
        
        if len(metrics) < 2:
            raise HTTPException(status_code=400, detail="Au moins deux valeurs de métrique sont nécessaires")
        
        # Analyser la tendance
        trend_analysis = PerformanceMetricsAnalyzer.analyze_trend(metrics)
        
        return {
            "metrics": metrics,
            "analysis": trend_analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        if not isinstance(e, HTTPException):
            logger.error(f"Erreur lors de l'analyse de tendance: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")
        raise e

@app.post("/integrations/shopify/update", summary="Mettre à jour les informations Shopify", response_model=Dict[str, Any])
async def update_shopify_info(
    shopify_api_key: str = Body(..., description="Clé API Shopify"),
    shopify_api_secret: str = Body(..., description="Secret API Shopify"),
    shopify_store_url: str = Body(..., description="URL du magasin Shopify")
):
    """Met à jour les informations d'authentification Shopify"""
    global performance_manager
    
    if performance_manager is None:
        raise HTTPException(status_code=503, detail="Le gestionnaire de performance n'est pas initialisé")
        
    try:
        # Mettre à jour les informations
        performance_manager.shopify_api_key = shopify_api_key
        performance_manager.shopify_api_secret = shopify_api_secret
        performance_manager.shopify_store_url = shopify_store_url
        
        return {
            "status": "shopify_info_updated",
            "store_url": shopify_store_url,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des informations Shopify: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
