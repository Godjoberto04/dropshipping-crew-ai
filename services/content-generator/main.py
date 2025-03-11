#!/usr/bin/env python3
"""
Content Generator - Agent principal pour la génération de contenu e-commerce
Fait partie du projet Dropshipping Crew AI

Ce module est le point d'entrée principal de l'agent Content Generator.
Il gère la boucle principale de l'agent, la communication avec l'API centrale,
et l'orchestration des différents générateurs de contenu.
"""

import asyncio
import logging
import os
import json
import time
from typing import Dict, Any, List, Optional
import uuid

from config import settings
from tools.api_client import ApiClient
from tools.claude_client import ClaudeClient
from generators.product_description import ProductDescriptionGenerator
from optimizers.seo_optimizer import SEOOptimizer
from integrations.data_analyzer import DataAnalyzerClient
from integrations.shopify import ShopifyClient

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"content_generator_{time.strftime('%Y%m%d')}.log")
    ]
)
logger = logging.getLogger("content_generator")

class ContentGeneratorAgent:
    """Agent principal pour la génération de contenu e-commerce."""

    def __init__(self):
        """Initialise l'agent Content Generator et ses dépendances."""
        self.api_client = ApiClient(
            base_url=settings.API_BASE_URL,
            agent_id=settings.AGENT_ID
        )
        
        self.claude_client = ClaudeClient(
            api_key=settings.CLAUDE_API_KEY,
            model=settings.CLAUDE_MODEL,
        )
        
        # Initialisation des clients d'intégration
        self.data_analyzer_client = DataAnalyzerClient(self.api_client)
        self.shopify_client = ShopifyClient(self.api_client)
        
        # Initialisation des générateurs
        self.product_desc_generator = ProductDescriptionGenerator(
            claude_client=self.claude_client,
            templates_dir=settings.TEMPLATES_DIR
        )
        
        # Initialisation des optimiseurs
        self.seo_optimizer = SEOOptimizer()
        
        logger.info(f"Content Generator Agent initialisé (version: {settings.AGENT_VERSION})")
        
    async def register_agent(self):
        """Enregistre l'agent auprès de l'API centrale."""
        capabilities = [
            "generate_product_description",
            "optimize_seo_content"
            # D'autres capacités seront ajoutées dans les phases suivantes
        ]
        
        await self.api_client.register_agent(
            status="online",
            version=settings.AGENT_VERSION,
            capabilities=capabilities
        )
        
        logger.info(f"Agent enregistré avec {len(capabilities)} capacités")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite une tâche reçue de l'API centrale.
        
        Args:
            task: Dictionnaire contenant les détails de la tâche
            
        Returns:
            Dictionnaire contenant le résultat de la tâche
        """
        task_id = task.get("id")
        action = task.get("params", {}).get("action")
        
        logger.info(f"Traitement de la tâche {task_id} - Action: {action}")
        await self.api_client.update_task_status(task_id, "processing", progress=10)
        
        try:
            result = {}
            
            # Routage des actions vers les méthodes appropriées
            if action == "generate_product_description":
                result = await self.handle_generate_product_description(task)
            elif action == "optimize_content":
                result = await self.handle_optimize_content(task)
            else:
                raise ValueError(f"Action non reconnue: {action}")
            
            # Marquer la tâche comme terminée
            await self.api_client.update_task_status(
                task_id, 
                "completed", 
                progress=100, 
                result=result
            )
            
            logger.info(f"Tâche {task_id} terminée avec succès")
            return result
            
        except Exception as e:
            error_msg = f"Erreur lors du traitement de la tâche {task_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Marquer la tâche comme échouée
            await self.api_client.update_task_status(
                task_id, 
                "failed", 
                result={"error": str(e)}
            )
            
            raise
    
    async def handle_generate_product_description(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gère la génération de description de produit.
        
        Args:
            task: Dictionnaire contenant les détails de la tâche
            
        Returns:
            Dictionnaire contenant la description générée et les méta-données
        """
        task_id = task.get("id")
        params = task.get("params", {})
        
        # Récupération des informations produit
        product_data = params.get("product_data", {})
        tone = params.get("tone", "persuasive")
        language = params.get("language", "fr")
        niche = params.get("niche", "general")
        seo_optimize = params.get("seo_optimize", True)
        
        logger.info(f"Génération de description pour produit: {product_data.get('name', 'Inconnu')}")
        await self.api_client.update_task_status(task_id, "processing", progress=30)
        
        # Enrichissement des données produit si nécessaire
        if params.get("enrich_data", False) and product_data.get("product_id"):
            product_data = await self.data_analyzer_client.get_product_details(
                product_data.get("product_id")
            )
        
        # Génération de la description
        raw_description = await self.product_desc_generator.generate(
            product_data=product_data,
            tone=tone,
            language=language,
            niche=niche
        )
        
        await self.api_client.update_task_status(task_id, "processing", progress=60)
        
        # Optimisation SEO si demandée
        if seo_optimize:
            keywords = params.get("keywords", [])
            if not keywords and product_data.get("name"):
                # Extraction de mots-clés à partir du nom du produit
                keywords = self.seo_optimizer.extract_keywords(product_data.get("name", ""))
                
            optimized_description = self.seo_optimizer.optimize(
                content=raw_description,
                keywords=keywords,
                content_type="product_description"
            )
            
            meta_description = self.seo_optimizer.generate_meta_description(
                content=optimized_description,
                product_name=product_data.get("name", ""),
                max_length=160
            )
            
            result = {
                "description": optimized_description,
                "seo_metadata": {
                    "meta_description": meta_description,
                    "title_tag": f"{product_data.get('name', 'Produit')} - Achetez en ligne",
                    "keywords": keywords
                },
                "raw_description": raw_description
            }
        else:
            result = {
                "description": raw_description,
                "seo_metadata": {},
                "raw_description": raw_description
            }
        
        await self.api_client.update_task_status(task_id, "processing", progress=90)
        
        # Si l'auto-publication est activée, publier via Website Builder
        if params.get("auto_publish", False) and product_data.get("product_id"):
            try:
                await self.shopify_client.update_product_description(
                    product_id=product_data.get("product_id"),
                    description=result["description"],
                    seo_metadata=result["seo_metadata"]
                )
                result["published"] = True
            except Exception as e:
                logger.error(f"Erreur lors de la publication: {str(e)}")
                result["published"] = False
                result["publish_error"] = str(e)
        
        return result
    
    async def handle_optimize_content(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gère l'optimisation SEO d'un contenu existant.
        
        Args:
            task: Dictionnaire contenant les détails de la tâche
            
        Returns:
            Dictionnaire contenant le contenu optimisé et les méta-données
        """
        task_id = task.get("id")
        params = task.get("params", {})
        
        content = params.get("content", "")
        content_type = params.get("content_type", "generic")
        keywords = params.get("keywords", [])
        
        logger.info(f"Optimisation SEO pour contenu de type: {content_type}")
        await self.api_client.update_task_status(task_id, "processing", progress=40)
        
        # Extraction de mots-clés si non fournis
        if not keywords:
            keywords = self.seo_optimizer.extract_keywords(content)
        
        # Optimisation du contenu
        optimized_content = self.seo_optimizer.optimize(
            content=content,
            keywords=keywords,
            content_type=content_type
        )
        
        # Génération de méta-description
        meta_description = self.seo_optimizer.generate_meta_description(
            content=optimized_content,
            product_name=params.get("title", ""),
            max_length=160
        )
        
        await self.api_client.update_task_status(task_id, "processing", progress=90)
        
        return {
            "optimized_content": optimized_content,
            "seo_metadata": {
                "meta_description": meta_description,
                "keywords": keywords
            },
            "original_content": content,
            "improvement_score": self.seo_optimizer.calculate_improvement_score(content, optimized_content)
        }
    
    async def poll_tasks(self):
        """Boucle principale de l'agent qui vérifie les tâches à traiter."""
        while True:
            try:
                # Récupérer les tâches en attente
                tasks = await self.api_client.get_pending_tasks()
                
                if tasks:
                    logger.info(f"Récupération de {len(tasks)} tâches en attente")
                    
                    # Traiter chaque tâche
                    for task in tasks:
                        await self.process_task(task)
                
                # Pause avant la prochaine vérification
                await asyncio.sleep(settings.POLL_INTERVAL)
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle principale: {str(e)}", exc_info=True)
                await asyncio.sleep(settings.ERROR_RETRY_INTERVAL)

async def main():
    """Fonction principale pour démarrer l'agent."""
    agent = ContentGeneratorAgent()
    
    # Enregistrement de l'agent
    await agent.register_agent()
    
    # Démarrage de la boucle principale
    await agent.poll_tasks()

if __name__ == "__main__":
    logger.info("Démarrage de l'agent Content Generator")
    asyncio.run(main())