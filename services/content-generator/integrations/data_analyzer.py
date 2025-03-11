"""
Intégration avec l'agent Data Analyzer
"""

import logging
import json
from typing import Dict, Any, List, Optional

from tools.api_client import ApiClient

logger = logging.getLogger("content_generator.integrations.data_analyzer")

class DataAnalyzerClient:
    """
    Client pour interagir avec l'agent Data Analyzer.
    
    Cette classe permet de récupérer des informations sur les produits
    et les analyses de marché auprès de l'agent Data Analyzer.
    """
    
    def __init__(self, api_client: ApiClient):
        """
        Initialise le client Data Analyzer.
        
        Args:
            api_client: Instance du client API centrale
        """
        self.api_client = api_client
        logger.info("Client Data Analyzer initialisé")
    
    async def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """
        Récupère les détails complets d'un produit analysé.
        
        Args:
            product_id: Identifiant du produit
            
        Returns:
            Détails complets du produit
        """
        logger.info(f"Récupération des détails du produit {product_id}")
        
        try:
            # Créer une tâche pour l'agent Data Analyzer
            task_data = await self.api_client.create_task(
                agent_id="data-analyzer",
                params={
                    "action": "get_product_details",
                    "product_id": product_id
                }
            )
            
            task_id = task_data.get("id")
            logger.debug(f"Tâche créée: {task_id}")
            
            # Attendre la fin de la tâche
            task_result = await self.api_client.wait_for_task_completion(task_id)
            
            if task_result.get("status") == "failed":
                logger.error(f"Échec de la récupération des détails du produit: {task_result.get('result', {}).get('error')}")
                return {}
            
            product_details = task_result.get("result", {}).get("product_details", {})
            logger.info(f"Détails du produit récupérés avec succès")
            
            return product_details
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des détails du produit: {str(e)}")
            return {}
    
    async def get_market_analysis(self, niche: str) -> Dict[str, Any]:
        """
        Récupère une analyse de marché pour une niche spécifique.
        
        Args:
            niche: Niche ou catégorie de produits
            
        Returns:
            Analyse de marché
        """
        logger.info(f"Récupération de l'analyse de marché pour la niche: {niche}")
        
        try:
            # Créer une tâche pour l'agent Data Analyzer
            task_data = await self.api_client.create_task(
                agent_id="data-analyzer",
                params={
                    "action": "analyze_market",
                    "niche": niche
                }
            )
            
            task_id = task_data.get("id")
            logger.debug(f"Tâche créée: {task_id}")
            
            # Attendre la fin de la tâche
            task_result = await self.api_client.wait_for_task_completion(task_id)
            
            if task_result.get("status") == "failed":
                logger.error(f"Échec de l'analyse de marché: {task_result.get('result', {}).get('error')}")
                return {}
            
            market_analysis = task_result.get("result", {}).get("market_analysis", {})
            logger.info(f"Analyse de marché récupérée avec succès")
            
            return market_analysis
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de marché: {str(e)}")
            return {}
    
    async def get_keywords_suggestions(
        self,
        product_name: str,
        niche: str,
        count: int = 10
    ) -> List[str]:
        """
        Récupère des suggestions de mots-clés pertinents.
        
        Args:
            product_name: Nom du produit
            niche: Niche ou catégorie de produits
            count: Nombre de mots-clés à suggérer
            
        Returns:
            Liste de mots-clés suggérés
        """
        logger.info(f"Récupération de suggestions de mots-clés pour: {product_name}")
        
        try:
            # Créer une tâche pour l'agent Data Analyzer
            task_data = await self.api_client.create_task(
                agent_id="data-analyzer",
                params={
                    "action": "suggest_keywords",
                    "product_name": product_name,
                    "niche": niche,
                    "count": count
                }
            )
            
            task_id = task_data.get("id")
            logger.debug(f"Tâche créée: {task_id}")
            
            # Attendre la fin de la tâche
            task_result = await self.api_client.wait_for_task_completion(task_id)
            
            if task_result.get("status") == "failed":
                logger.error(f"Échec de la suggestion de mots-clés: {task_result.get('result', {}).get('error')}")
                return []
            
            keywords = task_result.get("result", {}).get("keywords", [])
            logger.info(f"Suggestions de mots-clés récupérées avec succès: {len(keywords)} mots-clés")
            
            return keywords
            
        except Exception as e:
            logger.error(f"Erreur lors de la suggestion de mots-clés: {str(e)}")
            return []