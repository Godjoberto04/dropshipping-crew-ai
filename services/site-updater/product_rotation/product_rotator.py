#!/usr/bin/env python3
"""
Module pour gérer la rotation intelligente des produits mis en avant sur le site.
"""

import asyncio
import json
import time
import logging
from typing import Dict, Any, List, Optional, Union

from config import settings, get_logger

logger = get_logger("product_rotator")

class ProductRotator:
    """
    Classe pour gérer la rotation des produits mis en avant sur le site
    selon différentes stratégies (performance, saisonnalité, nouveautés).
    """
    
    def __init__(self):
        """Initialise le gestionnaire de rotation des produits."""
        self.last_rotation = {}  # Stocke la date de dernière rotation par section
        logger.info("Gestionnaire de rotation des produits initialisé")
    
    async def _get_shop_products(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste des produits de la boutique.
        Cette méthode devrait être remplacée par une requête à l'API Shopify.
        
        Returns:
            Liste des produits
        """
        # Simuler la récupération des produits (remplacer par l'API réelle)
        await asyncio.sleep(0.5)  # Simulation de requête API
        
        return [
            {
                "id": f"prod_{i}",
                "title": f"Produit {i}",
                "created_at": time.time() - (i * 86400),  # Créé il y a i jours
                "updated_at": time.time() - (i * 43200),  # Mis à jour il y a i/2 jours
                "published_at": time.time() - (i * 86400),
                "sales_count": 100 - i,  # Simule des ventes décroissantes
                "view_count": 1000 - (i * 10),
                "conversion_rate": 0.1 - (i * 0.005),
                "tags": ["tag1", "tag2"] if i % 3 == 0 else ["tag3", "tag4"],
                "seasonal_score": 0.8 - (i * 0.05)
            } for i in range(1, 31)  # 30 produits
        ]
    
    async def _get_section_settings(self, section: str) -> Dict[str, Any]:
        """
        Récupère les paramètres de rotation pour une section spécifique.
        
        Args:
            section: Nom de la section
            
        Returns:
            Paramètres de rotation
        """
        # Paramètres par défaut
        default_settings = {
            "max_products": 10,
            "rotation_interval": settings.PRODUCT_ROTATION_INTERVAL,
            "criteria_weights": {
                "sales": 0.4,
                "views": 0.2,
                "conversion": 0.3,
                "recency": 0.1
            }
        }
        
        # Paramètres spécifiques par section
        section_settings = {
            "homepage": {
                "max_products": 5,
                "criteria_weights": {
                    "sales": 0.5,
                    "views": 0.2,
                    "conversion": 0.2,
                    "recency": 0.1
                }
            },
            "featured": {
                "max_products": 12,
                "criteria_weights": {
                    "sales": 0.3,
                    "views": 0.2,
                    "conversion": 0.4,
                    "recency": 0.1
                }
            },
            "collections": {
                "max_products": 20,
                "criteria_weights": {
                    "sales": 0.3,
                    "views": 0.3,
                    "conversion": 0.3,
                    "recency": 0.1
                }
            }
        }
        
        # Retourner les paramètres spécifiques ou par défaut
        return section_settings.get(section, default_settings)
    
    def _score_product(self, product: Dict[str, Any], criteria_weights: Dict[str, float], strategy: str) -> float:
        """
        Calcule un score pour un produit en fonction des critères et de la stratégie.
        
        Args:
            product: Données du produit
            criteria_weights: Pondération des critères
            strategy: Stratégie de rotation (performance, seasonal, newest)
            
        Returns:
            Score du produit
        """
        scores = {}
        
        # Score de ventes (normalisé à 100 max)
        scores["sales"] = min(product.get("sales_count", 0) / 100.0, 1.0)
        
        # Score de vues
        scores["views"] = min(product.get("view_count", 0) / 1000.0, 1.0)
        
        # Score de conversion
        scores["conversion"] = min(product.get("conversion_rate", 0) / 0.1, 1.0)  # normalise à 10% max
        
        # Score de nouveauté
        publish_time = product.get("published_at", 0)
        age_in_days = (time.time() - publish_time) / 86400.0 if publish_time else 30
        scores["recency"] = max(0, 1.0 - (age_in_days / 30.0))  # décroissant avec l'âge, 0 après 30 jours
        
        # Score de saisonnalité
        scores["seasonal"] = product.get("seasonal_score", 0.5)
        
        # Calcul du score pondéré selon la stratégie
        final_score = 0.0
        
        if strategy == "performance":
            # Utiliser les pondérations standards
            for criterion, weight in criteria_weights.items():
                if criterion in scores:
                    final_score += scores[criterion] * weight
        
        elif strategy == "seasonal":
            # Priorité à la saisonnalité
            seasonal_weight = 0.7
            remaining_weight = 1.0 - seasonal_weight
            
            final_score += scores["seasonal"] * seasonal_weight
            
            # Répartir le poids restant
            for criterion, weight in criteria_weights.items():
                if criterion != "seasonal" and criterion in scores:
                    final_score += scores[criterion] * (weight * remaining_weight)
        
        elif strategy == "newest":
            # Priorité aux nouveautés
            recency_weight = 0.8
            remaining_weight = 1.0 - recency_weight
            
            final_score += scores["recency"] * recency_weight
            
            # Répartir le poids restant
            for criterion, weight in criteria_weights.items():
                if criterion != "recency" and criterion in scores:
                    final_score += scores[criterion] * (weight * remaining_weight)
        
        else:  # Par défaut: équilibré
            # Pondération équitable de tous les critères
            all_criteria = list(scores.keys())
            equal_weight = 1.0 / len(all_criteria)
            
            for criterion in all_criteria:
                final_score += scores[criterion] * equal_weight
        
        return final_score
    
    async def rotate_featured_products(self, sections: List[str], strategy: str, max_products: int = None) -> Dict[str, Any]:
        """
        Effectue une rotation des produits mis en avant dans les sections spécifiées.
        
        Args:
            sections: Liste des sections à mettre à jour
            strategy: Stratégie de rotation (performance, seasonal, newest)
            max_products: Nombre maximal de produits par section
            
        Returns:
            Résultat de la rotation
        """
        # Récupérer tous les produits
        all_products = await self._get_shop_products()
        rotation_results = {}
        
        for section in sections:
            # Récupérer les paramètres de la section
            section_settings = await self._get_section_settings(section)
            section_max_products = max_products or section_settings.get("max_products", 10)
            criteria_weights = section_settings.get("criteria_weights", {})
            
            # Vérifier si une rotation est nécessaire
            last_rotation_time = self.last_rotation.get(section, 0)
            rotation_interval = section_settings.get("rotation_interval", settings.PRODUCT_ROTATION_INTERVAL)
            current_time = time.time()
            
            if (current_time - last_rotation_time) < rotation_interval:
                # Pas besoin de rotation pour cette section
                rotation_results[section] = {
                    "rotated": False,
                    "next_rotation": last_rotation_time + rotation_interval,
                    "reason": "Interval not reached"
                }
                continue
            
            # Calculer les scores pour chaque produit
            scored_products = [
                {
                    "id": product["id"],
                    "title": product["title"],
                    "score": self._score_product(product, criteria_weights, strategy),
                    "original_data": product
                }
                for product in all_products
            ]
            
            # Trier par score décroissant
            scored_products.sort(key=lambda p: p["score"], reverse=True)
            
            # Sélectionner les meilleurs produits
            selected_products = scored_products[:section_max_products]
            
            # Mettre à jour la section (simulation)
            # Dans une implémentation réelle, il faudrait appeler l'API Shopify
            await asyncio.sleep(0.3)  # Simulation de mise à jour
            
            # Mettre à jour le temps de dernière rotation
            self.last_rotation[section] = current_time
            
            # Enregistrer le résultat
            rotation_results[section] = {
                "rotated": True,
                "strategy": strategy,
                "products": [
                    {
                        "id": p["id"],
                        "title": p["title"],
                        "score": p["score"]
                    }
                    for p in selected_products
                ],
                "next_rotation": current_time + rotation_interval
            }
        
        return {
            "timestamp": time.time(),
            "results": rotation_results
        }
