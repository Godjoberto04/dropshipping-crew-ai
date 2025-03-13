#!/usr/bin/env python3
"""
Client API pour l'agent Data Analyzer.
Gère la communication avec l'API centrale du système.
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
import aiohttp
from aiohttp import ClientSession, ClientError

from config import settings, get_logger

logger = get_logger("api_client")

class ApiClient:
    """Client pour l'API centrale du système."""

    def __init__(self, base_url: str = None, agent_id: str = None):
        """
        Initialise le client API.
        
        Args:
            base_url: URL de base de l'API (optionnel, par défaut depuis la config)
            agent_id: Identifiant de l'agent (optionnel, par défaut depuis la config)
        """
        self.base_url = base_url or settings.API_BASE_URL
        self.agent_id = agent_id or settings.AGENT_ID
        self.session: Optional[ClientSession] = None
        
        logger.info(f"Initialisation du client API pour {self.agent_id} - Endpoint: {self.base_url}")
        
    async def _ensure_session(self) -> ClientSession:
        """
        S'assure qu'une session HTTP est active.
        
        Returns:
            Session HTTP active
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={"Content-Type": "application/json"}
            )
        return self.session
    
    async def close(self):
        """Ferme la session HTTP si elle est active."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Effectue une requête HTTP vers l'API.
        
        Args:
            method: Méthode HTTP (GET, POST, etc.)
            endpoint: Point d'entrée de l'API
            data: Données à envoyer (pour POST, PUT, etc.)
            params: Paramètres de requête (pour GET)
            
        Returns:
            Réponse JSON de l'API
            
        Raises:
            Exception: En cas d'erreur dans la requête
        """
        session = await self._ensure_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.request(
                method=method, 
                url=url, 
                json=data, 
                params=params
            ) as response:
                response_text = await response.text()
                
                if response.status >= 400:
                    logger.error(f"Erreur API ({response.status}): {response_text}")
                    raise Exception(f"Erreur API ({response.status}): {response_text}")
                
                # Certains endpoints peuvent ne pas retourner de JSON
                if response_text and response_text.strip():
                    return json.loads(response_text)
                return {}
                
        except ClientError as e:
            logger.error(f"Erreur de connexion à l'API: {str(e)}")
            raise Exception(f"Erreur de connexion à l'API: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {str(e)} - Réponse: {response_text}")
            raise Exception(f"Erreur de décodage JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue: {str(e)}")
            raise
    
    async def register_agent(
        self, 
        status: str = "online",
        version: str = settings.AGENT_VERSION,
        capabilities: List[str] = None
    ) -> Dict[str, Any]:
        """
        Enregistre l'agent auprès de l'API centrale.
        
        Args:
            status: Statut de l'agent (online, offline, etc.)
            version: Version de l'agent
            capabilities: Liste des capacités de l'agent
            
        Returns:
            Réponse de l'API
        """
        if capabilities is None:
            capabilities = []
            
        data = {
            "agent_id": self.agent_id,
            "status": status,
            "version": version,
            "capabilities": capabilities
        }
        
        logger.info(f"Enregistrement de l'agent avec {len(capabilities)} capacités")
        return await self._request("POST", "/agents/register", data=data)
    
    async def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """
        Récupère les tâches en attente pour l'agent.
        
        Returns:
            Liste des tâches en attente
        """
        params = {"agent_id": self.agent_id, "status": "pending"}
        response = await self._request("GET", "/tasks", params=params)
        
        tasks = response.get("tasks", [])
        if tasks:
            logger.info(f"Récupération de {len(tasks)} tâches en attente")
        
        return tasks
    
    async def update_task_status(
        self, 
        task_id: str, 
        status: str, 
        progress: int = None,
        result: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Met à jour le statut d'une tâche.
        
        Args:
            task_id: Identifiant de la tâche
            status: Nouveau statut (processing, completed, failed)
            progress: Progression (0-100)
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
        
        logger.info(f"Mise à jour de la tâche {task_id} - Status: {status}, Progress: {progress}")
        return await self._request("PATCH", f"/tasks/{task_id}", data=data)
    
    async def create_task(
        self, 
        target_agent_id: str,
        action: str,
        parameters: Dict[str, Any] = None,
        priority: int = 1
    ) -> Dict[str, Any]:
        """
        Crée une nouvelle tâche pour un autre agent.
        
        Args:
            target_agent_id: Identifiant de l'agent cible
            action: Action à effectuer
            parameters: Paramètres de l'action
            priority: Priorité de la tâche (1-5)
            
        Returns:
            Réponse de l'API avec les détails de la tâche créée
        """
        if parameters is None:
            parameters = {}
            
        data = {
            "agent_id": target_agent_id,
            "created_by": self.agent_id,
            "action": action,
            "parameters": parameters,
            "priority": priority
        }
        
        logger.info(f"Création d'une tâche pour {target_agent_id} - Action: {action}")
        return await self._request("POST", "/tasks", data=data)
        
    async def get_products(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Récupère la liste des produits avec filtres optionnels.
        
        Args:
            filters: Filtres à appliquer (catégorie, prix min/max, etc.)
            
        Returns:
            Liste des produits
        """
        params = filters or {}
        response = await self._request("GET", "/products", params=params)
        return response.get("products", [])
    
    async def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """
        Récupère les détails d'un produit spécifique.
        
        Args:
            product_id: Identifiant du produit
            
        Returns:
            Détails du produit
        """
        response = await self._request("GET", f"/products/{product_id}")
        return response
    
    async def save_analysis_result(
        self, 
        analysis_type: str,
        data: Dict[str, Any],
        source: str = "data_analyzer"
    ) -> Dict[str, Any]:
        """
        Sauvegarde les résultats d'une analyse.
        
        Args:
            analysis_type: Type d'analyse (trends, scoring, forecasting)
            data: Données d'analyse
            source: Source des données
            
        Returns:
            Réponse de l'API
        """
        payload = {
            "type": analysis_type,
            "data": data,
            "source": source,
            "agent_id": self.agent_id
        }
        
        logger.info(f"Sauvegarde des résultats d'analyse de type {analysis_type}")
        return await self._request("POST", "/analytics", data=payload)
