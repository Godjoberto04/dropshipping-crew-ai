#!/usr/bin/env python3
"""
Utilitaires pour l'optimisation SEO.
"""

import json
import time
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union

from config import settings, get_logger

logger = get_logger("seo_utils")

class SEOUtils:
    """
    Classe d'utilitaires pour l'optimisation SEO.
    """
    
    @staticmethod
    async def generate_structured_data(page_type: str, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère un schéma de données structurées (JSON-LD) pour une page.
        
        Args:
            page_type: Type de page (product, collection, page, blog)
            page_data: Données spécifiques à la page
            
        Returns:
            Objet de données structurées au format JSON-LD
        """
        # Simulation d'appel API, dans une implémentation réelle 
        # cette méthode interrogerait des sources de données réelles
        await asyncio.sleep(0.2)
        
        # Structure de base
        base_structure = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "url": page_data.get("url", ""),
            "name": page_data.get("title", ""),
            "description": page_data.get("description", ""),
            "inLanguage": "fr-FR"
        }
        
        # Compléter selon le type de page
        if page_type == "product":
            product_data = {
                "@type": "Product",
                "name": page_data.get("title", ""),
                "description": page_data.get("description", ""),
                "image": page_data.get("images", []),
                "sku": page_data.get("sku", ""),
                "brand": {
                    "@type": "Brand",
                    "name": page_data.get("brand", "")
                },
                "offers": {
                    "@type": "Offer",
                    "price": page_data.get("price", 0),
                    "priceCurrency": "EUR",
                    "availability": "https://schema.org/InStock" if page_data.get("in_stock", True) else "https://schema.org/OutOfStock",
                    "url": page_data.get("url", "")
                }
            }
            return product_data
            
        elif page_type == "collection":
            collection_data = {
                "@type": "CollectionPage",
                "name": page_data.get("title", ""),
                "description": page_data.get("description", ""),
                "url": page_data.get("url", "")
            }
            return {**base_structure, **collection_data}
            
        elif page_type == "blog":
            blog_data = {
                "@type": "BlogPosting",
                "headline": page_data.get("title", ""),
                "datePublished": page_data.get("published_date", ""),
                "dateModified": page_data.get("modified_date", ""),
                "author": {
                    "@type": "Person",
                    "name": page_data.get("author", "")
                },
                "image": page_data.get("featured_image", ""),
                "articleBody": page_data.get("content", "")
            }
            return {**base_structure, **blog_data}
        
        # Pour les autres types de pages
        return base_structure
    
    @staticmethod
    async def extract_keywords_from_page(url: str, title: str, content: str) -> List[str]:
        """
        Extrait automatiquement les mots-clés pertinents d'une page.
        
        Args:
            url: URL de la page
            title: Titre de la page
            content: Contenu textuel de la page
            
        Returns:
            Liste des mots-clés extraits
        """
        # Simulation d'analyse
        await asyncio.sleep(0.3)
        
        # Dans une implémentation réelle, cette fonction utiliserait une analyse TF-IDF
        # ou une autre technique d'extraction de mots-clés
        
        # Extraction simplifiée basée sur le titre et l'URL
        url_parts = url.split("/")
        url_keywords = []
        for part in url_parts:
            if part and not part.startswith("http") and not "." in part:
                # Traiter les parties de l'URL qui pourraient contenir des mots-clés
                part = part.replace("-", " ").replace("_", " ")
                words = part.split()
                for word in words:
                    if len(word) > 3:  # Ignorer les mots trop courts
                        url_keywords.append(word.lower())
        
        title_words = title.lower().split()
        title_keywords = [word for word in title_words if len(word) > 3]
        
        # Simuler quelques mots-clés extraits du contenu
        if "product" in url:
            content_keywords = ["qualité", "premium", "design", "meilleur", "prix"]
        elif "collection" in url:
            content_keywords = ["collection", "série", "ensemble", "exclusif"]
        elif "blog" in url:
            content_keywords = ["conseils", "astuces", "guide", "comment", "pourquoi"]
        else:
            content_keywords = ["boutique", "magasin", "acheter", "vente"]
        
        # Combiner et dédupliquer
        all_keywords = list(set(url_keywords + title_keywords + content_keywords))
        
        # Prioriser et limiter
        return all_keywords[:10]  # Limiter à 10 mots-clés
    
    @staticmethod
    def format_seo_report(analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Formate un rapport SEO à partir des résultats d'analyse.
        
        Args:
            analysis_results: Liste des résultats d'analyse SEO
            
        Returns:
            Rapport SEO formaté
        """
        # Calculer des statistiques
        total_pages = len(analysis_results)
        if total_pages == 0:
            return {
                "timestamp": time.time(),
                "total_pages": 0,
                "message": "Aucune page analysée"
            }
        
        # Scores moyens
        avg_overall = sum(r.get("seo_scores", {}).get("overall", 0) for r in analysis_results) / total_pages
        avg_meta = sum(r.get("seo_scores", {}).get("meta", 0) for r in analysis_results) / total_pages
        avg_content = sum(r.get("seo_scores", {}).get("content", 0) for r in analysis_results) / total_pages
        avg_links = sum(r.get("seo_scores", {}).get("links", 0) for r in analysis_results) / total_pages
        avg_images = sum(r.get("seo_scores", {}).get("images", 0) for r in analysis_results) / total_pages
        
        # Identifier les problèmes communs
        common_issues = {}
        all_recommendations = []
        
        for result in analysis_results:
            recommendations = result.get("recommendations", [])
            all_recommendations.extend(recommendations)
            
            for rec in recommendations:
                issue_key = f"{rec.get('category')}:{rec.get('issue')}"
                if issue_key in common_issues:
                    common_issues[issue_key]["count"] += 1
                    common_issues[issue_key]["pages"].append(result.get("url"))
                else:
                    common_issues[issue_key] = {
                        "category": rec.get("category"),
                        "issue": rec.get("issue"),
                        "recommendation": rec.get("recommendation"),
                        "priority": rec.get("priority"),
                        "count": 1,
                        "pages": [result.get("url")]
                    }
        
        # Trier les problèmes par priorité et fréquence
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_issues = sorted(
            common_issues.values(),
            key=lambda x: (priority_order.get(x["priority"], 999), -x["count"])
        )
        
        # Identifier les pages avec les scores les plus faibles
        lowest_scoring_pages = sorted(
            [r for r in analysis_results if "url" in r and "seo_scores" in r],
            key=lambda x: x.get("seo_scores", {}).get("overall", 0)
        )[:5]  # Top 5 des pages les plus faibles
        
        # Construire le rapport
        report = {
            "timestamp": time.time(),
            "total_pages": total_pages,
            "average_scores": {
                "overall": round(avg_overall, 1),
                "meta": round(avg_meta, 1),
                "content": round(avg_content, 1),
                "links": round(avg_links, 1),
                "images": round(avg_images, 1)
            },
            "common_issues": sorted_issues[:10],  # Top 10 des problèmes
            "low_scoring_pages": [
                {
                    "url": page.get("url"),
                    "type": page.get("type", "unknown"),
                    "overall_score": page.get("seo_scores", {}).get("overall", 0),
                    "issues": len([r for r in page.get("recommendations", []) if r.get("priority") == "high"])
                }
                for page in lowest_scoring_pages
            ],
            "optimization_opportunities": len(all_recommendations),
            "priority_distribution": {
                "high": len([r for r in all_recommendations if r.get("priority") == "high"]),
                "medium": len([r for r in all_recommendations if r.get("priority") == "medium"]),
                "low": len([r for r in all_recommendations if r.get("priority") == "low"])
            }
        }
        
        return report
