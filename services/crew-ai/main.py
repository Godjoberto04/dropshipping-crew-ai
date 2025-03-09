import os
import json
import time
import logging
import threading
import schedule
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from tools.scraping import SimpleScrapingTool, SimpleProductAnalysisTool
from tools.trend_analysis import SimpleTrendAnalysisTool
from tools.api_client import ApiClient

# Configuration du logging
os.makedirs('/app/logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/logs/data_analyzer.log')
    ]
)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Vérification de la clé API Claude
if not os.getenv("CLAUDE_API_KEY"):
    logger.error("La clé API Claude n'est pas définie. Veuillez configurer la variable d'environnement CLAUDE_API_KEY.")
    exit(1)

# Configuration de l'API key Claude
os.environ["ANTHROPIC_API_KEY"] = os.getenv("CLAUDE_API_KEY")

# Initialisation du client API
api_client = ApiClient()

# Création des outils
web_scraping_tool = SimpleScrapingTool()
product_analysis_tool = SimpleProductAnalysisTool()
trend_analysis_tool = SimpleTrendAnalysisTool()

# Fonction pour exécuter l'analyse de marché
def run_market_analysis(competitor_urls: List[str], market_segment: str = None, min_margin: float = 30.0, task_id: str = None):
    """
    Exécute une analyse de marché
    
    Args:
        competitor_urls: Liste des URLs de sites concurrents à analyser
        market_segment: Segment de marché à cibler (optionnel)
        min_margin: Marge minimale souhaitée en pourcentage (par défaut 30%)
        task_id: Identifiant de la tâche (pour le suivi via l'API)
        
    Returns:
        Résultats de l'analyse au format JSON
    """
    logger.info(f"Démarrage de l'analyse de marché sur {len(competitor_urls)} URLs...")
    
    # Mettre à jour le statut de la tâche si un task_id est fourni
    if task_id:
        api_client.update_task_status(
            task_id=task_id,
            status="in_progress",
            progress=10
        )
    
    try:
        # Exécution de l'analyse
        logger.info("Exécution de l'analyse...")
        start_time = time.time()
        
        # Mettre à jour le statut si task_id est fourni
        if task_id:
            api_client.update_task_status(
                task_id=task_id,
                status="in_progress",
                progress=30
            )
        
        # Étape 1: Scraping des sites web
        all_products = []
        for url in competitor_urls:
            products = web_scraping_tool.scrape_website(url)
            if products and not isinstance(products, dict) and not (isinstance(products, list) and products and "error" in products[0]):
                all_products.extend(products)
        
        if not all_products:
            raise Exception("Aucun produit trouvé sur les sites spécifiés")
        
        # Mettre à jour le statut si task_id est fourni
        if task_id:
            api_client.update_task_status(
                task_id=task_id,
                status="in_progress",
                progress=50
            )
        
        # Étape 2: Analyse des produits
        analysis_results = product_analysis_tool.analyze_products(
            all_products, 
            min_margin_percent=min_margin
        )
        
        # Mettre à jour le statut si task_id est fourni
        if task_id:
            api_client.update_task_status(
                task_id=task_id,
                status="in_progress",
                progress=70
            )
        
        # Étape 3: Analyse des tendances et de la concurrence
        if "products" in analysis_results:
            trends_results = trend_analysis_tool.analyze_trends(
                analysis_results["products"], 
                market_segment=market_segment
            )
            
            # Combiner les résultats
            top_products = trends_results.get("top_products", [])
        else:
            top_products = []
        
        execution_time = time.time() - start_time
        logger.info(f"Analyse terminée en {execution_time:.2f} secondes")
        
        # Construire les résultats finaux
        results_json = {
            "top_products": top_products,
            "analysis_metadata": {
                "execution_time_seconds": execution_time,
                "analyzed_urls_count": len(competitor_urls),
                "market_segment": market_segment,
                "min_margin_required": min_margin,
                "timestamp": time.time(),
                "task_id": task_id,
                "total_products_found": len(all_products),
                "profitable_products_found": analysis_results.get("profitable_count", 0)
            }
        }
        
        logger.info(f"Analyse réussie: {len(top_products)} produits identifiés")
        
        # Enregistrer les résultats via l'API si task_id est fourni
        if task_id:
            api_client.update_task_status(
                task_id=task_id,
                status="completed",
                progress=100,
                result=results_json
            )
            
            # Enregistrer également les résultats dans l'API
            api_client.register_analysis_results(
                results=results_json,
                urls=competitor_urls
            )
        
        return results_json
            
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'analyse: {str(e)}")
        error_result = {
            "error": f"Erreur lors de l'exécution de l'analyse: {str(e)}",
            "analysis_metadata": {
                "execution_time_seconds": time.time() - start_time,
                "analyzed_urls_count": len(competitor_urls),
                "market_segment": market_segment,
                "min_margin_required": min_margin,
                "timestamp": time.time(),
                "task_id": task_id
            }
        }
        
        # Mettre à jour le statut si task_id est fourni
        if task_id:
            api_client.update_task_status(
                task_id=task_id,
                status="failed",
                progress=100,
                result=error_result
            )
        
        return error_result


def check_pending_tasks():
    """
    Vérifie les tâches en attente via l'API et les exécute
    """
    logger.info("Vérification des tâches en attente...")
    
    try:
        # Récupérer les tâches en attente
        pending_tasks = api_client.get_pending_tasks("data-analyzer")
        
        if not pending_tasks:
            logger.info("Aucune tâche en attente")
            return
        
        logger.info(f"Nombre de tâches en attente: {len(pending_tasks)}")
        
        # Exécuter chaque tâche
        for task in pending_tasks:
            task_id = task.get("task_id")
            urls = task.get("params", {}).get("urls", [])
            market_segment = task.get("params", {}).get("market_segment")
            min_margin = task.get("params", {}).get("min_margin", 30.0)
            
            if not urls:
                logger.warning(f"Tâche {task_id} sans URLs, marquée comme échouée")
                api_client.update_task_status(
                    task_id=task_id,
                    status="failed",
                    result={"error": "Aucune URL spécifiée"}
                )
                continue
            
            logger.info(f"Exécution de la tâche {task_id}")
            
            # Lancer l'analyse dans un thread séparé
            threading.Thread(
                target=run_market_analysis,
                args=(urls, market_segment, min_margin, task_id)
            ).start()
    
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des tâches en attente: {str(e)}")


def run_scheduled_tasks():
    """
    Configure et exécute les tâches planifiées
    """
    logger.info("Démarrage du planificateur de tâches...")
    
    # Vérifier les tâches en attente toutes les 5 minutes
    schedule.every(5).minutes.do(check_pending_tasks)
    
    # Mettre à jour le statut de l'agent data-analyzer
    api_client.update_agent_status(
        agent_id="data-analyzer",
        status="online",
        details={
            "version": "1.0.0",
            "capabilities": [
                "Website scraping",
                "Product analysis",
                "Trend analysis",
                "Competition assessment"
            ]
        }
    )
    
    # Boucle principale du planificateur
    while True:
        schedule.run_pending()
        time.sleep(1)


# Fonction principale
if __name__ == "__main__":
    logger.info("Démarrage de l'agent Data Analyzer")
    
    # Exécuter le gestionnaire de tâches programmées dans un thread séparé
    scheduler_thread = threading.Thread(target=run_scheduled_tasks)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Pour les tests en ligne de commande, on peut aussi exécuter une analyse manuellement
    if os.getenv("RUN_TEST_ANALYSIS", "false").lower() == "true":
        logger.info("Exécution d'une analyse de test...")
        
        # URLs de test
        test_urls = [
            "https://example-shop.com/category/accessories",
            "https://another-shop.com/bestsellers"
        ]
        
        # Exécution de l'analyse
        analysis_results = run_market_analysis(
            test_urls, 
            market_segment="smartphone accessories",
            min_margin=30.0
        )
        
        # Affichage des résultats
        print(json.dumps(analysis_results, indent=2))
    
    # En mode normal, attendre que le thread du planificateur se termine (ne devrait jamais arriver)
    logger.info("Agent Data Analyzer en attente de tâches...")
    scheduler_thread.join()
