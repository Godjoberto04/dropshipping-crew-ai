#!/usr/bin/env python3
"""
Client API pour interagir avec l'API centrale.
"""

import aiohttp
import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Union

from config import settings, get_logger

logger = get_logger("api_client")

class ApiClient:
    """Client pour interagir avec l'API centrale du système."""
    
    def __init__(self, base_url: str, agent_id: str):
        """
        Initialise le client API.
        
        Args:
            base_url: URL de base de l'API
            agent_id: Identifiant de l'agent utilisant ce client
        """
        self.base_url = base_url.rstrip("/")
        self.agent_id = agent_id
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Création de la session
        self._create_session()
    
    def _create_session(self):
        """Crée une nouvelle session HTTP."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=settings.API_TIMEOUT)
            )
    
    async def close(self):
        """Ferme la session HTTP."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def register_agent(self, status: str = "online", version: str = "0.1.0", 
                            capabilities: List[str] = None) -> Dict[str, Any]:
        """
        Enregistre l'agent auprès de l'API centrale.
        
        Args:
            status: Statut initial de l'agent
            version: Version de l'agent
            capabilities: Liste des capacités de l'agent
            
        Returns:
            Réponse de l'API
        """
        if capabilities is None:
            capabilities = []
            
        url = f"{self.base_url}/agents/register"
        payload = {
            "agent_id": self.agent_id,
            "status": status,
            "version": version,
            "capabilities": capabilities,
            "registered_at": time.time()
        }
        
        try:
            self._create_session()
            async with self.session.post(url, json=payload) as response:
                response.raise_for_status()
                result = await response.json()
                logger.info(f"Agent {self.agent_id} enregistré avec succès")
                return result
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'agent: {str(e)}")
            raise
    
    async def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """
        Récupère les tâches en attente pour cet agent.
        
        Returns:
            Liste des tâches en attente
        """
        url = f"{self.base_url}/tasks/pending/{self.agent_id}"
        
        try:
            self._create_session()
            async with self.session.get(url) as response:
                response.raise_for_status()
                result = await response.json()
                return result.get("tasks", [])
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des tâches: {str(e)}")
            return []
    
    async def update_task_status(self, task_id: str, status: str, progress: int = None, 
                               result: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Met à jour le statut d'une tâche.
        
        Args:
            task_id: Identifiant de la tâche
            status: Nouveau statut (pending, processing, completed, failed)
            progress: Pourcentage de progression (0-100)
            result: Résultat de la tâche (pour les tâches terminées)
            
        Returns:
            Réponse de l'API
        """
        url = f"{self.base_url}/tasks/{task_id}/status"
        payload = {
            "agent_id": self.agent_id,
            "status": status,
            "updated_at": time.time()
        }
        
        # Ajout des paramètres optionnels
        if progress is not None:
            payload["progress"] = progress
            
        if result is not None:
            payload["result"] = result
        
        try:
            self._create_session()
            async with self.session.put(url, json=payload) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la tâche {task_id}: {str(e)}")
            raise
    
    async def save_analysis_result(self, analysis_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sauvegarde un résultat d'analyse dans l'API.
        
        Args:
            analysis_type: Type d'analyse
            data: Données d'analyse à sauvegarder
            
        Returns:
            Réponse de l'API
        """
        url = f"{self.base_url}/analysis/save"
        payload = {
            "agent_id": self.agent_id,
            "analysis_type": analysis_type,
            "data": data,
            "created_at": time.time()
        }
        
        try:
            self._create_session()
            async with self.session.post(url, json=payload) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des résultats d'analyse: {str(e)}")
            raise
    
    async def get_shop_data(self, data_type: str = "all") -> Dict[str, Any]:
        """
        Récupère des données de la boutique.
        
        Args:
            data_type: Type de données à récupérer (all, products, collections, etc.)
            
        Returns:
            Données de la boutique
        """
        url = f"{self.base_url}/shop/data/{data_type}"
        
        try:
            self._create_session()
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données de boutique: {str(e)}")
            raise
