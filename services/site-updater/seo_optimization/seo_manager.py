#!/usr/bin/env python3
"""
Module pour l'optimisation SEO continue du site e-commerce.
"""

import asyncio
import json
import time
import re
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from urllib.parse import urlparse, urljoin
import aiohttp
from bs4 import BeautifulSoup

from config import settings, get_logger

logger = get_logger("seo_optimization_manager")

class SEOOptimizationManager:
    """
    Classe pour analyser et optimiser les aspects SEO du site e-commerce.
    Permet d'améliorer le référencement en optimisant les meta données,
    la structure de contenu, les URLs et le contenu textuel.
    """
    
    def __init__(self):
        """Initialise le gestionnaire d'optimisation SEO."""
        self.session = None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]
        self.current_user_agent_index = 0
        
        # Limites pour éviter d'être bloqué
        self.request_delay = 1.0  # secondes entre chaque requête
        
        # Scores recommandés pour différents éléments SEO
        self.recommended_scores = {
            "title_length": {"min": 30, "max": 60},  # Caractères
            "meta_description_length": {"min": 70, "max": 160},  # Caractères
            "h1_count": {"min": 1, "max": 1},  # Un seul H1 par page
            "keyword_density": {"min": 0.5, "max": 2.5},  # Pourcentage
            "internal_links": {"min": 2, "max": 100},  # Nombre de liens internes
            "img_alt_ratio": {"min": 80, "max": 100},  # Pourcentage d'images avec alt
            "content_length": {"min": 300, "max": 10000},  # Nombre de mots
        }
        
        logger.info("Gestionnaire d'optimisation SEO initialisé")
    
    def _create_session(self):
        """Crée une nouvelle session HTTP."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "User-Agent": self._get_next_user_agent(),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Cache-Control": "max-age=0"
                }
            )
    
    def _get_next_user_agent(self) -> str:
        """Retourne le prochain user agent dans la rotation."""
        user_agent = self.user_agents[self.current_user_agent_index]
        self.current_user_agent_index = (self.current_user_agent_index + 1) % len(self.user_agents)
        return user_agent
    
    async def _close_session(self):
        """Ferme la session HTTP."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _fetch_page(self, url: str) -> Optional[str]:
        """
        Récupère le contenu d'une page web.
        
        Args:
            url: URL de la page à récupérer
            
        Returns:
            Contenu HTML de la page ou None en cas d'erreur
        """
        # Pause pour respecter le délai entre requêtes
        await asyncio.sleep(self.request_delay)
        
        try:
            self._create_session()
            async with self.session.get(url, ssl=False) as response:
                if response.status != 200:
                    logger.warning(f"Erreur lors de la récupération de {url}: {response.status}")
                    return None
                return await response.text()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de {url}: {str(e)}")
            return None
    
    async def analyze_page_seo(self, url: str, target_keywords: List[str] = None) -> Dict[str, Any]:
        """
        Analyse les aspects SEO d'une page.
        
        Args:
            url: URL de la page à analyser
            target_keywords: Liste des mots-clés cibles pour cette page
            
        Returns:
            Résultats de l'analyse SEO
        """
        html = await self._fetch_page(url)
        if html is None:
            return {
                "url": url,
                "status": "error",
                "message": "Impossible de récupérer la page",
                "timestamp": time.time()
            }
        
        # Analyser le HTML
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extraire les informations de base
            title = soup.title.string.strip() if soup.title else ""
            
            # Meta description
            meta_description = ""
            meta_desc_tag = soup.find("meta", attrs={"name": "description"})
            if meta_desc_tag and meta_desc_tag.get("content"):
                meta_description = meta_desc_tag["content"].strip()
            
            # Extraire les titres (h1, h2, h3)
            h1_tags = soup.find_all("h1")
            h2_tags = soup.find_all("h2")
            h3_tags = soup.find_all("h3")
            
            # Extraire le contenu textuel principal
            # Supprimer les scripts, styles, et autres balises non pertinentes
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()
            
            text_content = soup.get_text(separator=" ", strip=True)
            words = [word for word in re.findall(r'\b\w+\b', text_content.lower()) if len(word) > 1]
            word_count = len(words)
            
            # Calculer la densité des mots-clés
            keyword_density = {}
            if target_keywords:
                for keyword in target_keywords:
                    keyword_lower = keyword.lower()
                    keyword_count = sum(1 for word in words if word == keyword_lower)
                    keyword_density[keyword] = (keyword_count / word_count * 100) if word_count > 0 else 0
            
            # Analyser les images
            images = soup.find_all("img")
            images_with_alt = [img for img in images if img.get("alt")]
            
            # Analyser les liens
            all_links = soup.find_all("a", href=True)
            internal_links = []
            external_links = []
            
            base_domain = urlparse(url).netloc
            for link in all_links:
                href = link["href"]
                if href.startswith("#") or href.startswith("javascript:"):
                    continue
                
                full_url = urljoin(url, href)
                parsed_url = urlparse(full_url)
                
                if parsed_url.netloc == base_domain or not parsed_url.netloc:
                    internal_links.append({
                        "url": full_url,
                        "text": link.get_text(strip=True),
                        "nofollow": "rel" in link.attrs and "nofollow" in link["rel"]
                    })
                else:
                    external_links.append({
                        "url": full_url,
                        "text": link.get_text(strip=True),
                        "nofollow": "rel" in link.attrs and "nofollow" in link["rel"]
                    })
            
            # Extraire les données structurées (JSON-LD)
            structured_data = []
            json_ld_tags = soup.find_all("script", type="application/ld+json")
            for tag in json_ld_tags:
                try:
                    data = json.loads(tag.string)
                    structured_data.append(data)
                except (json.JSONDecodeError, TypeError):
                    pass
            
            # Calculer les scores SEO
            seo_scores = self._calculate_seo_scores({
                "title_length": len(title),
                "meta_description_length": len(meta_description),
                "h1_count": len(h1_tags),
                "keyword_density": max(keyword_density.values()) if keyword_density else 0,
                "internal_links": len(internal_links),
                "img_alt_ratio": (len(images_with_alt) / len(images) * 100) if images else 100,
                "content_length": word_count,
            })
            
            # Préparer les résultats
            results = {
                "url": url,
                "status": "success",
                "timestamp": time.time(),
                "basic_info": {
                    "title": title,
                    "title_length": len(title),
                    "meta_description": meta_description,
                    "meta_description_length": len(meta_description)
                },
                "content_analysis": {
                    "word_count": word_count,
                    "h1_tags": [h1.get_text(strip=True) for h1 in h1_tags],
                    "h2_tags": [h2.get_text(strip=True) for h2 in h2_tags],
                    "h3_tags": [h3.get_text(strip=True) for h3 in h3_tags]
                },
                "keyword_analysis": {
                    "target_keywords": target_keywords,
                    "keyword_density": keyword_density
                },
                "link_analysis": {
                    "internal_links_count": len(internal_links),
                    "external_links_count": len(external_links),
                    "internal_links": internal_links[:10],  # Limiter pour éviter des résultats trop volumineux
                    "external_links": external_links[:10]
                },
                "image_analysis": {
                    "total_images": len(images),
                    "images_with_alt": len(images_with_alt),
                    "alt_text_ratio": (len(images_with_alt) / len(images) * 100) if images else 100
                },
                "structured_data": {
                    "count": len(structured_data),
                    "types": [self._get_schema_type(data) for data in structured_data]
                },
                "seo_scores": seo_scores
            }
            
            # Générer des recommandations
            recommendations = self._generate_recommendations(results)
            results["recommendations"] = recommendations
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse SEO de {url}: {str(e)}")
            return {
                "url": url,
                "status": "error",
                "message": f"Erreur lors de l'analyse: {str(e)}",
                "timestamp": time.time()
            }
        finally:
            await self._close_session()
    
    def _calculate_seo_scores(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule les scores SEO pour chaque métrique.
        
        Args:
            metrics: Dictionnaire des métriques mesurées
            
        Returns:
            Scores SEO calculés
        """
        scores = {}
        
        for metric, value in metrics.items():
            if metric in self.recommended_scores:
                rec = self.recommended_scores[metric]
                
                # Pour les métriques où une valeur entre min et max est idéale
                if "min" in rec and "max" in rec:
                    if value < rec["min"]:
                        # Trop bas
                        score = (value / rec["min"]) * 100
                    elif value > rec["max"]:
                        # Trop élevé
                        if metric in ["h1_count"]:  # Métriques où l'excès est mauvais
                            score = max(0, 100 - ((value - rec["max"]) * 25))  # Pénalité pour excès
                        else:
                            score = 100  # Pour des métriques comme content_length, l'excès n'est pas pénalisé
                    else:
                        # Dans la plage idéale
                        score = 100
                else:
                    # Métriques simples
                    score = value
                
                scores[metric] = min(100, max(0, score))
        
        # Score global (moyenne pondérée)
        weights = {
            "title_length": 1.5,
            "meta_description_length": 1.5,
            "h1_count": 1.0,
            "keyword_density": 2.0,
            "internal_links": 1.0,
            "img_alt_ratio": 1.0,
            "content_length": 2.0
        }
        
        total_weight = sum(weights.get(metric, 1.0) for metric in scores.keys())
        weighted_score = sum(score * weights.get(metric, 1.0) for metric, score in scores.items())
        overall_score = weighted_score / total_weight if total_weight > 0 else 0
        
        scores["overall"] = min(100, max(0, overall_score))
        return scores
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Génère des recommandations SEO basées sur l'analyse.
        
        Args:
            analysis: Résultats de l'analyse SEO
            
        Returns:
            Liste de recommandations
        """
        recommendations = []
        
        # Titre
        title_length = analysis["basic_info"]["title_length"]
        if title_length < self.recommended_scores["title_length"]["min"]:
            recommendations.append({
                "priority": "high",
                "category": "meta",
                "issue": "Titre trop court",
                "recommendation": f"Allongez le titre à au moins {self.recommended_scores['title_length']['min']} caractères pour améliorer son impact SEO."
            })
        elif title_length > self.recommended_scores["title_length"]["max"]:
            recommendations.append({
                "priority": "medium",
                "category": "meta",
                "issue": "Titre trop long",
                "recommendation": f"Raccourcissez le titre à maximum {self.recommended_scores['title_length']['max']} caractères pour éviter qu'il soit tronqué dans les résultats de recherche."
            })
        
        # Meta description
        meta_description_length = analysis["basic_info"]["meta_description_length"]
        if meta_description_length < self.recommended_scores["meta_description_length"]["min"]:
            recommendations.append({
                "priority": "high",
                "category": "meta",
                "issue": "Meta description trop courte",
                "recommendation": f"Allongez la meta description à au moins {self.recommended_scores['meta_description_length']['min']} caractères pour améliorer son impact dans les résultats de recherche."
            })
        elif meta_description_length > self.recommended_scores["meta_description_length"]["max"]:
            recommendations.append({
                "priority": "medium",
                "category": "meta",
                "issue": "Meta description trop longue",
                "recommendation": f"Raccourcissez la meta description à maximum {self.recommended_scores['meta_description_length']['max']} caractères pour éviter qu'elle soit tronquée."
            })
        elif meta_description_length == 0:
            recommendations.append({
                "priority": "high",
                "category": "meta",
                "issue": "Meta description manquante",
                "recommendation": "Ajoutez une meta description qui résume de façon attrayante le contenu de la page."
            })
        
        # H1
        h1_count = len(analysis["content_analysis"]["h1_tags"])
        if h1_count == 0:
            recommendations.append({
                "priority": "high",
                "category": "headings",
                "issue": "H1 manquant",
                "recommendation": "Ajoutez une balise H1 qui définit clairement le sujet principal de la page."
            })
        elif h1_count > 1:
            recommendations.append({
                "priority": "medium",
                "category": "headings",
                "issue": "Trop de balises H1",
                "recommendation": "Limitez-vous à une seule balise H1 par page pour une meilleure structure SEO."
            })
        
        # Contenu
        word_count = analysis["content_analysis"]["word_count"]
        if word_count < self.recommended_scores["content_length"]["min"]:
            recommendations.append({
                "priority": "high",
                "category": "content",
                "issue": "Contenu trop court",
                "recommendation": f"Enrichissez le contenu pour atteindre au moins {self.recommended_scores['content_length']['min']} mots pour améliorer la pertinence SEO."
            })
        
        # Densité de mots-clés
        keyword_densities = analysis["keyword_analysis"]["keyword_density"]
        for keyword, density in keyword_densities.items():
            if density < self.recommended_scores["keyword_density"]["min"]:
                recommendations.append({
                    "priority": "medium",
                    "category": "keywords",
                    "issue": f"Densité faible pour '{keyword}'",
                    "recommendation": f"Augmentez la fréquence du mot-clé '{keyword}' dans le contenu pour atteindre une densité d'au moins {self.recommended_scores['keyword_density']['min']}%."
                })
            elif density > self.recommended_scores["keyword_density"]["max"]:
                recommendations.append({
                    "priority": "medium",
                    "category": "keywords",
                    "issue": f"Densité excessive pour '{keyword}'",
                    "recommendation": f"Réduisez la fréquence du mot-clé '{keyword}' pour éviter le bourrage de mots-clés."
                })
        
        # Images alt
        images_total = analysis["image_analysis"]["total_images"]
        alt_ratio = analysis["image_analysis"]["alt_text_ratio"]
        if images_total > 0 and alt_ratio < 100:
            recommendations.append({
                "priority": "medium",
                "category": "images",
                "issue": "Images sans attribut alt",
                "recommendation": "Ajoutez des attributs alt descriptifs à toutes les images pour améliorer l'accessibilité et le SEO."
            })
        
        # Liens internes
        internal_links_count = analysis["link_analysis"]["internal_links_count"]
        if internal_links_count < self.recommended_scores["internal_links"]["min"]:
            recommendations.append({
                "priority": "medium",
                "category": "links",
                "issue": "Peu de liens internes",
                "recommendation": "Ajoutez plus de liens internes pour améliorer la navigation et la distribution du PageRank."
            })
        
        # Données structurées
        if analysis["structured_data"]["count"] == 0:
            recommendations.append({
                "priority": "low",
                "category": "structured_data",
                "issue": "Absence de données structurées",
                "recommendation": "Ajoutez des données structurées (JSON-LD) pour améliorer l'affichage dans les résultats de recherche."
            })
        
        return recommendations
    
    def _get_schema_type(self, schema_data: Dict[str, Any]) -> str:
        """
        Extrait le type d'un schéma JSON-LD.
        
        Args:
            schema_data: Données du schéma
            
        Returns:
            Type du schéma
        """
        if isinstance(schema_data, dict):
            return schema_data.get("@type", "Unknown")
        return "Unknown"
    
    async def generate_optimized_meta(self, page_url: str, content: str, keywords: List[str]) -> Dict[str, str]:
        """
        Génère des balises meta optimisées pour une page.
        
        Args:
            page_url: URL de la page
            content: Contenu principal de la page
            keywords: Mots-clés cibles
            
        Returns:
            Balises meta optimisées
        """
        # Dans une implémentation réelle, cette fonction pourrait utiliser l'API Claude
        # pour générer des méta-données optimisées en fonction du contenu et des mots-clés
        
        # Simuler un délai pour l'appel à l'API
        await asyncio.sleep(0.5)
        
        # Exemple de génération simplifiée
        keywords_str = ", ".join(keywords)
        title = f"Découvrez nos {keywords[0]} de qualité | {' '.join(keywords[:2]).capitalize()}"
        
        # Limiter la longueur du titre
        if len(title) > self.recommended_scores["title_length"]["max"]:
            title = title[:self.recommended_scores["title_length"]["max"] - 3] + "..."
        
        # Générer la meta description
        description = f"Explorez notre sélection de {keywords[0]} de haute qualité. Trouvez les meilleurs {' et '.join(keywords[:2])} pour répondre à vos besoins."
        
        # Limiter la longueur de la description
        if len(description) > self.recommended_scores["meta_description_length"]["max"]:
            description = description[:self.recommended_scores["meta_description_length"]["max"] - 3] + "..."
        
        return {
            "title": title,
            "meta_description": description,
            "meta_keywords": keywords_str
        }
