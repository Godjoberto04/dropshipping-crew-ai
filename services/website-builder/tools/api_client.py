import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ApiClient:
    """
    Client pour interagir avec l'API du système
    """
    
    def __init__(self):
        """
        Initialise le client API
        """
        self.api_url = os.getenv("API_URL", "http://api:8000")
        logger.info(f"Client API initialisé avec l'URL: {self.api_url}")
    
    def get_pending_tasks(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Récupère les tâches en attente pour un agent donné
        
        Args:
            agent_id: ID de l'agent concerné
            
        Returns:
            Liste des tâches en attente
        """
        try:
            url = f"{self.api_url}/tasks/pending/{agent_id}"
            response = requests.get(url)
            response.raise_for_status()
            
            tasks = response.json()
            logger.info(f"Récupération de {len(tasks)} tâches en attente pour l'agent '{agent_id}'")
            return tasks
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des tâches en attente: {str(e)}")
            return []
    
    def update_task_status(self, task_id: str, status: str, progress: int = None, result: Dict[str, Any] = None) -> bool:
        """
        Met à jour le statut d'une tâche
        
        Args:
            task_id: ID de la tâche à mettre à jour
            status: Nouveau statut de la tâche ('pending', 'in_progress', 'completed', 'failed')
            progress: Pourcentage d'avancement (optionnel)
            result: Résultats de la tâche (optionnel)
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        try:
            url = f"{self.api_url}/tasks/{task_id}/status"
            
            data = {"status": status}
            if progress is not None:
                data["progress"] = progress
            if result is not None:
                data["result"] = result
            
            response = requests.put(url, json=data)
            response.raise_for_status()
            
            logger.info(f"Statut de la tâche {task_id} mis à jour: {status}, avancement: {progress}%")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut de la tâche {task_id}: {str(e)}")
            return False
    
    def update_agent_status(self, agent_id: str, status: str, details: Dict[str, Any] = None) -> bool:
        """
        Met à jour le statut d'un agent
        
        Args:
            agent_id: ID de l'agent à mettre à jour
            status: Nouveau statut de l'agent ('online', 'offline', 'error')
            details: Détails supplémentaires (optionnel)
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        try:
            url = f"{self.api_url}/agents/{agent_id}/status"
            
            data = {"status": status}
            if details is not None:
                data["details"] = details
            
            response = requests.put(url, json=data)
            response.raise_for_status()
            
            logger.info(f"Statut de l'agent {agent_id} mis à jour: {status}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut de l'agent {agent_id}: {str(e)}")
            return False
    
    def register_store_config(self, config: Dict[str, Any], store_url: str) -> bool:
        """
        Enregistre la configuration d'une boutique
        
        Args:
            config: Configuration de la boutique
            store_url: URL de la boutique Shopify
            
        Returns:
            True si l'enregistrement a réussi, False sinon
        """
        try:
            url = f"{self.api_url}/stores/config"
            
            data = {
                "config": config,
                "store_url": store_url,
                "timestamp": "auto"  # L'API générera automatiquement l'horodatage
            }
            
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            logger.info(f"Configuration de la boutique enregistrée pour {store_url}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la configuration de la boutique: {str(e)}")
            return False
    
    def register_product(self, product_data: Dict[str, Any], store_url: str) -> bool:
        """
        Enregistre un produit dans le système
        
        Args:
            product_data: Données du produit
            store_url: URL de la boutique Shopify
            
        Returns:
            True si l'enregistrement a réussi, False sinon
        """
        try:
            url = f"{self.api_url}/products"
            
            data = {
                "product": product_data,
                "store_url": store_url,
                "timestamp": "auto"  # L'API générera automatiquement l'horodatage
            }
            
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            logger.info(f"Produit enregistré: {product_data.get('title', 'Sans titre')}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du produit: {str(e)}")
            return False
    
    def get_analysis_results(self, limit: int = 1) -> List[Dict[str, Any]]:
        """
        Récupère les résultats d'analyse de l'agent Data Analyzer
        
        Args:
            limit: Nombre maximum de résultats à récupérer
            
        Returns:
            Liste des résultats d'analyse
        """
        try:
            url = f"{self.api_url}/analysis/results?limit={limit}"
            response = requests.get(url)
            response.raise_for_status()
            
            results = response.json()
            logger.info(f"Récupération de {len(results)} résultats d'analyse")
            return results
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des résultats d'analyse: {str(e)}")
            return []
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Récupère le statut d'une tâche
        
        Args:
            task_id: ID de la tâche
            
        Returns:
            Statut de la tâche
        """
        try:
            url = f"{self.api_url}/tasks/{task_id}"
            response = requests.get(url)
            response.raise_for_status()
            
            task_status = response.json()
            logger.info(f"Statut de la tâche {task_id} récupéré: {task_status.get('status')}")
            return task_status
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut de la tâche {task_id}: {str(e)}")
            return {}