import os
import json
import time
import logging
import threading
import schedule
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from tools.shopify_api import ShopifyClient
from tools.theme_manager import ThemeManager
from tools.store_setup import StoreSetup
from tools.navigation import NavigationManager
from tools.api_client import ApiClient

# Configuration du logging
os.makedirs('/app/logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/logs/website_builder.log')
    ]
)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Vérification des variables d'environnement requises
required_env_vars = [
    "CLAUDE_API_KEY",
    "SHOPIFY_API_KEY",
    "SHOPIFY_API_SECRET",
    "SHOPIFY_STORE_URL",
    "SHOPIFY_ACCESS_TOKEN"
]

for var in required_env_vars:
    if not os.getenv(var):
        logger.error(f"La variable d'environnement {var} n'est pas définie.")
        exit(1)

# Configuration de l'API key Claude
os.environ["ANTHROPIC_API_KEY"] = os.getenv("CLAUDE_API_KEY")

# Initialisation du client API
api_client = ApiClient()

# Initialisation des outils Shopify
shopify_client = ShopifyClient()
theme_manager = ThemeManager(shopify_client)
store_setup = StoreSetup(shopify_client)
navigation_manager = NavigationManager(shopify_client)

# Fonction pour configurer une nouvelle boutique
def setup_new_store(store_config: Dict[str, Any], task_id: str = None) -> Dict[str, Any]:
    """
    Configure une nouvelle boutique Shopify avec les paramètres spécifiés
    
    Args:
        store_config: Configuration de la boutique (nom, devise, etc.)
        task_id: Identifiant de la tâche (pour le suivi via l'API)
        
    Returns:
        Résultats de la configuration au format JSON
    """
    logger.info(f"Démarrage de la configuration d'une nouvelle boutique: {store_config.get('name', 'Unnamed')}")
    
    # Mettre à jour le statut de la tâche si un task_id est fourni
    if task_id:
        api_client.update_task_status(
            task_id=task_id,
            status="in_progress",
            progress=10
        )
    
    try:
        # Exécution de la configuration
        logger.info("Configuration de la boutique...")
        start_time = time.time()
        
        # Étape 1: Configuration des paramètres de base
        basic_config_result = store_setup.configure_basic_settings(store_config)
        
        # Mettre à jour le statut si task_id est fourni
        if task_id:
            api_client.update_task_status(
                task_id=task_id,
                status="in_progress",
                progress=30
            )
        
        # Étape 2: Configuration du thème
        theme_config = store_config.get('theme', {})
        theme_result = theme_manager.configure_theme(theme_config)
        
        # Mettre à jour le statut si task_id est fourni
        if task_id:
            api_client.update_task_status(
                task_id=task_id,
                status="in_progress",
                progress=60
            )
        
        # Étape 3: Configuration de la navigation
        navigation_config = store_config.get('navigation', {})
        navigation_result = navigation_manager.configure_navigation(navigation_config)
        
        execution_time = time.time() - start_time
        logger.info(f"Configuration terminée en {execution_time:.2f} secondes")
        
        # Construire les résultats finaux
        results_json = {
            "store_url": shopify_client.get_store_url(),
            "setup_details": {
                "basic_config": basic_config_result,
                "theme": theme_result,
                "navigation": navigation_result
            },
            "setup_metadata": {
                "execution_time_seconds": execution_time,
                "timestamp": time.time(),
                "task_id": task_id
            }
        }
        
        logger.info(f"Configuration réussie de la boutique: {store_config.get('name', 'Unnamed')}")
        
        # Enregistrer les résultats via l'API si task_id est fourni
        if task_id:
            api_client.update_task_status(
                task_id=task_id,
                status="completed",
                progress=100,
                result=results_json
            )
        
        return results_json
            
    except Exception as e:
        logger.error(f"Erreur lors de la configuration de la boutique: {str(e)}")
        error_result = {
            "error": f"Erreur lors de la configuration de la boutique: {str(e)}",
            "setup_metadata": {
                "execution_time_seconds": time.time() - start_time,
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

# Fonction pour ajouter un produit à la boutique
def add_product(product_data: Dict[str, Any], task_id: str = None) -> Dict[str, Any]:
    """
    Ajoute un nouveau produit à la boutique Shopify
    
    Args:
        product_data: Données du produit à ajouter
        task_id: Identifiant de la tâche (pour le suivi via l'API)
        
    Returns:
        Résultats de l'ajout au format JSON
    """
    logger.info(f"Ajout d'un nouveau produit: {product_data.get('title', 'Unnamed')}")
    
    # Mettre à jour le statut de la tâche si un task_id est fourni
    if task_id:
        api_client.update_task_status(
            task_id=task_id,
            status="in_progress",
            progress=10
        )
    
    try:
        # Exécution de l'ajout du produit
        logger.info("Ajout du produit...")
        start_time = time.time()
        
        # Ajout du produit via l'API Shopify
        product_result = shopify_client.create_product(product_data)
        
        execution_time = time.time() - start_time
        logger.info(f"Ajout terminé en {execution_time:.2f} secondes")
        
        # Construire les résultats finaux
        results_json = {
            "product": product_result,
            "product_metadata": {
                "execution_time_seconds": execution_time,
                "timestamp": time.time(),
                "task_id": task_id
            }
        }
        
        logger.info(f"Ajout réussi du produit: {product_data.get('title', 'Unnamed')}")
        
        # Enregistrer les résultats via l'API si task_id est fourni
        if task_id:
            api_client.update_task_status(
                task_id=task_id,
                status="completed",
                progress=100,
                result=results_json
            )
        
        return results_json
            
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout du produit: {str(e)}")
        error_result = {
            "error": f"Erreur lors de l'ajout du produit: {str(e)}",
            "product_metadata": {
                "execution_time_seconds": time.time() - start_time,
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
        pending_tasks = api_client.get_pending_tasks("website-builder")
        
        if not pending_tasks:
            logger.info("Aucune tâche en attente")
            return
        
        logger.info(f"Nombre de tâches en attente: {len(pending_tasks)}")
        
        # Exécuter chaque tâche
        for task in pending_tasks:
            task_id = task.get("task_id")
            action = task.get("params", {}).get("action")
            
            if action == "setup_store":
                store_config = task.get("params", {}).get("store_config", {})
                
                if not store_config:
                    logger.warning(f"Tâche {task_id} sans configuration de boutique, marquée comme échouée")
                    api_client.update_task_status(
                        task_id=task_id,
                        status="failed",
                        result={"error": "Aucune configuration de boutique spécifiée"}
                    )
                    continue
                
                logger.info(f"Exécution de la tâche de configuration de boutique {task_id}")
                
                # Lancer la configuration dans un thread séparé
                threading.Thread(
                    target=setup_new_store,
                    args=(store_config, task_id)
                ).start()
                
            elif action == "add_product":
                product_data = task.get("params", {}).get("product_data", {})
                
                if not product_data:
                    logger.warning(f"Tâche {task_id} sans données de produit, marquée comme échouée")
                    api_client.update_task_status(
                        task_id=task_id,
                        status="failed",
                        result={"error": "Aucune donnée de produit spécifiée"}
                    )
                    continue
                
                logger.info(f"Exécution de la tâche d'ajout de produit {task_id}")
                
                # Lancer l'ajout de produit dans un thread séparé
                threading.Thread(
                    target=add_product,
                    args=(product_data, task_id)
                ).start()
                
            else:
                logger.warning(f"Tâche {task_id} avec action inconnue '{action}', marquée comme échouée")
                api_client.update_task_status(
                    task_id=task_id,
                    status="failed",
                    result={"error": f"Action inconnue: {action}"}
                )
    
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des tâches en attente: {str(e)}")

def run_scheduled_tasks():
    """
    Configure et exécute les tâches planifiées
    """
    logger.info("Démarrage du planificateur de tâches...")
    
    # Vérifier les tâches en attente toutes les 5 minutes
    schedule.every(5).minutes.do(check_pending_tasks)
    
    # Mettre à jour le statut de l'agent website-builder
    api_client.update_agent_status(
        agent_id="website-builder",
        status="online",
        details={
            "version": "1.0.0",
            "capabilities": [
                "Store configuration",
                "Theme management",
                "Navigation setup",
                "Product management"
            ]
        }
    )
    
    # Boucle principale du planificateur
    while True:
        schedule.run_pending()
        time.sleep(1)

# Fonction principale
if __name__ == "__main__":
    logger.info("Démarrage de l'agent Website Builder")
    
    # Exécuter le gestionnaire de tâches programmées dans un thread séparé
    scheduler_thread = threading.Thread(target=run_scheduled_tasks)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Pour les tests en ligne de commande, on peut aussi exécuter une configuration manuellement
    if os.getenv("RUN_TEST_SETUP", "false").lower() == "true":
        logger.info("Exécution d'une configuration de test...")
        
        # Configuration de test
        test_config = {
            "name": "Test Dropshipping Store",
            "currency": "EUR",
            "language": "fr",
            "theme": {
                "name": "Dawn",
                "colors": {
                    "primary": "#3b82f6",
                    "secondary": "#10b981",
                    "background": "#ffffff"
                }
            },
            "navigation": {
                "main_menu": [
                    {"title": "Accueil", "url": "/"},
                    {"title": "Produits", "url": "/collections/all"},
                    {"title": "À propos", "url": "/pages/about"},
                    {"title": "Contact", "url": "/pages/contact"}
                ]
            }
        }
        
        # Exécution de la configuration
        setup_results = setup_new_store(test_config)
        
        # Affichage des résultats
        print(json.dumps(setup_results, indent=2))
    
    # En mode normal, attendre que le thread du planificateur se termine (ne devrait jamais arriver)
    logger.info("Agent Website Builder en attente de tâches...")
    scheduler_thread.join()
