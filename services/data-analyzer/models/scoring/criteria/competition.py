#!/usr/bin/env python3
"""
Méthodes de scoring pour évaluer le niveau de concurrence des produits.
"""

from typing import Dict, Any, Optional
from config import get_logger

logger = get_logger("criteria.competition")

def score_competitor_count(data: Dict[str, Any]) -> Optional[float]:
    """
    Évalue le nombre de concurrents directs.
    
    Args:
        data: Données collectées pour le produit
        
    Returns:
        Score du nombre de concurrents (0-100) ou None si non disponible
    """
    # Vérifier les données de marketplace
    if 'marketplace' in data and 'competitor_count' in data['marketplace']:
        competitors = data['marketplace'].get('competitor_count', 0)
        
        # Échelle inversée: moins de concurrents = meilleur score
        if competitors == 0:
            return 100  # Marché vierge (rare)
        elif competitors < 5:
            return 90 - (competitors - 1) * 5  # 90 à 70
        elif competitors < 20:
            return 70 - (competitors - 5) * 2  # 70 à 40
        elif competitors < 50:
            return 40 - (competitors - 20) * 0.5  # 40 à 25
        elif competitors < 100:
            return 25 - (competitors - 50) * 0.2  # 25 à 15
        else:
            return max(0, 15 - (competitors - 100) * 0.05)  # 15 à 0
    
    # Aucune donnée disponible
    return None

def score_price_competition(data: Dict[str, Any]) -> Optional[float]:
    """
    Évalue l'intensité de la concurrence par les prix.
    
    Args:
        data: Données collectées pour le produit
        
    Returns:
        Score de la concurrence par les prix (0-100) ou None si non disponible
    """
    # Vérifier les données de marketplace
    if 'marketplace' in data and 'price_competition' in data['marketplace']:
        competition = data['marketplace'].get('price_competition', 50)
        
        # Le score est inversement proportionnel à l'intensité de la concurrence
        return 100 - competition
    
    # Alternative: vérifier l'écart de prix
    elif 'marketplace' in data and 'price_gap' in data['marketplace']:
        price_gap = data['marketplace'].get('price_gap', 0)
        
        # Un grand écart de prix est favorable (plus de marge potentielle)
        if price_gap > 70:
            return 100
        elif price_gap > 50:
            return 80 + (price_gap - 50) * 1
        elif price_gap > 30:
            return 60 + (price_gap - 30) * 1
        elif price_gap > 15:
            return 40 + (price_gap - 15) * 4/3
        elif price_gap > 5:
            return 20 + (price_gap - 5) * 2
        else:
            return max(0, price_gap * 4)
    
    # Aucune donnée disponible
    return None

def score_barriers_to_entry(data: Dict[str, Any]) -> Optional[float]:
    """
    Évalue les barrières à l'entrée sur le marché.
    
    Args:
        data: Données collectées pour le produit
        
    Returns:
        Score des barrières à l'entrée (0-100) ou None si non disponible
    """
    # Vérifier les données de marché
    if 'market' in data and 'barriers_to_entry' in data['market']:
        barriers = data['market'].get('barriers_to_entry', 50)
        
        # Les barrières modérées sont optimales pour le dropshipping
        # (assez basses pour qu'on puisse entrer, assez hautes pour limiter la concurrence)
        if barriers > 80:
            return 40  # Trop de barrières, difficile d'entrer
        elif barriers > 60:
            return 70 + (80 - barriers) * 1.5  # 70 à 100
        elif barriers > 30:
            return 70  # Zone optimale
        elif barriers > 10:
            return 70 - (30 - barriers) * 1.5  # 70 à 40
        else:
            return 40 - (10 - barriers) * 4  # 40 à 0
    
    # Estimation basée sur d'autres facteurs
    else:
        # Importation ici pour éviter les dépendances circulaires
        from models.scoring.criteria.operational import score_shipping_complexity
        
        # Estimer les barrières à partir des scores de concurrence et complexité
        competitor_score = score_competitor_count(data)
        complexity_score = score_shipping_complexity(data)
        
        if competitor_score is not None and complexity_score is not None:
            # Beaucoup de concurrents + faible complexité = faibles barrières
            # Peu de concurrents + forte complexité = fortes barrières
            estimated_barriers = (100 - competitor_score) * 0.7 + complexity_score * 0.3
            
            # Appliquer la même échelle de préférence pour les barrières modérées
            if estimated_barriers > 80:
                return 40
            elif estimated_barriers > 60:
                return 70 + (80 - estimated_barriers) * 1.5
            elif estimated_barriers > 30:
                return 70
            elif estimated_barriers > 10:
                return 70 - (30 - estimated_barriers) * 1.5
            else:
                return 40 - (10 - estimated_barriers) * 4
    
    # Aucune donnée disponible
    return None
