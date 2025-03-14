#!/usr/bin/env python3
"""
Système de sélection automatique du fournisseur optimal
Fait partie du projet Dropshipping Crew AI
"""

import asyncio
from typing import Dict, Any, List, Tuple, Optional
from loguru import logger

from models import SupplierType
from .communicator import SupplierCommunicator


class SupplierSelector:
    """
    Système de sélection du fournisseur optimal pour une commande donnée.
    
    Cette classe utilise les APIs des différents fournisseurs pour déterminer
    le meilleur fournisseur pour un produit donné, en fonction de critères
    tels que le prix, le délai d'expédition, la disponibilité, etc.
    """
    
    def __init__(self, communicator: SupplierCommunicator):
        """
        Initialise le sélecteur de fournisseur.
        
        Args:
            communicator: Communicateur avec les fournisseurs
        """
        self.communicator = communicator
        
        # Configuration des pondérations pour les critères de sélection
        self.weights = {
            "price": 0.35,          # Prix du produit
            "shipping_cost": 0.20,  # Coût d'expédition
            "delivery_time": 0.15,  # Temps de livraison estimé
            "stock": 0.10,          # Disponibilité en stock
            "seller_rating": 0.10,  # Notation du vendeur
            "reliability": 0.10     # Fiabilité du fournisseur (historique de performance)
        }
        
        # Fiabilité relative des fournisseurs (basée sur l'expérience)
        self.supplier_reliability = {
            SupplierType.ALIEXPRESS: 0.85,
            SupplierType.CJ_DROPSHIPPING: 0.90
        }
    
    async def select_optimal_supplier(self, product_id: str, variant_id: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Sélectionne le fournisseur optimal pour un produit donné.
        
        Args:
            product_id: Identifiant du produit
            variant_id: Identifiant de la variante (optionnel)
            
        Returns:
            Tuple contenant le type de fournisseur sélectionné et les détails du produit
        """
        logger.info(f"Recherche du fournisseur optimal pour le produit {product_id}, variante {variant_id}")
        
        # Liste des fournisseurs à comparer
        suppliers = [SupplierType.ALIEXPRESS, SupplierType.CJ_DROPSHIPPING]
        
        # Récupération des détails du produit chez chaque fournisseur
        product_details = {}
        tasks = []
        
        for supplier in suppliers:
            tasks.append(self.communicator.get_product_details(supplier, product_id))
        
        # Exécution des requêtes en parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traitement des résultats
        for i, result in enumerate(results):
            supplier = suppliers[i]
            
            # Gestion des erreurs
            if isinstance(result, Exception):
                logger.warning(f"Erreur lors de la récupération des détails du produit chez {supplier}: {str(result)}")
                continue
                
            # Si la requête a réussi mais le produit n'est pas disponible
            if not result.get("success", False):
                logger.warning(f"Produit non disponible chez {supplier}: {result.get('error', 'Erreur inconnue')}")
                continue
                
            # Stockage des détails du produit
            product_details[supplier] = result
        
        # Si aucun fournisseur n'a le produit, retourner une erreur
        if not product_details:
            logger.error(f"Aucun fournisseur disponible pour le produit {product_id}")
            return None, {"error": "Product not available from any supplier"}
        
        # Calcul des scores pour chaque fournisseur
        scores = {}
        
        for supplier, details in product_details.items():
            score = self._calculate_supplier_score(supplier, details, variant_id)
            scores[supplier] = score
            logger.debug(f"Score pour {supplier}: {score}")
        
        # Sélection du fournisseur avec le score le plus élevé
        best_supplier = max(scores.items(), key=lambda x: x[1])[0]
        logger.info(f"Fournisseur optimal pour le produit {product_id}: {best_supplier} avec un score de {scores[best_supplier]}")
        
        return best_supplier, product_details[best_supplier]
    
    def _calculate_supplier_score(self, supplier: str, details: Dict[str, Any], variant_id: Optional[str] = None) -> float:
        """
        Calcule un score pour un fournisseur donné, en fonction des détails du produit.
        
        Args:
            supplier: Type de fournisseur
            details: Détails du produit
            variant_id: Identifiant de la variante (optionnel)
            
        Returns:
            Score du fournisseur (0-100)
        """
        scores = {}
        
        # Score pour le prix
        if variant_id and "variations" in details:
            # Recherche du prix pour la variante spécifiée
            for variation in details.get("variations", []):
                if variation.get("id") == variant_id:
                    price = variation.get("price", 0)
                    break
            else:
                # Si la variante n'est pas trouvée, utiliser le prix minimum
                price = details.get("price", {}).get("min", 0)
        else:
            # Si pas de variante, utiliser le prix minimum
            price = details.get("price", {}).get("min", 0)
        
        # Plus le prix est bas, meilleur est le score (échelle inverse)
        # Nous normaliserons cela plus tard en comparant avec d'autres fournisseurs
        scores["price"] = price
        
        # Score pour le coût d'expédition
        shipping_methods = details.get("shipping_info", {}).get("methods", [])
        if shipping_methods:
            # Utiliser la méthode d'expédition la moins chère
            shipping_cost = min(method.get("price", 0) for method in shipping_methods)
        else:
            shipping_cost = 0
        
        scores["shipping_cost"] = shipping_cost
        
        # Score pour le délai de livraison
        if shipping_methods:
            # Extraire les délais de livraison (format habituel: "10-15 days")
            delivery_times = []
            for method in shipping_methods:
                delivery_time = method.get("delivery_time", "")
                if delivery_time:
                    try:
                        # Essayer d'extraire le délai maximum
                        parts = delivery_time.split("-")
                        if len(parts) == 2 and "days" in parts[1]:
                            max_days = int(parts[1].replace("days", "").strip())
                            delivery_times.append(max_days)
                    except (ValueError, IndexError):
                        # En cas d'erreur, ignorer cette valeur
                        pass
            
            # Utiliser le délai minimum si disponible
            delivery_time = min(delivery_times) if delivery_times else 30  # Valeur par défaut: 30 jours
        else:
            delivery_time = 30  # Valeur par défaut
        
        # Plus le délai est court, meilleur est le score (échelle inverse)
        scores["delivery_time"] = delivery_time
        
        # Score pour la disponibilité en stock
        if variant_id and "variations" in details:
            # Recherche du stock pour la variante spécifiée
            for variation in details.get("variations", []):
                if variation.get("id") == variant_id:
                    stock = variation.get("stock", 0)
                    break
            else:
                stock = 0
        else:
            # Si pas de variante, utiliser une valeur par défaut
            stock = 100  # Valeur par défaut
        
        # Un stock plus élevé est meilleur, mais avec un plafond
        stock = min(stock, 100)  # Plafonner à 100 pour normalisation
        scores["stock"] = stock
        
        # Score pour la notation du vendeur
        seller_rating = details.get("seller", {}).get("rating", 0)
        scores["seller_rating"] = seller_rating
        
        # Score pour la fiabilité du fournisseur
        scores["reliability"] = self.supplier_reliability.get(supplier, 0.5) * 100
        
        # Normalisation et calcul du score total
        return self._normalize_and_calculate_total_score(scores, supplier)
    
    def _normalize_and_calculate_total_score(self, scores: Dict[str, float], supplier: str) -> float:
        """
        Normalise les scores et calcule le score total pour un fournisseur.
        
        Args:
            scores: Dictionnaire des scores par critère
            supplier: Type de fournisseur
            
        Returns:
            Score total normalisé
        """
        # Normalisation des scores (conversion à l'échelle 0-100)
        normalized_scores = {}
        
        # Prix et coût d'expédition sont inversés (plus bas = meilleur)
        # Cela dépend du contexte des autres fournisseurs, mais nous utilisons une échelle relative
        # basée sur des valeurs typiques pour le dropshipping
        
        # Prix
        price = scores.get("price", 0)
        if price <= 0:
            normalized_scores["price"] = 0
        else:
            # Fonction inverse avec plafond à 100$ (échelle relative)
            normalized_scores["price"] = max(0, 100 - (price / 100) * 100)
        
        # Coût d'expédition
        shipping_cost = scores.get("shipping_cost", 0)
        if shipping_cost <= 0:
            normalized_scores["shipping_cost"] = 100  # Expédition gratuite
        else:
            # Fonction inverse avec plafond à 50$ (échelle relative)
            normalized_scores["shipping_cost"] = max(0, 100 - (shipping_cost / 50) * 100)
        
        # Délai de livraison
        delivery_time = scores.get("delivery_time", 30)
        # Fonction inverse avec 7 jours comme idéal et 30+ jours comme minimum
        if delivery_time <= 7:
            normalized_scores["delivery_time"] = 100
        elif delivery_time >= 30:
            normalized_scores["delivery_time"] = 0
        else:
            normalized_scores["delivery_time"] = 100 - ((delivery_time - 7) / 23) * 100
        
        # Stock (déjà normalisé entre 0-100)
        normalized_scores["stock"] = scores.get("stock", 0)
        
        # Notation du vendeur (supposée entre 0-5, normalisée à 0-100)
        seller_rating = scores.get("seller_rating", 0)
        normalized_scores["seller_rating"] = (seller_rating / 5) * 100
        
        # Fiabilité (déjà normalisée entre 0-100)
        normalized_scores["reliability"] = scores.get("reliability", 0)
        
        # Calcul du score total pondéré
        total_score = 0
        for criterion, score in normalized_scores.items():
            weight = self.weights.get(criterion, 0)
            total_score += score * weight
        
        return total_score
    
    async def find_product_across_suppliers(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Recherche un produit chez tous les fournisseurs disponibles.
        
        Args:
            query: Requête de recherche
            limit: Nombre de résultats à retourner par fournisseur
            
        Returns:
            Liste des produits trouvés, triés par pertinence
        """
        logger.info(f"Recherche de produits correspondant à '{query}' chez tous les fournisseurs")
        
        # Liste des fournisseurs à interroger
        suppliers = [SupplierType.ALIEXPRESS, SupplierType.CJ_DROPSHIPPING]
        
        # Recherche parallèle chez tous les fournisseurs
        tasks = []
        for supplier in suppliers:
            tasks.append(self.communicator.search_products(supplier, query, page=1, limit=limit))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Agrégation des résultats
        all_products = []
        
        for i, result in enumerate(results):
            supplier = suppliers[i]
            
            # Gestion des erreurs
            if isinstance(result, Exception):
                logger.warning(f"Erreur lors de la recherche chez {supplier}: {str(result)}")
                continue
                
            # Si la requête a réussi mais aucun produit n'est trouvé
            if not result.get("success", False):
                logger.warning(f"Recherche non disponible chez {supplier}: {result.get('error', 'Erreur inconnue')}")
                continue
            
            # Ajout des produits avec leur fournisseur d'origine
            products = result.get("products", [])
            for product in products:
                product["supplier"] = supplier
                all_products.append(product)
        
        # Tri des produits par pertinence (ici, nous utilisons simplement l'ordre original)
        # Dans une implémentation plus avancée, on pourrait calculer un score de pertinence
        
        return all_products
