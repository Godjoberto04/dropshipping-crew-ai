from crewai import Tool
from typing import Dict, List, Any
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import logging
import asyncio
from playwright.async_api import async_playwright

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebScrapingTool(Tool):
    """Outil pour scraper des sites web de e-commerce de manière respectueuse"""
    
    def __init__(self):
        super().__init__(
            name="WebScrapingTool",
            description="Extrait des données de produits à partir d'URLs e-commerce",
            func=self.scrape_website
        )
        # Limiter le nombre de requêtes
        self.max_requests_per_hour = int(os.getenv('MAX_SCRAPING_REQUESTS_PER_HOUR', 100))
        self.request_timestamps = []
    
    def _is_rate_limited(self):
        """Vérifie si nous avons atteint la limite de requêtes par heure"""
        current_time = time.time()
        # Supprimer les timestamps plus anciens qu'une heure
        self.request_timestamps = [ts for ts in self.request_timestamps if current_time - ts < 3600]
        # Vérifier si nous avons atteint la limite
        return len(self.request_timestamps) >= self.max_requests_per_hour
    
    def _add_request_timestamp(self):
        """Ajoute un timestamp pour une nouvelle requête"""
        self.request_timestamps.append(time.time())
    
    def scrape_website(self, url: str, selectors: Dict[str, str] = None) -> List[Dict]:
        """
        Scrape un site e-commerce avec des sélecteurs CSS spécifiques
        
        Args:
            url: URL du site à scraper
            selectors: Dictionnaire de sélecteurs CSS (nom_champ: sélecteur)
            
        Returns:
            Liste de dictionnaires contenant les données extraites
        """
        # Vérifier la limite de requêtes
        if self._is_rate_limited():
            logger.warning(f"Rate limit atteint: {self.max_requests_per_hour} requêtes par heure")
            return [{"error": f"Rate limit atteint: {self.max_requests_per_hour} requêtes par heure"}]
        
        # Utiliser des sélecteurs par défaut si non spécifiés
        if not selectors:
            selectors = {
                "product_container": "div.product,li.product,div.product-item",
                "name": "h2.product-title,h3.product-name,div.product-title",
                "price": "span.price,div.price,p.price",
                "rating": "div.rating,span.stars,div.star-rating",
                "image": "img.product-image,img.main-image,img"
            }
        
        try:
            logger.info(f"Tentative de scraping de {url}")
            
            # Ajouter un délai aléatoire pour éviter la détection
            time.sleep(random.uniform(1, 3))
            
            # Enregistrer cette requête
            self._add_request_timestamp()
            
            # Exécuter le scraping avec Playwright de manière asynchrone
            results = asyncio.run(self._async_scrape_with_playwright(url, selectors))
            
            logger.info(f"Scraping terminé: {len(results)} produits extraits")
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors du scraping: {str(e)}")
            return [{"error": str(e)}]
    
    async def _async_scrape_with_playwright(self, url: str, selectors: Dict[str, str]) -> List[Dict]:
        """
        Exécute le scraping avec Playwright de manière asynchrone
        
        Args:
            url: URL du site à scraper
            selectors: Dictionnaire de sélecteurs CSS
            
        Returns:
            Liste de dictionnaires contenant les données extraites
        """
        results = []
        
        async with async_playwright() as p:
            # Lancer un navigateur
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Configuration des headers pour simuler un navigateur réel
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'DNT': '1'  # Do Not Track
            })
            
            # Naviguer vers l'URL
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception as e:
                logger.warning(f"Timeout lors du chargement de la page, continuant avec le contenu disponible: {str(e)}")
                
            # Attendre que le contenu soit chargé
            await page.wait_for_load_state("domcontentloaded")
            
            # Récupérer le contenu HTML
            content = await page.content()
            
            # Utiliser BeautifulSoup pour parser le HTML (plus facile pour extraire les données)
            soup = BeautifulSoup(content, 'html.parser')
            
            # Trouver tous les conteneurs de produits
            product_containers = soup.select(selectors.get('product_container', 'div.product'))
            logger.info(f"Nombre de produits trouvés: {len(product_containers)}")
            
            for container in product_containers:
                product_data = {}
                
                # Extraire chaque élément demandé
                for field, selector in selectors.items():
                    if field == 'product_container':
                        continue
                        
                    element = container.select_one(selector)
                    if element:
                        if field == 'price':
                            # Nettoyer le prix (supprimer symboles de devise, etc.)
                            price_text = element.text.strip()
                            product_data[field] = self._clean_price(price_text)
                        elif field == 'image' and element.get('src'):
                            product_data[field] = element.get('src')
                        else:
                            product_data[field] = element.text.strip()
                    else:
                        product_data[field] = None
                
                if product_data:
                    results.append(product_data)
            
            # Fermer le navigateur
            await browser.close()
        
        return results
    
    def _clean_price(self, price_text: str) -> float:
        """Nettoie une chaîne de prix et la convertit en nombre"""
        try:
            # Supprimer tous les caractères non numériques sauf le point décimal
            digits_only = ''.join(c for c in price_text if c.isdigit() or c == '.')
            
            # Gestion des formats avec virgule comme séparateur décimal
            if '.' not in digits_only and ',' in price_text:
                digits_only = ''.join(c for c in price_text if c.isdigit() or c == ',')
                digits_only = digits_only.replace(',', '.')
                
            # Convertir en float
            return float(digits_only)
        except ValueError:
            logger.warning(f"Impossible de convertir le prix: {price_text}")
            return 0.0


class ProductAnalysisTool(Tool):
    """Outil pour analyser les produits extraits et identifier les opportunités"""
    
    def __init__(self):
        super().__init__(
            name="ProductAnalysisTool",
            description="Analyse les produits pour identifier les opportunités de dropshipping",
            func=self.analyze_products
        )
    
    def analyze_products(self, products: List[Dict], 
                         min_margin_percent: float = 30.0, 
                         shipping_cost: float = 5.0) -> Dict[str, Any]:
        """
        Analyse une liste de produits pour identifier les meilleures opportunités
        
        Args:
            products: Liste de produits extraits
            min_margin_percent: Marge minimale souhaitée (en pourcentage)
            shipping_cost: Coût d'expédition moyen
            
        Returns:
            Dictionnaire contenant l'analyse
        """
        if not products:
            return {"error": "Aucun produit à analyser"}
        
        logger.info(f"Analyse de {len(products)} produits")
        
        # Convertir en DataFrame pour faciliter l'analyse
        df = pd.DataFrame(products)
        
        # S'assurer que le prix est numérique
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
        else:
            return {"error": "Les données de produits ne contiennent pas de prix"}
        
        # Ajouter un prix fournisseur estimé (50% du prix de vente moins frais d'expédition)
        df['estimated_supplier_price'] = (df['price'] * 0.5) - shipping_cost
        df['estimated_supplier_price'] = df['estimated_supplier_price'].apply(lambda x: max(x, 1.0))
        
        # Calculer le prix recommandé pour atteindre la marge minimale
        df['recommended_price'] = df['estimated_supplier_price'] * (1 + min_margin_percent/100)
        
        # Calculer la marge potentielle en pourcentage
        df['potential_margin_percent'] = ((df['price'] - df['estimated_supplier_price']) / df['price']) * 100
        
        # Filtrer les produits avec une marge potentielle suffisante
        profitable_products = df[df['potential_margin_percent'] >= min_margin_percent].copy()
        
        # Si aucun produit n'a une marge suffisante, prendre les 5 meilleurs
        if len(profitable_products) == 0:
            profitable_products = df.nlargest(5, 'potential_margin_percent')
        
        # Ajouter un score basé sur la marge
        profitable_products['margin_score'] = profitable_products['potential_margin_percent'] / 100 * 10
        profitable_products['margin_score'] = profitable_products['margin_score'].clip(0, 10)
        
        # Préparer les résultats
        results = []
        for _, product in profitable_products.iterrows():
            product_result = {
                "name": product.get('name', 'Produit inconnu'),
                "supplier_price": round(product['estimated_supplier_price'], 2),
                "market_price": round(product['price'], 2),
                "recommended_price": round(product['recommended_price'], 2),
                "potential_margin_percent": round(product['potential_margin_percent'], 1),
                "margin_score": round(product['margin_score'], 1)
            }
            
            # Ajouter l'image si disponible
            if 'image' in product and product['image']:
                product_result['image_url'] = product['image']
            
            results.append(product_result)
        
        # Trier par score de marge
        results = sorted(results, key=lambda x: x['margin_score'], reverse=True)
        
        logger.info(f"Analyse terminée: {len(results)} produits profitables identifiés")
        
        return {
            "analyzed_count": len(products),
            "profitable_count": len(results),
            "average_margin": round(profitable_products['potential_margin_percent'].mean(), 1),
            "products": results[:10]  # Limiter aux 10 meilleurs produits
        }
