import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain.tools import BaseTool

logger = logging.getLogger(__name__)

class ApiClient:
    """Client pour communiquer avec l'API FastAPI"""
    
    def __init__(self, api_url: str = None):
        """
        Initialise le client API
        
        Args:
            api_url: URL de base de l'API (format: http://hostname:port)
        """
        self.api_url = api_url or os.getenv("API_URL", "http://api:8000")
        logger.info(f"Client API initialisé avec URL: {self.api_url}")
        
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Gère la réponse de l'API et gère les erreurs
        
        Args:
            response: Objet Response de requests
            
        Returns:
            Données de la réponse en format dict
            
        Raises:
            Exception: Si la requête échoue
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_message = f"Erreur HTTP: {str(e)}"
            try:
                error_detail = response.json()
                error_message += f" - Détails: {json.dumps(error_detail)}"
            except:
                pass
            
            logger.error(error_message)
            raise Exception(error_message)
        except Exception as e:
            logger.error(f"Erreur lors de la communication avec l'API: {str(e)}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """
        Récupère le statut général du système
        
        Returns:
            Statut du système
        """
        url = f"{self.api_url}/status"
        logger.debug(f"GET {url}")
        
        try:
            response = requests.get(url, timeout=10)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut: {str(e)}")
            return {"error": str(e)}
    
    def register_analysis_results(self, results: Dict[str, Any], urls: List[str]) -> Dict[str, Any]:
        """
        Enregistre les résultats d'une analyse dans l'API
        
        Args:
            results: Résultats de l'analyse
            urls: Liste des URLs analysées
            
        Returns:
            Réponse de l'API
        """
        url = f"{self.api_url}/analysis/results"
        logger.debug(f"POST {url}")
        
        # Préparer les données à envoyer
        payload = {
            "results": results,
            "source_urls": urls,
            "created_at": datetime.now().isoformat(),
            "agent_id": "data-analyzer"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des résultats: {str(e)}")
            return {"error": str(e)}
    
    def update_agent_status(self, agent_id: str, status: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Met à jour le statut d'un agent dans l'API
        
        Args:
            agent_id: Identifiant de l'agent
            status: Statut (online, offline, partial)
            details: Détails supplémentaires (optionnel)
            
        Returns:
            Réponse de l'API
        """
        url = f"{self.api_url}/agents/{agent_id}/status"
        logger.debug(f"PUT {url}")
        
        # Préparer les données à envoyer
        payload = {
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
        
        if details:
            payload.update(details)
        
        try:
            response = requests.put(url, json=payload, timeout=10)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut: {str(e)}")
            return {"error": str(e)}
            
    def get_pending_tasks(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Récupère les tâches en attente pour un agent
        
        Args:
            agent_id: Identifiant de l'agent
            
        Returns:
            Liste des tâches en attente
        """
        url = f"{self.api_url}/tasks?agent_id={agent_id}&status=pending"
        logger.debug(f"GET {url}")
        
        try:
            response = requests.get(url, timeout=10)
            result = self._handle_response(response)
            return result.get("tasks", [])
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des tâches: {str(e)}")
            return []
    
    def update_task_status(self, task_id: str, status: str, progress: int = None, 
                          result: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Met à jour le statut d'une tâche
        
        Args:
            task_id: Identifiant de la tâche
            status: Statut (pending, in_progress, completed, failed)
            progress: Pourcentage de progression (0-100)
            result: Résultat de la tâche (si terminée)
            
        Returns:
            Réponse de l'API
        """
        url = f"{self.api_url}/tasks/{task_id}"
        logger.debug(f"PUT {url}")
        
        # Préparer les données à envoyer
        payload = {
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
        
        if progress is not None:
            payload["progress"] = progress
            
        if result:
            payload["result"] = result
        
        try:
            response = requests.put(url, json=payload, timeout=15)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la tâche: {str(e)}")
            return {"error": str(e)}
