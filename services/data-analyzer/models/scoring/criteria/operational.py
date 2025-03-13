#!/usr/bin/env python3
"""
Méthodes de scoring pour évaluer les aspects opérationnels des produits.
"""

from typing import Dict, Any, Optional
from config import get_logger

logger = get_logger("criteria.operational")

def score_shipping_complexity(data: Dict[str, Any]) -> Optional[float]:
    """
    Évalue la complexité d'expédition d'un produit.
    
    Args:
        data: Données collectées pour le produit
        
    Returns:
        Score inversé de la complexité d'expédition (0-100) ou None si non disponible
    """
    # Vérifier les données de logistique
    if 'logistics' in data and 'shipping_complexity' in data['logistics']:
        complexity = data['logistics'].get('shipping_complexity', 50)
        
        # Inverser le score (moins complexe = meilleur score)
        return 100 - complexity
    
    # Alternative: estimer à partir des caractéristiques du produit
    elif 'basic_info' in data:
        info = data.get('basic_info', {})
        weight_kg = info.get('weight_kg', None)
        is_fragile = info.get('is_fragile', False)
        is_liquid = info.get('is_liquid', False)
        is_hazardous = info.get('is_hazardous', False)
        dimensions = info.get('dimensions', None)
        
        # Score de base
        base_score = 70
        
        # Appliquer des pénalités
        if is_hazardous:
            base_score -= 50  # Produits dangereux = très complexes
            
        if is_liquid:
            base_score -= 20  # Liquides = risque de fuite
            
        if is_fragile:
            base_score -= 15  # Fragile = emballage spécial requis
            
        if weight_kg is not None:
            if weight_kg > 20:
                base_score -= 30  # Très lourd
            elif weight_kg > 10:
                base_score -= 20  # Lourd
            elif weight_kg > 5:
                base_score -= 10  # Moyennement lourd
            elif weight_kg > 2:
                base_score -= 5   # Légèrement lourd
                
        if dimensions is not None:
            # Calculer si c'est un colis surdimensionné
            volume = dimensions.get('length', 0) * dimensions.get('width', 0) * dimensions.get('height', 0)
            if volume > 0.5:  # Plus de 0.5 m³
                base_score -= 25  # Très volumineux
            elif volume > 0.2:
                base_score -= 15  # Volumineux
            elif volume > 0.1:
                base_score -= 5   # Légèrement volumineux
                
        return max(0, min(100, base_score))
    
    # Aucune donnée disponible
    return None

def score_return_rate(data: Dict[str, Any]) -> Optional[float]:
    """
    Évalue le taux de retour anticipé pour un produit.
    
    Args:
        data: Données collectées pour le produit
        
    Returns:
        Score inversé du taux de retour (0-100) ou None si non disponible
    """
    # Vérifier les données de performance
    if 'performance' in data and 'return_rate' in data['performance']:
        return_rate = data['performance'].get('return_rate', 0)
        
        # Convertir le pourcentage de retours en score (inversé)
        if return_rate < 1:
            return 100  # Presque pas de retours
        elif return_rate < 3:
            return 90 - (return_rate - 1) * 5  # 90 à 80
        elif return_rate < 5:
            return 80 - (return_rate - 3) * 10  # 80 à 60
        elif return_rate < 10:
            return 60 - (return_rate - 5) * 4  # 60 à 40
        elif return_rate < 20:
            return 40 - (return_rate - 10) * 2  # 40 à 20
        else:
            return max(0, 20 - (return_rate - 20) * 0.5)  # 20 à 0
    
    # Alternative: estimer à partir des avis et de la catégorie
    elif 'marketplace' in data:
        marketplace_data = data.get('marketplace', {})
        product_category = marketplace_data.get('category', '')
        avg_rating = marketplace_data.get('avg_rating', 0)
        
        # Score de base selon la catégorie (certaines catégories ont plus de retours)
        base_score = 70
        high_return_categories = ['clothing', 'shoes', 'fashion', 'jewelry']
        medium_return_categories = ['electronics', 'beauty', 'health']
        
        # Ajuster le score selon la catégorie
        for category in high_return_categories:
            if category in product_category.lower():
                base_score -= 20
                break
                
        for category in medium_return_categories:
            if category in product_category.lower():
                base_score -= 10
                break
        
        # Ajuster selon la note moyenne (1-5)
        if avg_rating > 0:
            rating_impact = (avg_rating - 3) * 10  # -20 à +20
            base_score += rating_impact
            
        return max(0, min(100, base_score))
    
    # Aucune donnée disponible
    return None

def score_supplier_reliability(data: Dict[str, Any]) -> Optional[float]:
    """
    Évalue la fiabilité du fournisseur d'un produit.
    
    Args:
        data: Données collectées pour le produit
        
    Returns:
        Score de la fiabilité du fournisseur (0-100) ou None si non disponible
    """
    # Vérifier les données de fournisseur
    if 'supplier' in data and 'reliability_score' in data['supplier']:
        reliability = data['supplier'].get('reliability_score', 50)
        return reliability
    
    # Alternative: estimer à partir d'autres métriques fournisseur
    elif 'supplier' in data:
        supplier_data = data.get('supplier', {})
        
        # Facteurs de fiabilité
        years_active = supplier_data.get('years_active', 0)
        on_time_delivery = supplier_data.get('on_time_delivery', 0)
        defect_rate = supplier_data.get('defect_rate', 0)
        communication_rating = supplier_data.get('communication_rating', 0)
        
        # Score de fiabilité cumulé
        reliability_score = 0
        metrics_count = 0
        
        # Ancienneté du fournisseur
        if years_active > 0:
            if years_active > 10:
                reliability_score += 100
            elif years_active > 5:
                reliability_score += 80
            elif years_active > 2:
                reliability_score += 60
            elif years_active > 1:
                reliability_score += 40
            else:
                reliability_score += 20
            metrics_count += 1
        
        # Livraison à temps (%)
        if on_time_delivery > 0:
            reliability_score += on_time_delivery
            metrics_count += 1
        
        # Taux de défauts inversé (%)
        if defect_rate >= 0:
            reliability_score += max(0, 100 - defect_rate * 10)  # 0% de défauts = 100, 10% = 0
            metrics_count += 1
        
        # Note de communication (1-5)
        if communication_rating > 0:
            reliability_score += communication_rating * 20  # 1 = 20, 5 = 100
            metrics_count += 1
        
        # Calculer la moyenne si des métriques sont disponibles
        if metrics_count > 0:
            return reliability_score / metrics_count
    
    # Aucune donnée disponible
    return None
