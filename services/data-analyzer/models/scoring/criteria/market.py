#!/usr/bin/env python3
"""
Méthodes de scoring pour évaluer le potentiel de marché des produits.
"""

from typing import Dict, Any, Optional
from config import get_logger

logger = get_logger("criteria.market")

def score_search_volume(data: Dict[str, Any]) -> Optional[float]:
    """
    Évalue le volume de recherche mensuel d'un produit.
    
    Args:
        data: Données collectées pour le produit
        
    Returns:
        Score du volume de recherche (0-100) ou None si non disponible
    """
    # Vérifier les données SEO
    if 'seo' in data and 'search_volume' in data['seo']:
        volume = data['seo'].get('search_volume', 0)
        # Échelle logarithmique pour le volume de recherche
        if volume > 100000:
            return 100
        elif volume > 10000:
            return 80 + (volume - 10000) / 90000 * 20
        elif volume > 1000:
            return 60 + (volume - 1000) / 9000 * 20
        elif volume > 100:
            return 40 + (volume - 100) / 900 * 20
        elif volume > 10:
            return 20 + (volume - 10) / 90 * 20
        else:
            return max(0, volume * 2)
    
    # Alternative: vérifier les données de tendances
    elif 'trends' in data and 'trend_metrics' in data['trends']:
        metrics = data['trends'].get('trend_metrics', {})
        # Utiliser les données du premier mot-clé
        if metrics:
            first_keyword = next(iter(metrics))
            keyword_metrics = metrics.get(first_keyword, {})
            current_interest = keyword_metrics.get('current_interest', 0)
            # Convertir l'intérêt actuel (0-100) en score de volume
            return current_interest
    
    # Aucune donnée disponible
    return None

def score_growth_rate(data: Dict[str, Any]) -> Optional[float]:
    """
    Évalue le taux de croissance du marché pour un produit.
    
    Args:
        data: Données collectées pour le produit
        
    Returns:
        Score du taux de croissance (0-100) ou None si non disponible
    """
    # Vérifier les données de tendances
    if 'trends' in data and 'trend_metrics' in data['trends']:
        metrics = data['trends'].get('trend_metrics', {})
        # Utiliser les données du premier mot-clé
        if metrics:
            first_keyword = next(iter(metrics))
            keyword_metrics = metrics.get(first_keyword, {})
            growth_rate = keyword_metrics.get('growth_rate', 0)
            
            # Convertir le taux de croissance en score
            if growth_rate > 100:
                return 100
            elif growth_rate > 50:
                return 90
            elif growth_rate > 25:
                return 80
            elif growth_rate > 10:
                return 70
            elif growth_rate > 0:
                return 60
            elif growth_rate > -10:
                return 40
            elif growth_rate > -25:
                return 30
            elif growth_rate > -50:
                return 20
            else:
                return 10
    
    # Vérifier les données de marché
    elif 'market' in data and 'growth_rate' in data['market']:
        growth_rate = data['market'].get('growth_rate', 0)
        # Score linéaire entre -50% et +100%
        return max(0, min(100, 50 + growth_rate * 0.5))
    
    # Aucune donnée disponible
    return None

def score_market_size(data: Dict[str, Any]) -> Optional[float]:
    """
    Évalue la taille du marché pour un produit.
    
    Args:
        data: Données collectées pour le produit
        
    Returns:
        Score de la taille du marché (0-100) ou None si non disponible
    """
    # Vérifier les données de marché
    if 'market' in data and 'market_size' in data['market']:
        market_size = data['market'].get('market_size', 0)
        
        # Échelle logarithmique pour la taille du marché (en millions $)
        if market_size > 1000:  # > 1 milliard $
            return 100
        elif market_size > 100:
            return 80 + (market_size - 100) / 900 * 20
        elif market_size > 10:
            return 60 + (market_size - 10) / 90 * 20
        elif market_size > 1:
            return 40 + (market_size - 1) / 9 * 20
        elif market_size > 0.1:
            return 20 + (market_size - 0.1) / 0.9 * 20
        else:
            return max(0, market_size * 200)
    
    # Alternative: estimation basée sur le volume de recherche
    elif 'seo' in data and 'search_volume' in data['seo']:
        volume = data['seo'].get('search_volume', 0)
        # Estimation très approximative
        estimated_market_size = volume * 0.01  # 1 cent par recherche mensuelle
        
        # Appliquer la même échelle logarithmique
        if estimated_market_size > 1000:
            return 100
        elif estimated_market_size > 100:
            return 80 + (estimated_market_size - 100) / 900 * 20
        elif estimated_market_size > 10:
            return 60 + (estimated_market_size - 10) / 90 * 20
        elif estimated_market_size > 1:
            return 40 + (estimated_market_size - 1) / 9 * 20
        elif estimated_market_size > 0.1:
            return 20 + (estimated_market_size - 0.1) / 0.9 * 20
        else:
            return max(0, estimated_market_size * 200)
    
    # Aucune donnée disponible
    return None
