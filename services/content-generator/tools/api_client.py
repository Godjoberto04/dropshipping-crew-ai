"""
Client pour l'API centrale du système Dropshipping Crew AI
"""

import asyncio
import json
import logging
import httpx
import time
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger("content_generator.api_client")

class ApiClient:
    """
    Client pour l'API centrale qui permet de communiquer avec les autres agents
    et de gérer les tâches de l'agent Content Generator.
    """
    
    def __init__(
        self, 
        base_url: str,
        agent_id: str,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialise le client API.
        
        Args:
            base_url: URL de base de l'API centrale
            agent_id: Identifiant de l'agent Content Generator
            timeout: Délai d'attente maximum en secondes pour les appels API
            max_retries: Nombre maximum de tentatives en cas d'erreur
        """
        self.base_url = base_url.rstrip('/')
        self.agent_id = agent_id
        self.timeout = timeout
        self.max_retries = max_retries
        
        logger.info(f"Client API initialisé (base_url: {base_url}, agent_id: {agent_id})")
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Méthode utilitaire pour effectuer des requêtes HTTP vers l'API centrale.
        
        Args:
            method: Méthode HTTP (GET, POST, PUT, etc.)
            endpoint: Point de terminaison de l'API
            data: Données à envoyer dans le corps de la requête
            params: Paramètres de requête URL
            
        Returns:
            La réponse de l'API sous forme de dictionnaire
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {"Content-Type": "application/json"}
        
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    if method == "GET":
                        response = await client.get(url, params=params, headers=headers)
                    elif method == "POST":
                        response = await client.post(url, json=data, params=params, headers=headers)
                    elif method == "PUT":
                        response = await client.put(url, json=data, params=params, headers=headers)
                    else:
                        raise ValueError(f"Méthode HTTP non supportée: {method}")
                    
                    # Vérification du code de statut
                    response.raise_for_status()
                    
                    # Convertir la réponse en JSON
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        logger.warning(f"Réponse non-JSON reçue: {response.text}")
                        return {"success": True, "data": response.text}
                    
            except httpx.HTTPStatusError as e:
                retry_count += 1
                wait_time = 2 ** retry_count  # Backoff exponentiel
                
                if retry_count >= self.max_retries:
                    logger.error(f"Échec de la requête après {self.max_retries} tentatives: {str(e)}")
                    raise
                
                logger.warning(f"Erreur HTTP {e.response.status_code}, nouvelle tentative dans {wait_time}s...")
                await asyncio.sleep(wait_time)
                
            except httpx.RequestError as e:
                retry_count += 1
                wait_time = 2 ** retry_count
                
                if retry_count >= self.max_retries:
                    logger.error(f"Échec de la connexion après {self.max_retries} tentatives: {str(e)}")
                    raise
                
                logger.warning(f"Erreur de connexion, nouvelle tentative dans {wait_time}s...")
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"Erreur inattendue: {str(e)}")
                raise
    
    async def register_agent(
        self,
        status: str = "online",
        version: Optional[str] = None,
        capabilities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Enregistre l'agent auprès de l'API centrale.
        
        Args:
            status: Statut de l'agent (online, offline, maintenance)
            version: Version de l'agent
            capabilities: Liste des capacités de l'agent
            
        Returns:
            Réponse de l'API
        """
        data = {
            "id": self.agent_id,
            "status": status,
            "version": version,
            "capabilities": capabilities or []
        }
        
        return await self._make_request("POST", "/agents/register", data=data)
    
    async def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """
        Récupère les tâches en attente pour l'agent.
        
        Returns:
            Liste des tâches en attente
        """
        params = {"agent_id": self.agent_id, "status": "pending"}
        response = await self._make_request("GET", "/tasks", params=params)
        
        return response.get("tasks", [])
    
    async def update_task_status(
        self,
        task_id: str,
        status: str,
        progress: Optional[int] = None,
        result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Met à jour le statut d'une tâche.
        
        Args:
            task_id: Identifiant de la tâche
            status: Nouveau statut (processing, completed, failed)
            progress: Pourcentage de progression (0-100)
            result: Résultat de la tâche
            
        Returns:
            Réponse de l'API
        """
        data = {
            "status": status
        }
        
        if progress is not None:
            data["progress"] = progress
            
        if result is not None:
            data["result"] = result
            
        return await self._make_request("PUT", f"/tasks/{task_id}", data=data)
    
    async def create_task(
        self,
        agent_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crée une nouvelle tâche pour un autre agent.
        
        Args:
            agent_id: Identifiant de l'agent qui doit exécuter la tâche
            params: Paramètres de la tâche
            
        Returns:
            Réponse de l'API incluant l'identifiant de la tâche créée
        """
        data = {
            "agent_id": agent_id,
            "params": params
        }
        
        return await self._make_request("POST", "/tasks", data=data)
    
    async def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        Récupère le résultat d'une tâche spécifique.
        
        Args:
            task_id: Identifiant de la tâche
            
        Returns:
            Résultat de la tâche
        """
        response = await self._make_request("GET", f"/tasks/{task_id}")
        return response
    
    async def wait_for_task_completion(
        self,
        task_id: str,
        polling_interval: float = 2.0,
        timeout: float = 300.0
    ) -> Dict[str, Any]:
        """
        Attend la fin d'une tâche avec un polling régulier.
        
        Args:
            task_id: Identifiant de la tâche
            polling_interval: Intervalle de vérification en secondes
            timeout: Délai maximum d'attente en secondes
            
        Returns:
            Résultat final de la tâche
            
        Raises:
            TimeoutError: Si la tâche n'est pas terminée dans le délai imparti
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            task_info = await self.get_task_result(task_id)
            
            if task_info.get("status") in ["completed", "failed"]:
                return task_info
            
            await asyncio.sleep(polling_interval)
        
        raise TimeoutError(f"Délai d'attente dépassé pour la tâche {task_id}")
