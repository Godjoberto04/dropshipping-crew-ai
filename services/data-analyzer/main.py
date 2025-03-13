#!/usr/bin/env python3
"""
Point d'entrée principal de l'agent Data Analyzer.
Gère la boucle principale de l'agent, le traitement des tâches et la coordination avec l'API centrale.
"""

import asyncio
import os
import json
import logging
import time
from typing import Dict, Any, List, Optional, Union

from config import settings, get_logger
from tools.api_client import ApiClient
from data_sources.trends.trends_analyzer import TrendsAnalyzer

logger = get_logger("data_analyzer_main")

class DataAnalyzerAgent:
    """Agent principal pour l'analyse de données et la recommandation de produits."""

    def __init__(self):
        """Initialise l'agent Data Analyzer et ses composants."""
        self.api_client = ApiClient(
            base_url=settings.API_BASE_URL,
            agent_id=settings.AGENT_ID
        )
        
        # Initialisation des sources de données
        self.trends_analyzer = TrendsAnalyzer()
        
        # État de l'agent
        self.is_running = False
        
        logger.info(f"Agent Data Analyzer initialisé (version: {settings.AGENT_VERSION})")
    
    async def register_agent(self):
        """Enregistre l'agent auprès de l'API centrale."""
        # Définition des capacités de l'agent
        capabilities = [
            "analyze_keywords",
            "analyze_product",
            "compare_products",
            "get_rising_products",
            "calculate_product_potential"
        ]
        
        # Enregistrement
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
        task_id = task.get("id", "unknown")
        action = task.get("params", {}).get("action", "")
        
        logger.info(f"Traitement de la tâche {task_id} - Action: {action}")
        await self.api_client.update_task_status(task_id, "processing", progress=10)
        
        try:
            # Création d'un identifiant pour suivre l'exécution
            execution_id = f"exec_{int(time.time())}_{task_id}"
            
            # Routage des actions vers les méthodes appropriées
            result = {}
            
            if action == "analyze_keywords":
                result = await self.handle_analyze_keywords(task, execution_id)
            elif action == "analyze_product":
                result = await self.handle_analyze_product(task, execution_id)
            elif action == "compare_products":
                result = await self.handle_compare_products(task, execution_id)
            elif action == "get_rising_products":
                result = await self.handle_get_rising_products(task, execution_id)
            elif action == "calculate_product_potential":
                result = await self.handle_calculate_product_potential(task, execution_id)
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
    
    async def handle_analyze_keywords(self, task: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """
        Gère l'analyse de mots-clés.
        
        Args:
            task: Tâche à traiter
            execution_id: Identifiant d'exécution pour le suivi
            
        Returns:
            Résultat de l'analyse
        """
        params = task.get("params", {})
        task_id = task.get("id", "unknown")
        
        # Extraction des paramètres
        keywords = params.get("keywords", [])
        timeframe = params.get("timeframe", "medium_term")
        geo = params.get("geo", None)
        category = params.get("category", 0)
        
        # Validation des paramètres
        if not keywords:
            raise ValueError("La liste de mots-clés est requise")
        
        logger.info(f"Analyse de mots-clés: {keywords}")
        await self.api_client.update_task_status(task_id, "processing", progress=30)
        
        # Analyse des mots-clés via Google Trends
        analysis_result = await asyncio.to_thread(
            self.trends_analyzer.analyze_keywords,
            keywords=keywords,
            timeframe=timeframe,
            geo=geo,
            category=category
        )
        
        await self.api_client.update_task_status(task_id, "processing", progress=70)
        
        # Sauvegarde des résultats dans l'API d'analyse
        analysis_data = {
            "execution_id": execution_id,
            "keywords": keywords,
            "timeframe": timeframe,
            "trend_metrics": analysis_result.get("trend_metrics", {}),
            "summary": analysis_result.get("summary", {})
        }
        
        await self.api_client.save_analysis_result(
            analysis_type="keyword_trends",
            data=analysis_data
        )
        
        # Extraction des données pour le retour
        result = {
            "summary": analysis_result.get("summary", {}),
            "trend_metrics": analysis_result.get("trend_metrics", {}),
            "interest_by_region": {}
        }
        
        # Conversion du DataFrame en dictionnaire
        interest_by_region = analysis_result.get("interest_by_region")
        if not interest_by_region.empty:
            result["interest_by_region"] = interest_by_region.to_dict()
        
        return result
    
    async def handle_analyze_product(self, task: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """
        Gère l'analyse complète d'un produit.
        
        Args:
            task: Tâche à traiter
            execution_id: Identifiant d'exécution pour le suivi
            
        Returns:
            Résultat de l'analyse
        """
        params = task.get("params", {})
        task_id = task.get("id", "unknown")
        
        # Extraction des paramètres
        product_name = params.get("product_name", "")
        product_keywords = params.get("product_keywords", [])
        timeframes = params.get("timeframes", None)
        geo = params.get("geo", None)
        
        # Validation des paramètres
        if not product_name:
            raise ValueError("Le nom du produit est requis")
        
        logger.info(f"Analyse du produit: {product_name}")
        await self.api_client.update_task_status(task_id, "processing", progress=30)
        
        # Analyse du produit
        analysis_result = await asyncio.to_thread(
            self.trends_analyzer.analyze_product,
            product_name=product_name,
            product_keywords=product_keywords,
            timeframes=timeframes,
            geo=geo
        )
        
        await self.api_client.update_task_status(task_id, "processing", progress=70)
        
        # Sauvegarde des résultats
        analysis_data = {
            "execution_id": execution_id,
            "product_name": product_name,
            "product_keywords": product_keywords,
            "overall_trend_score": analysis_result.get("overall_trend_score", 0),
            "is_trending": analysis_result.get("is_trending", False),
            "seasonality": analysis_result.get("seasonality", {}),
            "conclusion": analysis_result.get("conclusion", {})
        }
        
        await self.api_client.save_analysis_result(
            analysis_type="product_analysis",
            data=analysis_data
        )
        
        # Simplifie l'objet de retour (évite les structures trop volumineuses)
        simplified_result = {
            "product_name": product_name,
            "overall_trend_score": analysis_result.get("overall_trend_score", 0),
            "is_trending": analysis_result.get("is_trending", False),
            "seasonality": analysis_result.get("seasonality", {}),
            "conclusion": analysis_result.get("conclusion", {}),
            "keywords": analysis_result.get("keywords", [])
        }
        
        return simplified_result
    
    async def handle_compare_products(self, task: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """
        Gère la comparaison de plusieurs produits.
        
        Args:
            task: Tâche à traiter
            execution_id: Identifiant d'exécution pour le suivi
            
        Returns:
            Résultat de la comparaison
        """
        params = task.get("params", {})
        task_id = task.get("id", "unknown")
        
        # Extraction des paramètres
        products = params.get("products", [])
        timeframe = params.get("timeframe", "medium_term")
        geo = params.get("geo", None)
        
        # Validation des paramètres
        if not products or len(products) < 2:
            raise ValueError("Au moins deux produits sont requis pour une comparaison")
        
        logger.info(f"Comparaison de {len(products)} produits")
        await self.api_client.update_task_status(task_id, "processing", progress=30)
        
        # Comparer les produits
        comparison_result = await asyncio.to_thread(
            self.trends_analyzer.compare_products,
            products=products,
            timeframe=timeframe,
            geo=geo
        )
        
        await self.api_client.update_task_status(task_id, "processing", progress=70)
        
        # Sauvegarde des résultats
        await self.api_client.save_analysis_result(
            analysis_type="product_comparison",
            data={
                "execution_id": execution_id,
                "products": products,
                "timeframe": timeframe,
                "results": comparison_result
            }
        )
        
        return comparison_result
    
    async def handle_get_rising_products(self, task: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """
        Gère la récupération des produits en forte croissance.
        
        Args:
            task: Tâche à traiter
            execution_id: Identifiant d'exécution pour le suivi
            
        Returns:
            Liste des produits en croissance
        """
        params = task.get("params", {})
        task_id = task.get("id", "unknown")
        
        # Extraction des paramètres
        category = params.get("category", 0)
        geo = params.get("geo", None)
        limit = params.get("limit", 10)
        
        # Limite le nombre de résultats
        limit = min(limit, 20)
        
        logger.info(f"Récupération des produits en croissance (catégorie: {category}, geo: {geo})")
        await self.api_client.update_task_status(task_id, "processing", progress=30)
        
        # Récupération des produits en croissance
        rising_products = await asyncio.to_thread(
            self.trends_analyzer.get_rising_products,
            category=category,
            geo=geo,
            limit=limit
        )
        
        await self.api_client.update_task_status(task_id, "processing", progress=70)
        
        # Sauvegarde des résultats
        await self.api_client.save_analysis_result(
            analysis_type="rising_products",
            data={
                "execution_id": execution_id,
                "category": category,
                "geo": geo,
                "products": rising_products
            }
        )
        
        return {
            "rising_products": rising_products,
            "timestamp": time.time()
        }
    
    async def handle_calculate_product_potential(self, task: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """
        Calcule le potentiel global d'un produit en combinant plusieurs sources de données.
        
        Args:
            task: Tâche à traiter
            execution_id: Identifiant d'exécution pour le suivi
            
        Returns:
            Évaluation du potentiel du produit
        """
        params = task.get("params", {})
        task_id = task.get("id", "unknown")
        
        # Extraction des paramètres
        product_name = params.get("product_name", "")
        product_data = params.get("product_data", {})
        
        # Validation des paramètres
        if not product_name:
            raise ValueError("Le nom du produit est requis")
        
        logger.info(f"Calcul du potentiel pour: {product_name}")
        await self.api_client.update_task_status(task_id, "processing", progress=30)
        
        # Analyse de tendance via Google Trends
        trend_analysis = await asyncio.to_thread(
            self.trends_analyzer.analyze_product,
            product_name=product_name
        )
        
        await self.api_client.update_task_status(task_id, "processing", progress=70)
        
        # Calcul simplifié du potentiel
        trend_score = trend_analysis.get("overall_trend_score", 50)
        is_trending = trend_analysis.get("is_trending", False)
        is_seasonal = trend_analysis.get("seasonality", {}).get("is_seasonal", False)
        
        # Facteurs supplémentaires (simplifiés pour cette version)
        market_factors = {
            "market_size": product_data.get("market_size", 50),
            "competition": product_data.get("competition", 50),
            "profit_margin": product_data.get("profit_margin", 20),
            "shipping_complexity": product_data.get("shipping_complexity", 50)
        }
        
        # Calcul du score global (simpliste pour cette implémentation)
        overall_potential = (
            trend_score * 0.4 +
            market_factors["market_size"] * 0.2 +
            (100 - market_factors["competition"]) * 0.2 +
            market_factors["profit_margin"] * 0.1 +
            (100 - market_factors["shipping_complexity"]) * 0.1
        )
        
        # Classification du potentiel
        if overall_potential >= settings.SCORING_THRESHOLDS["high_potential"]:
            potential_category = "high"
            recommendation = "Recommandé comme produit prioritaire"
        elif overall_potential >= settings.SCORING_THRESHOLDS["medium_potential"]:
            potential_category = "medium"
            recommendation = "Potentiel intéressant, à considérer"
        elif overall_potential >= settings.SCORING_THRESHOLDS["low_potential"]:
            potential_category = "low"
            recommendation = "Potentiel limité, à considérer avec prudence"
        else:
            potential_category = "very_low"
            recommendation = "Non recommandé à moins de facteurs spécifiques favorables"
        
        # Préparation du résultat
        result = {
            "product_name": product_name,
            "overall_potential": overall_potential,
            "potential_category": potential_category,
            "recommendation": recommendation,
            "trend_score": trend_score,
            "is_trending": is_trending,
            "is_seasonal": is_seasonal,
            "market_factors": market_factors
        }
        
        # Sauvegarde des résultats
        await self.api_client.save_analysis_result(
            analysis_type="product_potential",
            data={
                "execution_id": execution_id,
                "product_name": product_name,
                "result": result
            }
        )
        
        return result
    
    async def poll_tasks(self):
        """Boucle principale de l'agent qui vérifie les tâches à traiter."""
        self.is_running = True
        
        while self.is_running:
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
    
    async def stop(self):
        """Arrête l'agent proprement."""
        logger.info("Arrêt de l'agent Data Analyzer...")
        self.is_running = False
        await self.api_client.close()

async def main():
    """Fonction principale pour démarrer l'agent."""
    agent = DataAnalyzerAgent()
    
    try:
        # Enregistrement de l'agent
        await agent.register_agent()
        
        # Démarrage de la boucle principale
        await agent.poll_tasks()
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur fatale: {str(e)}", exc_info=True)
    finally:
        await agent.stop()

if __name__ == "__main__":
    logger.info("Démarrage de l'agent Data Analyzer")
    asyncio.run(main())
