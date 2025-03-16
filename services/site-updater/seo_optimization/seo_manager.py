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
