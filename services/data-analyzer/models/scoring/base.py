#!/usr/bin/env python3
"""
Classe de base pour les systèmes de scoring de produits.
Cette classe définit l'interface commune pour tous les scorers de produits.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import logging

from config import settings, get_logger

logger = get_logger("product_scorer")

class ProductScorer(ABC):
    """
    Classe abstraite définissant l'interface pour les systèmes de scoring de produits.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le système de scoring.
        
        Args:
            config: Configuration optionnelle pour le scorer
        """
        self.config = config or self._default_config()
        logger.info(f"Initialisation de {self.__class__.__name__}")
    
    @abstractmethod
    def _default_config(self) -> Dict[str, Any]:
        """
        Retourne la configuration par défaut du scorer.
        
        Returns:
            Dictionnaire de configuration par défaut
        """
        pass
    
    @abstractmethod
    def score_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule le score d'un produit.
        
        Args:
            product_data: Données du produit à évaluer
            
        Returns:
            Dictionnaire contenant le score global et les scores détaillés
        """
        pass
    
    @abstractmethod
    def explain_score(self, score_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère une explication textuelle du score.
        
        Args:
            score_result: Résultat du scoring retourné par score_product
            
        Returns:
            Dictionnaire contenant des explications structurées du scoring
        """
        pass
    
    def get_recommendation(self, score_result: Dict[str, Any]) -> str:
        """
        Génère une recommandation basée sur le score.
        
        Args:
            score_result: Résultat du scoring retourné par score_product
            
        Returns:
            Recommandation textuelle
        """
        overall_score = score_result.get("overall_score", 0)
        
        if overall_score >= settings.SCORING_THRESHOLDS["high_potential"]:
            return "Potentiel élevé - Fortement recommandé"
        elif overall_score >= settings.SCORING_THRESHOLDS["medium_potential"]:
            return "Potentiel moyen - À considérer avec attention"
        elif overall_score >= settings.SCORING_THRESHOLDS["low_potential"]:
            return "Potentiel faible - Non recommandé sauf focus de niche"
        else:
            return "Potentiel très faible - À éviter"
    
    def calculate_confidence(self, score_result: Dict[str, Any]) -> float:
        """
        Calcule un niveau de confiance pour le score généré.
        
        Args:
            score_result: Résultat du scoring retourné par score_product
            
        Returns:
            Score de confiance entre 0 et 100
        """
        # Implémentation par défaut simpliste
        # Les sous-classes devraient implémenter une logique plus sophistiquée
        completeness = score_result.get("data_completeness", 50)
        consistency = score_result.get("data_consistency", 50)
        
        return (completeness * 0.6) + (consistency * 0.4)
    
    def batch_score_products(self, products_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calcule les scores pour plusieurs produits.
        
        Args:
            products_data: Liste des données de produits à évaluer
            
        Returns:
            Liste des résultats de scoring
        """
        results = []
        
        for product_data in products_data:
            try:
                score_result = self.score_product(product_data)
                results.append(score_result)
            except Exception as e:
                logger.error(f"Erreur lors du scoring du produit {product_data.get('name', 'inconnu')}: {str(e)}")
                # Ajouter un résultat d'erreur pour maintenir l'ordre
                results.append({
                    "error": str(e),
                    "product_id": product_data.get("id"),
                    "product_name": product_data.get("name", "inconnu")
                })
        
        return results
    
    def update_config(self, config_updates: Dict[str, Any]) -> None:
        """
        Met à jour la configuration du scorer.
        
        Args:
            config_updates: Nouvelles valeurs de configuration
        """
        # Mise à jour récursive de la configuration
        self._update_dict_recursively(self.config, config_updates)
        logger.info(f"Configuration de {self.__class__.__name__} mise à jour")
    
    def _update_dict_recursively(self, target: Dict[str, Any], updates: Dict[str, Any]) -> None:
        """
        Met à jour récursivement un dictionnaire avec de nouvelles valeurs.
        
        Args:
            target: Dictionnaire cible à mettre à jour
            updates: Dictionnaire contenant les mises à jour
        """
        for key, value in updates.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict_recursively(target[key], value)
            else:
                target[key] = value
