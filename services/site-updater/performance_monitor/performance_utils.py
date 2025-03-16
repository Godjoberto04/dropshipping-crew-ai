"""
Performance Utilities Module
Ce module contient des fonctions utilitaires pour l'analyse et l'optimisation des performances,
complétant les fonctionnalités du PerformanceManager principal.
"""

import logging
import asyncio
import aiohttp
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Configuration du logging
logger = logging.getLogger("PerformanceUtils")

class ImageOptimizer:
    """
    Classe pour l'optimisation des images d'un site web
    """
    
    @staticmethod
    async def optimize_image(image_url: str, target_format: str = "webp") -> Dict[str, Any]:
        """
        Optimise une image en la convertissant au format spécifié et en appliquant une compression
        
        Args:
            image_url: URL de l'image à optimiser
            target_format: Format cible (webp, avif, etc.)
            
        Returns:
            Résultat de l'optimisation avec les métadonnées
        """
        logger.info(f"Optimisation de l'image {image_url} vers le format {target_format}")
        
        try:
            # Dans une implémentation réelle, cette fonction téléchargerait l'image,
            # la convertirait et la compresserait avec des bibliothèques comme Pillow
            # puis téléverserait l'image optimisée via l'API Shopify
            await asyncio.sleep(1)  # Simulation du temps de traitement
            
            # Simuler une réduction de taille
            original_size = 1500000  # Taille fictive en octets
            optimized_size = int(original_size * 0.4)  # Simulation d'une réduction de 60%
            
            result = {
                "original_url": image_url,
                "original_format": image_url.split(".")[-1],
                "original_size": original_size,
                "optimized_format": target_format,
                "optimized_size": optimized_size,
                "optimization_ratio": round((original_size - optimized_size) / original_size * 100, 1),
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Image optimisée: {result['optimization_ratio']}% de réduction")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation de l'image: {str(e)}")
            return {
                "original_url": image_url,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    async def bulk_optimize_images(image_urls: List[str], target_format: str = "webp") -> Dict[str, Any]:
        """
        Optimise un lot d'images en parallèle
        
        Args:
            image_urls: Liste des URLs d'images à optimiser
            target_format: Format cible (webp, avif, etc.)
            
        Returns:
            Résultats d'optimisation pour toutes les images
        """
        logger.info(f"Optimisation en masse de {len(image_urls)} images")
        
        # Créer les tâches d'optimisation pour chaque image
        optimization_tasks = [ImageOptimizer.optimize_image(url, target_format) for url in image_urls]
        
        # Exécuter toutes les tâches en parallèle
        results = await asyncio.gather(*optimization_tasks, return_exceptions=True)
        
        # Traitement des résultats
        successful = [r for r in results if isinstance(r, dict) and r.get("status") == "success"]
        failed = [r for r in results if isinstance(r, dict) and r.get("status") == "error"]
        exceptions = [r for r in results if isinstance(r, Exception)]
        
        # Calcul des statistiques
        total_original_size = sum(r.get("original_size", 0) for r in successful)
        total_optimized_size = sum(r.get("optimized_size", 0) for r in successful)
        overall_reduction = 0
        if total_original_size > 0:
            overall_reduction = round((total_original_size - total_optimized_size) / total_original_size * 100, 1)
        
        summary = {
            "total_images": len(image_urls),
            "successful_optimizations": len(successful),
            "failed_optimizations": len(failed) + len(exceptions),
            "total_original_size_bytes": total_original_size,
            "total_optimized_size_bytes": total_optimized_size,
            "total_bytes_saved": total_original_size - total_optimized_size,
            "overall_reduction_percentage": overall_reduction,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Optimisation en masse terminée: {summary['successful_optimizations']} réussies, "
                   f"{summary['failed_optimizations']} échouées, {summary['overall_reduction_percentage']}% d'économie")
        
        return {
            "summary": summary,
            "results": {
                "successful": successful,
                "failed": failed,
                "exceptions": [str(e) for e in exceptions]
            }
        }


class ResourceMinifier:
    """
    Classe pour la minification des ressources JS et CSS
    """
    
    @staticmethod
    async def minify_js(js_content: str) -> Dict[str, Any]:
        """
        Minifie un contenu JavaScript
        
        Args:
            js_content: Contenu JavaScript à minifier
            
        Returns:
            Résultat de la minification
        """
        logger.info("Minification d'un contenu JavaScript")
        
        try:
            # Dans une implémentation réelle, on utiliserait une bibliothèque de minification
            # comme UglifyJS ou Terser via un service ou une bibliothèque Python
            
            # Simuler la minification en supprimant les commentaires, espaces et sauts de ligne
            # Noter que ceci est une simplification grossière et ne fonctionne pas pour un vrai JS
            minified = js_content
            # Supprimer les commentaires sur une ligne
            minified = re.sub(r'//.*$', '', minified, flags=re.MULTILINE)
            # Supprimer les commentaires multi-lignes
            minified = re.sub(r'/\*.*?\*/', '', minified, flags=re.DOTALL)
            # Supprimer les espaces inutiles
            minified = re.sub(r'\s+', ' ', minified)
            # Supprimer les espaces autour des opérateurs
            minified = re.sub(r'\s*([+\-*/%=<>!&|,;:(){}\[\]])\s*', r'\1', minified)
            
            original_size = len(js_content)
            minified_size = len(minified)
            
            result = {
                "original_size_bytes": original_size,
                "minified_size_bytes": minified_size,
                "bytes_saved": original_size - minified_size,
                "reduction_percentage": round((original_size - minified_size) / original_size * 100, 1),
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Minification JavaScript terminée: {result['reduction_percentage']}% de réduction")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la minification JavaScript: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    async def minify_css(css_content: str) -> Dict[str, Any]:
        """
        Minifie un contenu CSS
        
        Args:
            css_content: Contenu CSS à minifier
            
        Returns:
            Résultat de la minification
        """
        logger.info("Minification d'un contenu CSS")
        
        try:
            # Dans une implémentation réelle, on utiliserait une bibliothèque de minification
            # comme cssnano ou csso via un service ou une bibliothèque Python
            
            # Simuler la minification en supprimant les commentaires, espaces et sauts de ligne
            # Noter que ceci est une simplification grossière et ne fonctionne pas pour un vrai CSS
            minified = css_content
            # Supprimer les commentaires
            minified = re.sub(r'/\*.*?\*/', '', minified, flags=re.DOTALL)
            # Supprimer les espaces inutiles
            minified = re.sub(r'\s+', ' ', minified)
            # Supprimer les espaces autour des opérateurs
            minified = re.sub(r'\s*([{};:,])\s*', r'\1', minified)
            
            original_size = len(css_content)
            minified_size = len(minified)
            
            result = {
                "original_size_bytes": original_size,
                "minified_size_bytes": minified_size,
                "bytes_saved": original_size - minified_size,
                "reduction_percentage": round((original_size - minified_size) / original_size * 100, 1),
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Minification CSS terminée: {result['reduction_percentage']}% de réduction")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la minification CSS: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


class PerformanceMetricsAnalyzer:
    """
    Classe pour l'analyse avancée des métriques de performance
    """
    
    @staticmethod
    def analyze_trend(metrics: List[float]) -> Dict[str, Any]:
        """
        Analyse la tendance d'une série de métriques
        
        Args:
            metrics: Liste de valeurs de métriques dans l'ordre chronologique
            
        Returns:
            Analyse de la tendance
        """
        if not metrics or len(metrics) < 2:
            return {
                "status": "insufficient_data",
                "message": "Au moins deux points de données sont nécessaires pour analyser une tendance"
            }
        
        # Calculer les variations
        changes = [metrics[i] - metrics[i-1] for i in range(1, len(metrics))]
        
        # Déterminer la tendance principale
        positive_changes = sum(1 for c in changes if c > 0)
        negative_changes = sum(1 for c in changes if c < 0)
        no_changes = sum(1 for c in changes if c == 0)
        
        # Calculer les statistiques
        current = metrics[-1]
        first = metrics[0]
        min_val = min(metrics)
        max_val = max(metrics)
        avg = sum(metrics) / len(metrics)
        
        # Déterminer la tendance globale
        if positive_changes > negative_changes + no_changes:
            trend = "increasing"
            trend_strength = positive_changes / len(changes)
        elif negative_changes > positive_changes + no_changes:
            trend = "decreasing"
            trend_strength = negative_changes / len(changes)
        else:
            trend = "stable"
            trend_strength = no_changes / len(changes)
        
        # Calculer le changement total
        total_change = current - first
        total_change_percentage = round((current - first) / first * 100, 1) if first != 0 else float('inf')
        
        return {
            "status": "success",
            "trend": trend,
            "trend_strength": round(trend_strength, 2),
            "total_change": round(total_change, 3),
            "total_change_percentage": total_change_percentage,
            "current_value": current,
            "initial_value": first,
            "min_value": min_val,
            "max_value": max_val,
            "average": round(avg, 3),
            "data_points": len(metrics),
            "volatility": round(sum(abs(c) for c in changes) / len(changes), 3) if changes else 0
        }
    
    @staticmethod
    def detect_performance_regression(current_metrics: Dict[str, float], 
                                     baseline_metrics: Dict[str, float], 
                                     threshold_percentage: float = 10.0) -> Dict[str, Any]:
        """
        Détecte les régressions de performance entre deux ensembles de métriques
        
        Args:
            current_metrics: Métriques actuelles
            baseline_metrics: Métriques de référence
            threshold_percentage: Pourcentage de dégradation à partir duquel signaler une régression
            
        Returns:
            Analyse des régressions
        """
        regressions = {}
        improvements = {}
        
        for metric, current_value in current_metrics.items():
            if metric in baseline_metrics:
                baseline_value = baseline_metrics[metric]
                
                # Calculer la variation en pourcentage
                if baseline_value != 0:
                    change_percentage = (current_value - baseline_value) / baseline_value * 100
                else:
                    change_percentage = float('inf') if current_value > 0 else 0
                
                # Déterminer s'il s'agit d'une amélioration ou d'une régression
                # Pour certaines métriques, plus c'est bas, mieux c'est (temps de chargement, etc.)
                # Pour d'autres, plus c'est haut, mieux c'est (score de performance, etc.)
                is_lower_better = metric in [
                    "page_load_time", "time_to_first_byte", "first_contentful_paint",
                    "largest_contentful_paint", "cumulative_layout_shift", "first_input_delay",
                    "server_response_time"
                ]
                
                if is_lower_better:
                    # Pour ces métriques, une augmentation est une régression
                    if change_percentage > threshold_percentage:
                        regressions[metric] = {
                            "current_value": current_value,
                            "baseline_value": baseline_value,
                            "change_percentage": round(change_percentage, 1),
                            "severity": "high" if change_percentage > threshold_percentage * 2 else "medium"
                        }
                    elif change_percentage < -threshold_percentage:
                        improvements[metric] = {
                            "current_value": current_value,
                            "baseline_value": baseline_value,
                            "change_percentage": round(change_percentage, 1),
                            "magnitude": "significant" if change_percentage < -threshold_percentage * 2 else "moderate"
                        }
                else:
                    # Pour ces métriques, une diminution est une régression
                    if change_percentage < -threshold_percentage:
                        regressions[metric] = {
                            "current_value": current_value,
                            "baseline_value": baseline_value,
                            "change_percentage": round(change_percentage, 1),
                            "severity": "high" if change_percentage < -threshold_percentage * 2 else "medium"
                        }
                    elif change_percentage > threshold_percentage:
                        improvements[metric] = {
                            "current_value": current_value,
                            "baseline_value": baseline_value,
                            "change_percentage": round(change_percentage, 1),
                            "magnitude": "significant" if change_percentage > threshold_percentage * 2 else "moderate"
                        }
        
        return {
            "has_regressions": len(regressions) > 0,
            "has_improvements": len(improvements) > 0,
            "regressions": regressions,
            "improvements": improvements,
            "metrics_analyzed": len(current_metrics),
            "threshold_percentage": threshold_percentage,
            "timestamp": datetime.now().isoformat()
        }


class SEOPerformanceAnalyzer:
    """
    Classe pour l'analyse des performances SEO liées à la vitesse
    """
    
    @staticmethod
    def analyze_core_web_vitals(metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyse les Core Web Vitals et leur impact sur le référencement
        
        Args:
            metrics: Métriques de performance incluant les Core Web Vitals
            
        Returns:
            Analyse des Core Web Vitals
        """
        # Seuils recommandés par Google
        thresholds = {
            "largest_contentful_paint": {
                "good": 2.5,  # en secondes
                "needs_improvement": 4.0  # en secondes
            },
            "first_input_delay": {
                "good": 0.1,  # en secondes
                "needs_improvement": 0.3  # en secondes
            },
            "cumulative_layout_shift": {
                "good": 0.1,  # score sans unité
                "needs_improvement": 0.25  # score sans unité
            }
        }
        
        results = {}
        for metric, threshold in thresholds.items():
            if metric in metrics:
                value = metrics[metric]
                
                if value <= threshold["good"]:
                    status = "good"
                    impact = "positive"
                elif value <= threshold["needs_improvement"]:
                    status = "needs_improvement"
                    impact = "moderate"
                else:
                    status = "poor"
                    impact = "negative"
                
                results[metric] = {
                    "value": value,
                    "status": status,
                    "impact": impact,
                    "threshold_good": threshold["good"],
                    "threshold_needs_improvement": threshold["needs_improvement"]
                }
        
        # Synthèse globale
        all_statuses = [r["status"] for r in results.values()]
        if "poor" in all_statuses:
            overall_status = "poor"
            overall_impact = "negative"
        elif "needs_improvement" in all_statuses:
            overall_status = "needs_improvement"
            overall_impact = "moderate"
        elif len(all_statuses) == 3:  # Les 3 métriques sont bonnes
            overall_status = "good"
            overall_impact = "positive"
        else:
            overall_status = "incomplete"
            overall_impact = "unknown"
        
        return {
            "metrics": results,
            "overall_status": overall_status,
            "overall_impact": overall_impact,
            "recommendations": SEOPerformanceAnalyzer._generate_cwv_recommendations(results),
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def _generate_cwv_recommendations(cwv_results: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Génère des recommandations pour améliorer les Core Web Vitals
        
        Args:
            cwv_results: Résultats de l'analyse des Core Web Vitals
            
        Returns:
            Recommandations par métrique
        """
        recommendations = {}
        
        if "largest_contentful_paint" in cwv_results:
            lcp = cwv_results["largest_contentful_paint"]
            if lcp["status"] != "good":
                recommendations["largest_contentful_paint"] = [
                    "Optimiser les images et ressources principales",
                    "Implémenter la mise en cache des ressources",
                    "Réduire le temps de réponse du serveur",
                    "Précharger les ressources critiques",
                    "Utiliser un CDN pour les ressources statiques"
                ]
        
        if "first_input_delay" in cwv_results:
            fid = cwv_results["first_input_delay"]
            if fid["status"] != "good":
                recommendations["first_input_delay"] = [
                    "Minimiser les scripts JavaScript tiers",
                    "Différer le chargement des scripts non critiques",
                    "Diviser les tâches JavaScript longues",
                    "Optimiser les gestionnaires d'événements",
                    "Utiliser des Web Workers pour les tâches intensives"
                ]
        
        if "cumulative_layout_shift" in cwv_results:
            cls = cwv_results["cumulative_layout_shift"]
            if cls["status"] != "good":
                recommendations["cumulative_layout_shift"] = [
                    "Spécifier les dimensions des images et médias",
                    "Réserver de l'espace pour les éléments dynamiques",
                    "Éviter d'insérer du contenu au-dessus du contenu existant",
                    "Préférer les transformations pour les animations",
                    "Optimiser le chargement des polices de caractères"
                ]
        
        return recommendations