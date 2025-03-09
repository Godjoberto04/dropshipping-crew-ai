from langchain.tools import BaseTool
from typing import Dict, List, Any
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebScrapingTool(BaseTool):
    """Outil pour scraper des sites web de e-commerce de manière respectueuse"""
    
    name = "WebScrapingTool"
    description = "Extrait des données de produits à partir d'URLs e-commerce"
    
    def __init__(self):
        super().__init__()
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
    
    def _run(self, url: str, selectors: Dict[str, str] = None) -> List[Dict]:
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
        
        # Configuration des headers pour un scraping respectueux
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://www.google.com/',
            'DNT': '1'  # Do Not Track
        }
        
        try:
            logger.info(f"Tentative de scraping de {url}")
            
            # Ajouter un délai aléatoire pour éviter la détection
            time.sleep(random.uniform(1, 3))
            
            # Enregistrer cette requête
            self._add_request_timestamp()
            
            # Effectuer la requête avec timeout plus long pour les sites lents
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Page récupérée avec succès: {response.status_code}")
            
            # Parser le HTML avec lxml parser (plus rapide)
            soup = BeautifulSoup(response.text, 'lxml')
            results = []
            
            # Traiter chaque sélecteur de conteneur de produit séparément
            product_container_selectors = selectors.get('product_container', 'div.product').split(',')
            product_containers = []
            
            for container_selector in product_container_selectors:
                containers = soup.select(container_selector.strip())
                if containers:
                    product_containers.extend(containers)
                    
            logger.info(f"Nombre de produits trouvés: {len(product_containers)}")
            
            # Si aucun produit n'est trouvé avec les sélecteurs spécifiques, utiliser une approche générique
            if not product_containers:
                logger.warning("Aucun produit trouvé avec les sélecteurs spécifiques, tentative d'extraction générique")
                # Chercher des éléments qui semblent être des produits (contient prix et nom)
                potential_products = soup.find_all(['div', 'li', 'article'], class_=lambda c: c and ('product' in c.lower() or 'item' in c.lower()))
                product_containers = potential_products
                logger.info(f"Extraction générique: {len(product_containers)} produits potentiels trouvés")
            
            # Traiter chaque conteneur de produit
            for container in product_containers:
                product_data = {}
                
                # Extraire chaque élément demandé en essayant différents sélecteurs
                for field, selector_str in selectors.items():
                    if field == 'product_container':
                        continue
                    
                    # Essayer chaque sélecteur alternativement
                    field_selectors = selector_str.split(',')
                    element = None
                    
                    for field_selector in field_selectors:
                        element = container.select_one(field_selector.strip())
                        if element:
                            break
                    
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
                        # Essayer des techniques alternatives pour trouver des champs communs
                        if field == 'name':
                            # Chercher le premier h1, h2, h3 ou élément avec 'title' dans sa classe
                            name_elem = container.find(['h1', 'h2', 'h3'], class_=lambda c: c and 'title' in c.lower())
                            if name_elem:
                                product_data[field] = name_elem.text.strip()
                            else:
                                product_data[field] = None
                        elif field == 'price':
                            # Chercher tout élément avec 'price' dans sa classe ou son texte
                            price_elem = container.find(class_=lambda c: c and 'price' in c.lower())
                            if price_elem:
                                product_data[field] = self._clean_price(price_elem.text.strip())
                            else:
                                # Chercher tout élément contenant un symbole de devise
                                currency_text = container.find(text=lambda t: t and ('$' in t or '€' in t or '£' in t))
                                if currency_text:
                                    product_data[field] = self._clean_price(currency_text.strip())
                                else:
                                    product_data[field] = None
                        else:
                            product_data[field] = None
                
                # S'assurer qu'il y a au moins un nom et un prix
                if product_data.get('name') and product_data.get('price'):
                    results.append(product_data)
            
            logger.info(f"Scraping terminé: {len(results)} produits extraits")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la requête HTTP: {str(e)}")
            return [{"error": f"Erreur HTTP: {str(e)}"}]
        except Exception as e:
            logger.error(f"Erreur lors du scraping: {str(e)}")
            return [{"error": str(e)}]
    
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


class ProductAnalysisTool(BaseTool):
    """Outil pour analyser les produits extraits et identifier les opportunités"""
    
    name = "ProductAnalysisTool"
    description = "Analyse les produits pour identifier les opportunités de dropshipping"
    
    def _run(self, products: List[Dict], min_margin_percent: float = 30.0, shipping_cost: float = 5.0) -> Dict[str, Any]:
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
