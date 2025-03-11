"""
Intégration avec l'agent Website Builder (Shopify)
"""

import logging
import json
from typing import Dict, Any, List, Optional

from tools.api_client import ApiClient

logger = logging.getLogger("content_generator.integrations.shopify")

class ShopifyClient:
    """
    Client pour interagir avec l'agent Website Builder (Shopify).
    
    Cette classe permet de publier du contenu généré vers la boutique Shopify
    via l'agent Website Builder.
    """
    
    def __init__(self, api_client: ApiClient):
        """
        Initialise le client Shopify.
        
        Args:
            api_client: Instance du client API centrale
        """
        self.api_client = api_client
        logger.info("Client Shopify initialisé")
    
    async def update_product_description(
        self,
        product_id: str,
        description: str,
        seo_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Met à jour la description d'un produit existant.
        
        Args:
            product_id: Identifiant du produit
            description: Nouvelle description du produit
            seo_metadata: Méta-données SEO (méta-description, titre, mots-clés)
            
        Returns:
            Résultat de la mise à jour
        """
        logger.info(f"Mise à jour de la description du produit {product_id}")
        
        try:
            # Préparer les paramètres de la tâche
            params = {
                "action": "update_product",
                "product_id": product_id,
                "fields": {
                    "description": description
                }
            }
            
            # Ajouter les méta-données SEO si fournies
            if seo_metadata:
                params["fields"]["seo_metadata"] = seo_metadata
            
            # Créer une tâche pour l'agent Website Builder
            task_data = await self.api_client.create_task(
                agent_id="website-builder",
                params=params
            )
            
            task_id = task_data.get("id")
            logger.debug(f"Tâche créée: {task_id}")
            
            # Attendre la fin de la tâche
            task_result = await self.api_client.wait_for_task_completion(task_id)
            
            if task_result.get("status") == "failed":
                logger.error(f"Échec de la mise à jour de la description: {task_result.get('result', {}).get('error')}")
                return {"success": False, "error": task_result.get("result", {}).get("error")}
            
            result = task_result.get("result", {})
            logger.info(f"Description du produit mise à jour avec succès")
            
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la description: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_product(
        self,
        product_data: Dict[str, Any],
        description: str,
        seo_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crée un nouveau produit avec la description générée.
        
        Args:
            product_data: Données du produit (nom, prix, etc.)
            description: Description du produit
            seo_metadata: Méta-données SEO (méta-description, titre, mots-clés)
            
        Returns:
            Résultat de la création
        """
        logger.info(f"Création d'un nouveau produit: {product_data.get('title', 'Inconnu')}")
        
        try:
            # S'assurer que la description est incluse dans les données produit
            product_data_with_description = product_data.copy()
            product_data_with_description["description"] = description
            
            # Ajouter les méta-données SEO si fournies
            if seo_metadata:
                product_data_with_description["seo_metadata"] = seo_metadata
            
            # Créer une tâche pour l'agent Website Builder
            task_data = await self.api_client.create_task(
                agent_id="website-builder",
                params={
                    "action": "add_product",
                    "product_data": product_data_with_description
                }
            )
            
            task_id = task_data.get("id")
            logger.debug(f"Tâche créée: {task_id}")
            
            # Attendre la fin de la tâche
            task_result = await self.api_client.wait_for_task_completion(task_id)
            
            if task_result.get("status") == "failed":
                logger.error(f"Échec de la création du produit: {task_result.get('result', {}).get('error')}")
                return {"success": False, "error": task_result.get("result", {}).get("error")}
            
            result = task_result.get("result", {})
            logger.info(f"Produit créé avec succès: {result.get('product_id')}")
            
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du produit: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_category_description(
        self,
        category_id: str,
        description: str,
        seo_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Met à jour la description d'une catégorie.
        
        Args:
            category_id: Identifiant de la catégorie
            description: Nouvelle description de la catégorie
            seo_metadata: Méta-données SEO (méta-description, titre, mots-clés)
            
        Returns:
            Résultat de la mise à jour
        """
        logger.info(f"Mise à jour de la description de la catégorie {category_id}")
        
        try:
            # Préparer les paramètres de la tâche
            params = {
                "action": "update_collection",
                "collection_id": category_id,
                "fields": {
                    "description": description
                }
            }
            
            # Ajouter les méta-données SEO si fournies
            if seo_metadata:
                params["fields"]["seo_metadata"] = seo_metadata
            
            # Créer une tâche pour l'agent Website Builder
            task_data = await self.api_client.create_task(
                agent_id="website-builder",
                params=params
            )
            
            task_id = task_data.get("id")
            logger.debug(f"Tâche créée: {task_id}")
            
            # Attendre la fin de la tâche
            task_result = await self.api_client.wait_for_task_completion(task_id)
            
            if task_result.get("status") == "failed":
                logger.error(f"Échec de la mise à jour de la catégorie: {task_result.get('result', {}).get('error')}")
                return {"success": False, "error": task_result.get("result", {}).get("error")}
            
            result = task_result.get("result", {})
            logger.info(f"Description de la catégorie mise à jour avec succès")
            
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la catégorie: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_blog_post(
        self,
        title: str,
        content: str,
        seo_metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        publish: bool = True
    ) -> Dict[str, Any]:
        """
        Crée un nouvel article de blog.
        
        Args:
            title: Titre de l'article
            content: Contenu de l'article
            seo_metadata: Méta-données SEO (méta-description, titre, mots-clés)
            tags: Liste des tags pour l'article
            publish: Si True, publie immédiatement l'article
            
        Returns:
            Résultat de la création
        """
        logger.info(f"Création d'un nouvel article de blog: {title}")
        
        try:
            # Préparer les données de l'article
            post_data = {
                "title": title,
                "content": content,
                "publish": publish
            }
            
            if tags:
                post_data["tags"] = tags
                
            if seo_metadata:
                post_data["seo_metadata"] = seo_metadata
            
            # Créer une tâche pour l'agent Website Builder
            task_data = await self.api_client.create_task(
                agent_id="website-builder",
                params={
                    "action": "create_blog_post",
                    "post_data": post_data
                }
            )
            
            task_id = task_data.get("id")
            logger.debug(f"Tâche créée: {task_id}")
            
            # Attendre la fin de la tâche
            task_result = await self.api_client.wait_for_task_completion(task_id)
            
            if task_result.get("status") == "failed":
                logger.error(f"Échec de la création de l'article: {task_result.get('result', {}).get('error')}")
                return {"success": False, "error": task_result.get("result", {}).get("error")}
            
            result = task_result.get("result", {})
            logger.info(f"Article de blog créé avec succès: {result.get('post_id')}")
            
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'article: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_page_content(
        self,
        page_id: str,
        content: str,
        seo_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Met à jour le contenu d'une page statique.
        
        Args:
            page_id: Identifiant de la page
            content: Nouveau contenu de la page
            seo_metadata: Méta-données SEO (méta-description, titre, mots-clés)
            
        Returns:
            Résultat de la mise à jour
        """
        logger.info(f"Mise à jour du contenu de la page {page_id}")
        
        try:
            # Préparer les paramètres de la tâche
            params = {
                "action": "update_page",
                "page_id": page_id,
                "fields": {
                    "content": content
                }
            }
            
            # Ajouter les méta-données SEO si fournies
            if seo_metadata:
                params["fields"]["seo_metadata"] = seo_metadata
            
            # Créer une tâche pour l'agent Website Builder
            task_data = await self.api_client.create_task(
                agent_id="website-builder",
                params=params
            )
            
            task_id = task_data.get("id")
            logger.debug(f"Tâche créée: {task_id}")
            
            # Attendre la fin de la tâche
            task_result = await self.api_client.wait_for_task_completion(task_id)
            
            if task_result.get("status") == "failed":
                logger.error(f"Échec de la mise à jour de la page: {task_result.get('result', {}).get('error')}")
                return {"success": False, "error": task_result.get("result", {}).get("error")}
            
            result = task_result.get("result", {})
            logger.info(f"Contenu de la page mis à jour avec succès")
            
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la page: {str(e)}")
            return {"success": False, "error": str(e)}