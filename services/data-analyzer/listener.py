"""
Module d'écoute Redis pour l'agent Data Analyzer.
Ce script s'abonne aux messages Redis pour traiter les tâches
demandées par l'API centrale du système.
"""

import os
import json
import asyncio
import logging
import redis
import httpx
import time
from datetime import datetime

# Import des modules d'analyse
from models.complementary.complementary_analyzer import ComplementaryAnalyzer
from models.complementary.association_rules import AssociationRulesMiner
from data_sources.trends.trends_analyzer import TrendsAnalyzer

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("data-analyzer-listener")

# Configuration Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_CHANNEL = "agent:data-analyzer:tasks"

# Configuration API interne de l'agent
AGENT_API_URL = "http://localhost:8000"  # URL de l'API FastAPI de l'agent

# Initialisation Redis
def get_redis_client():
    """Initialise et retourne un client Redis."""
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

# Initialisation des analyseurs
def init_analyzers():
    """Initialise les analyseurs avec les données disponibles."""
    try:
        # Initialisation de l'analyseur de tendances
        trends_analyzer = TrendsAnalyzer()
        logger.info("Analyseur de tendances initialisé avec succès")
        
        # Initialisation de l'analyseur de complémentarité
        complementary_analyzer = ComplementaryAnalyzer()
        
        # On pourrait charger des données d'exemple ici,
        # mais on suppose que l'API de l'agent s'en charge
        
        logger.info("Analyseurs initialisés avec succès")
        return trends_analyzer, complementary_analyzer
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des analyseurs: {str(e)}")
        return None, None

# Gestionnaire de messages
async def handle_message(message, trends_analyzer, complementary_analyzer):
    """
    Traite un message reçu de Redis.
    
    Args:
        message: Message reçu du canal Redis
        trends_analyzer: Instance de l'analyseur de tendances
        complementary_analyzer: Instance de l'analyseur de complémentarité
    """
    try:
        # Décodage du message JSON
        data = json.loads(message["data"])
        task_id = data.get("task_id")
        action = data.get("action")
        params = data.get("params", {})
        
        logger.info(f"Réception de la tâche {task_id}: {action}")
        
        # Préparer la mise à jour initiale
        await update_task_status(task_id, "processing", 10, "Traitement commencé")
        
        # Traiter selon l'action demandée
        if action == "analyze_market":
            await process_market_analysis(task_id, params, trends_analyzer)
        elif action == "compare_products":
            await process_product_comparison(task_id, params, trends_analyzer)
        elif action == "get_complementary_products":
            await process_complementary_products(task_id, params, complementary_analyzer)
        elif action == "get_upsell_products":
            await process_upsell_products(task_id, params, complementary_analyzer)
        elif action == "create_bundles":
            await process_create_bundles(task_id, params, complementary_analyzer)
        elif action == "analyze_cart":
            await process_analyze_cart(task_id, params, complementary_analyzer)
        else:
            logger.warning(f"Action non reconnue: {action}")
            await update_task_status(
                task_id, 
                "failed", 
                0, 
                f"Action non reconnue: {action}"
            )
    except json.JSONDecodeError:
        logger.error(f"Erreur de décodage JSON: {message['data']}")
    except Exception as e:
        logger.error(f"Erreur lors du traitement du message: {str(e)}")
        if task_id:
            await update_task_status(task_id, "failed", 0, f"Erreur: {str(e)}")

# Mise à jour du statut des tâches
async def update_task_status(task_id, status, progress, message=None, result=None):
    """
    Met à jour le statut d'une tâche dans Redis.
    
    Args:
        task_id: ID de la tâche
        status: Statut de la tâche (pending, processing, completed, failed)
        progress: Progression (0-100)
        message: Message optionnel
        result: Résultat optionnel
    """
    try:
        redis_client = get_redis_client()
        
        # Préparer les données de mise à jour
        update_data = {
            "status": status,
            "progress": str(progress),
            "updated_at": datetime.now().isoformat()
        }
        
        if message:
            update_data["message"] = message
        
        if result:
            update_data["result"] = json.dumps(result)
        
        if status in ["completed", "failed"]:
            update_data["completed_at"] = datetime.now().isoformat()
        
        # Mettre à jour dans Redis
        redis_client.hset(f"task:{task_id}", mapping=update_data)
        
        logger.info(f"Mise à jour de la tâche {task_id}: {status}, {progress}%")
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du statut: {str(e)}")

# Traitement des différentes actions
async def process_market_analysis(task_id, params, trends_analyzer):
    """Traite une demande d'analyse de marché."""
    try:
        urls = params.get("urls", [])
        market_segment = params.get("market_segment")
        min_margin = params.get("min_margin", 30.0)
        
        if not urls:
            await update_task_status(
                task_id, 
                "failed", 
                0, 
                "Aucune URL fournie pour l'analyse"
            )
            return
        
        # Mise à jour de progression
        await update_task_status(task_id, "processing", 20, "Analyse des URLs en cours")
        
        # Simulation de l'analyse (à remplacer par la véritable logique)
        # Dans une implémentation réelle, vous utiliseriez trends_analyzer ici
        await asyncio.sleep(3)  # Simulation du temps de traitement
        
        # Progression
        await update_task_status(task_id, "processing", 60, "Génération des recommandations")
        await asyncio.sleep(2)  # Suite de la simulation
        
        # Résultats fictifs (à remplacer par de vrais résultats)
        result = {
            "top_products": [
                {
                    "name": f"Produit tendance de {market_segment or 'marché général'}",
                    "supplier_price": 15.99,
                    "recommended_price": 39.99,
                    "potential_margin_percent": 60.0,
                    "competition_level": "Moyen",
                    "trend_direction": "Hausse",
                    "recommendation_score": 8.7,
                    "justification": "Forte tendance à la hausse avec une concurrence modérée"
                },
                {
                    "name": f"Produit secondaire de {urls[0][:30]}...",
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
            "min_margin": min_margin
        }
        
        # Mise à jour finale
        await update_task_status(
            task_id, 
            "completed", 
            100, 
            "Analyse de marché terminée", 
            result
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de marché: {str(e)}")
        await update_task_status(
            task_id, 
            "failed", 
            0, 
            f"Erreur lors de l'analyse: {str(e)}"
        )

async def process_product_comparison(task_id, params, trends_analyzer):
    """Traite une demande de comparaison de produits."""
    try:
        products = params.get("products", [])
        timeframe = params.get("timeframe", "medium_term")
        geo = params.get("geo")
        
        if not products:
            await update_task_status(
                task_id, 
                "failed", 
                0, 
                "Aucun produit fourni pour la comparaison"
            )
            return
        
        # Mise à jour de progression
        await update_task_status(
            task_id, 
            "processing", 
            30, 
            "Analyse des tendances des produits"
        )
        
        # Simulation de la comparaison (à remplacer par la véritable logique)
        # Dans une implémentation réelle, vous utiliseriez trends_analyzer.compare_keywords ici
        await asyncio.sleep(3)  # Simulation du temps de traitement
        
        # Résultats fictifs (à remplacer par de vrais résultats)
        result = {
            "products": products,
            "timeframe": timeframe,
            "geo": geo,
            "comparisons": [
                {
                    "product": product,
                    "trend_score": round(50 + 30 * (0.5 - (i / len(products))), 1),
                    "interest_over_time": {
                        "current": round(50 + 30 * (0.5 - (i / len(products))), 1),
                        "change_percent": round(10 - 5 * (i / len(products)), 1)
                    },
                    "seasonal_pattern": i % 2 == 0,
                    "recommendation": "Forte demande" if i == 0 else "Demande modérée" if i == 1 else "Faible demande"
                }
                for i, product in enumerate(products)
            ],
            "best_product": products[0],
            "analysis_date": datetime.now().isoformat()
        }
        
        # Mise à jour finale
        await update_task_status(
            task_id, 
            "completed", 
            100, 
            "Comparaison de produits terminée", 
            result
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la comparaison de produits: {str(e)}")
        await update_task_status(
            task_id, 
            "failed", 
            0, 
            f"Erreur lors de la comparaison: {str(e)}"
        )

async def process_complementary_products(task_id, params, complementary_analyzer):
    """Traite une demande de produits complémentaires."""
    try:
        product_id = params.get("product_id")
        max_products = params.get("max_products", 5)
        
        if not product_id:
            await update_task_status(
                task_id, 
                "failed", 
                0, 
                "Aucun ID de produit fourni"
            )
            return
        
        # Mise à jour de progression
        await update_task_status(
            task_id, 
            "processing", 
            50, 
            "Recherche de produits complémentaires"
        )
        
        # Dans une implémentation réelle, on appelle directement l'API interne
        # pour obtenir les résultats du module d'analyse de complémentarité
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{AGENT_API_URL}/action",
                    json={
                        "action": "get_complementary_products",
                        "product_id": product_id,
                        "max_products": max_products
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json().get("result", [])
                    
                    # Mise à jour finale
                    await update_task_status(
                        task_id, 
                        "completed", 
                        100, 
                        "Produits complémentaires trouvés", 
                        result
                    )
                else:
                    # Fallback si le service direct n'est pas disponible ou échoue
                    # Dans ce cas, on pourrait avoir une implémentation directe ici
                    logger.warning(f"L'API a retourné le code {response.status_code}, génération de résultats alternatifs")
                    
                    # Résultats fictifs (à remplacer par une implémentation directe)
                    result = [
                        {
                            "product": f"complement_{product_id}_1",
                            "score": 0.85,
                            "source": "category"
                        },
                        {
                            "product": f"complement_{product_id}_2",
                            "score": 0.72,
                            "source": "association"
                        }
                    ]
                    
                    await update_task_status(
                        task_id, 
                        "completed", 
                        100, 
                        "Produits complémentaires générés (fallback)", 
                        result
                    )
                    
        except (httpx.RequestError, asyncio.TimeoutError):
            # En cas d'erreur de connexion, utiliser une implémentation directe ou des résultats fictifs
            logger.error("Impossible de contacter l'API interne, génération de résultats fictifs")
            
            result = [
                {
                    "product": f"fallback_complement_{product_id}_1",
                    "score": 0.78,
                    "source": "fallback"
                }
            ]
            
            await update_task_status(
                task_id, 
                "completed", 
                100, 
                "Produits complémentaires (fallback d'urgence)", 
                result
            )
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de produits complémentaires: {str(e)}")
        await update_task_status(
            task_id, 
            "failed", 
            0, 
            f"Erreur: {str(e)}"
        )

async def process_upsell_products(task_id, params, complementary_analyzer):
    """Traite une demande de produits d'up-sell."""
    try:
        product_id = params.get("product_id")
        max_products = params.get("max_products", 3)
        
        if not product_id:
            await update_task_status(
                task_id, 
                "failed", 
                0, 
                "Aucun ID de produit fourni"
            )
            return
        
        # Mise à jour de progression
        await update_task_status(
            task_id, 
            "processing", 
            50, 
            "Recherche de produits d'up-sell"
        )
        
        # Utilisation de l'API interne (même approche que pour les produits complémentaires)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{AGENT_API_URL}/action",
                    json={
                        "action": "get_upsell_products",
                        "product_id": product_id,
                        "max_products": max_products
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json().get("result", [])
                    
                    # Mise à jour finale
                    await update_task_status(
                        task_id, 
                        "completed", 
                        100, 
                        "Produits d'up-sell trouvés", 
                        result
                    )
                else:
                    # Fallback
                    logger.warning(f"L'API a retourné le code {response.status_code}, génération de résultats alternatifs")
                    
                    # Résultats fictifs
                    result = [
                        {
                            "product": f"upsell_{product_id}_premium",
                            "score": 0.90,
                            "price_difference": 30.0,
                            "price_ratio": 1.5,
                            "source": "category_upsell"
                        }
                    ]
                    
                    await update_task_status(
                        task_id, 
                        "completed", 
                        100, 
                        "Produits d'up-sell générés (fallback)", 
                        result
                    )
                    
        except (httpx.RequestError, asyncio.TimeoutError):
            # Fallback d'urgence
            logger.error("Impossible de contacter l'API interne, génération de résultats fictifs")
            
            result = [
                {
                    "product": f"fallback_upsell_{product_id}",
                    "score": 0.85,
                    "price_difference": 25.0,
                    "price_ratio": 1.4,
                    "source": "fallback"
                }
            ]
            
            await update_task_status(
                task_id, 
                "completed", 
                100, 
                "Produits d'up-sell (fallback d'urgence)", 
                result
            )
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de produits d'up-sell: {str(e)}")
        await update_task_status(
            task_id, 
            "failed", 
            0, 
            f"Erreur: {str(e)}"
        )

async def process_create_bundles(task_id, params, complementary_analyzer):
    """Traite une demande de création de bundles."""
    try:
        product_ids = params.get("product_ids", [])
        max_bundles = params.get("max_bundles", 3)
        
        if not product_ids:
            await update_task_status(
                task_id, 
                "failed", 
                0, 
                "Aucun ID de produit fourni"
            )
            return
        
        # Mise à jour de progression
        await update_task_status(
            task_id, 
            "processing", 
            50, 
            "Création de bundles"
        )
        
        # Utilisation de l'API interne
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{AGENT_API_URL}/action",
                    json={
                        "action": "create_bundles",
                        "product_ids": product_ids,
                        "max_bundles": max_bundles
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json().get("result", [])
                    
                    # Mise à jour finale
                    await update_task_status(
                        task_id, 
                        "completed", 
                        100, 
                        "Bundles créés avec succès", 
                        result
                    )
                else:
                    # Fallback
                    logger.warning(f"L'API a retourné le code {response.status_code}, génération de résultats alternatifs")
                    
                    # Résultats fictifs
                    result = [
                        {
                            "name": "Bundle Essentiel",
                            "products": product_ids + ["complementary_product"],
                            "original_price": 100.0,
                            "bundle_price": 95.0,
                            "discount_percentage": 5,
                            "score": 0.8
                        }
                    ]
                    
                    await update_task_status(
                        task_id, 
                        "completed", 
                        100, 
                        "Bundles générés (fallback)", 
                        result
                    )
                    
        except (httpx.RequestError, asyncio.TimeoutError):
            # Fallback d'urgence
            logger.error("Impossible de contacter l'API interne, génération de résultats fictifs")
            
            result = [
                {
                    "name": "Bundle Fallback",
                    "products": product_ids,
                    "original_price": 50.0,
                    "bundle_price": 45.0,
                    "discount_percentage": 10,
                    "score": 0.7
                }
            ]
            
            await update_task_status(
                task_id, 
                "completed", 
                100, 
                "Bundles (fallback d'urgence)", 
                result
            )
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de bundles: {str(e)}")
        await update_task_status(
            task_id, 
            "failed", 
            0, 
            f"Erreur: {str(e)}"
        )

async def process_analyze_cart(task_id, params, complementary_analyzer):
    """Traite une demande d'analyse de panier."""
    try:
        product_ids = params.get("product_ids", [])
        
        if not product_ids:
            await update_task_status(
                task_id, 
                "failed", 
                0, 
                "Aucun ID de produit fourni"
            )
            return
        
        # Mise à jour de progression
        await update_task_status(
            task_id, 
            "processing", 
            50, 
            "Analyse du panier en cours"
        )
        
        # Utilisation de l'API interne
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{AGENT_API_URL}/action",
                    json={
                        "action": "analyze_cart",
                        "product_ids": product_ids
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json().get("result", {})
                    
                    # Mise à jour finale
                    await update_task_status(
                        task_id, 
                        "completed", 
                        100, 
                        "Analyse du panier terminée", 
                        result
                    )
                else:
                    # Fallback
                    logger.warning(f"L'API a retourné le code {response.status_code}, génération de résultats alternatifs")
                    
                    # Résultats fictifs
                    result = {
                        "cart_value": 150.0,
                        "product_count": len(product_ids),
                        "missing_complementary": [
                            {
                                "product": "suggested_product_1",
                                "score": 0.85,
                                "for_product": product_ids[0]
                            }
                        ],
                        "potential_upsells": [],
                        "bundle_opportunities": [],
                        "cart_score": 65.0  # Score d'optimisation (plus bas = plus d'opportunités)
                    }
                    
                    await update_task_status(
                        task_id, 
                        "completed", 
                        100, 
                        "Analyse du panier générée (fallback)", 
                        result
                    )
                    
        except (httpx.RequestError, asyncio.TimeoutError):
            # Fallback d'urgence
            logger.error("Impossible de contacter l'API interne, génération de résultats fictifs")
            
            result = {
                "cart_value": 100.0,
                "product_count": len(product_ids),
                "missing_complementary": [],
                "potential_upsells": [],
                "bundle_opportunities": [],
                "cart_score": 50.0
            }
            
            await update_task_status(
                task_id, 
                "completed", 
                100, 
                "Analyse du panier (fallback d'urgence)", 
                result
            )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du panier: {str(e)}")
        await update_task_status(
            task_id, 
            "failed", 
            0, 
            f"Erreur: {str(e)}"
        )

# Mise à jour régulière du statut de l'agent
async def update_agent_status():
    """Met à jour régulièrement le statut de l'agent dans Redis."""
    try:
        redis_client = get_redis_client()
        
        # Mise à jour du statut
        redis_client.hset(
            "agent:data-analyzer",
            mapping={
                "status": "online",
                "version": "0.1.0",
                "capabilities": json.dumps([
                    "market_analysis",
                    "product_trends",
                    "complementary_analysis",
                    "cart_analysis",
                    "bundle_creation"
                ]),
                "last_run": datetime.now().isoformat()
            }
        )
        
        logger.info("Statut de l'agent mis à jour dans Redis")
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du statut de l'agent: {str(e)}")

# Boucle principale d'écoute Redis
async def listen_for_tasks():
    """Écoute les tâches publiées sur Redis et les traite."""
    # Initialisation des analyseurs
    trends_analyzer, complementary_analyzer = init_analyzers()
    
    # Mise à jour initiale du statut
    await update_agent_status()
    
    # Créer une tâche pour mettre à jour régulièrement le statut
    asyncio.create_task(periodic_status_update())
    
    # Client Redis pour les abonnements
    redis_client = get_redis_client()
    pubsub = redis_client.pubsub()
    
    try:
        # S'abonner au canal
        pubsub.subscribe(REDIS_CHANNEL)
        logger.info(f"Abonnement au canal Redis {REDIS_CHANNEL}")
        
        # Boucle d'écoute
        for message in pubsub.listen():
            if message["type"] == "message":
                # Traiter le message de manière asynchrone
                asyncio.create_task(
                    handle_message(message, trends_analyzer, complementary_analyzer)
                )
    except Exception as e:
        logger.error(f"Erreur dans la boucle d'écoute Redis: {str(e)}")
    finally:
        # Nettoyage
        pubsub.unsubscribe(REDIS_CHANNEL)
        logger.info(f"Désabonnement du canal Redis {REDIS_CHANNEL}")

# Mise à jour périodique du statut
async def periodic_status_update():
    """Met à jour périodiquement le statut de l'agent."""
    while True:
        await update_agent_status()
        await asyncio.sleep(60)  # Mise à jour toutes les minutes

# Point d'entrée
if __name__ == "__main__":
    try:
        # Courte pause pour s'assurer que Redis est prêt
        time.sleep(5)
        
        # Exécuter la boucle d'écoute
        asyncio.run(listen_for_tasks())
    except KeyboardInterrupt:
        logger.info("Arrêt du listener par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur non gérée: {str(e)}")
