#!/usr/bin/env python3
"""
Méthodes de scoring pour évaluer les tendances des produits.
"""

from typing import Dict, Any, Optional
from config import get_logger

logger = get_logger("criteria.trend")

def score_trend_consistency(data: Dict[str, Any]) -> Optional[float]:
    """
    Évalue la consistance de la tendance d'un produit.
    
    Args:
        data: Données collectées pour le produit
        
    Returns:
        Score de consistance de la tendance (0-100) ou None si non disponible
    """
    # Vérifier les données de tendances
    if 'trends' in data and 'trend_metrics' in data['trends']:
        metrics = data['trends'].get('trend_metrics', {})
        
        # Utiliser les données du premier mot-clé
        if metrics:
            first_keyword = next(iter(metrics))
            keyword_metrics = metrics.get(first_keyword, {})
            
            # La volatilité faible indique une tendance consistante
            volatility = keyword_metrics.get('volatility', 50)
            momentum = keyword_metrics.get('momentum', 0)
            
            # Score de consistance basé sur la volatilité inversée
            consistency_score = max(0, 100 - volatility)
            
            # Bonus pour un momentum positif (tendance qui s'accélère)
            if momentum > 0:
                momentum_bonus = min(20, momentum * 0.2)  # Jusqu'à 20 points bonus
                consistency_score = min(100, consistency_score + momentum_bonus)
                
            return consistency_score
    
    # Aucune donnée disponible
    return None

def score_seasonality(data: Dict[str, Any]) -> Optional[float]:
    """
    Évalue l'impact de la saisonnalité pour un produit.
    
    Args:
        data: Données collectées pour le produit
        
    Returns:
        Score de l'impact de la saisonnalité (0-100) ou None si non disponible
    """
    # Vérifier les données de tendances
    if 'trends' in data and 'seasonality' in data['trends']:
        seasonality = data['trends'].get('seasonality', {})
        is_seasonal = seasonality.get('is_seasonal', False)
        confidence = seasonality.get('confidence', 0)
        pattern = seasonality.get('pattern', 'unknown')
        
        # Une saisonnalité bien définie est généralement positive (opportunité)
        # mais une saisonnalité extrême peut être risquée
        if not is_seasonal:
            return 60  # Produit non saisonnier = score moyen
        
        # Bonus pour les produits saisonniers identifiés avec confiance
        seasonal_score = 60 + confidence * 25  # 60 à 85
        
        # Ajustement selon le pattern saisonnier
        if pattern == 'annual':
            # Pattern annuel = bonne prévisibilité
            seasonal_score += 15
        elif pattern == 'multi_peak':
            # Plusieurs pics = opportunités multiples
            seasonal_score += 10
        elif pattern == 'quarterly':
            # Trimestriel = cycles courts, plus d'opportunités
            seasonal_score += 5
            
        return min(100, seasonal_score)
    
    # Alternative: estimer à partir de la catégorie de produit
    elif 'basic_info' in data:
        info = data.get('basic_info', {})
        category = info.get('category', '')
        
        # Catégories fortement saisonnières
        highly_seasonal = ['christmas', 'halloween', 'valentines', 'seasonal', 'holiday', 'winter', 'summer']
        moderately_seasonal = ['outdoor', 'garden', 'beach', 'school', 'back to school', 'sports']
        
        # Vérifier si la catégorie contient des mots-clés saisonniers
        for term in highly_seasonal:
            if term in category.lower():
                return 85  # Fortement saisonnier
                
        for term in moderately_seasonal:
            if term in category.lower():
                return 75  # Modérément saisonnier
                
        # Par défaut, supposer une saisonnalité moyenne
        return 60
    
    # Aucune donnée disponible
    return None

def score_social_mentions(data: Dict[str, Any]) -> Optional[float]:
    """
    Évalue le niveau et la qualité des mentions sur les réseaux sociaux.
    
    Args:
        data: Données collectées pour le produit
        
    Returns:
        Score des mentions sociales (0-100) ou None si non disponible
    """
    # Vérifier les données sociales
    if 'social' in data and 'mentions' in data['social']:
        social_data = data['social']
        mentions = social_data.get('mentions', 0)
        sentiment = social_data.get('sentiment', 0)  # -100 à +100
        engagement = social_data.get('engagement', 0)  # 0 à 100
        growth = social_data.get('mention_growth', 0)  # % de croissance
        
        # Base du score sur le nombre de mentions
        if mentions > 10000:
            base_score = 100
        elif mentions > 5000:
            base_score = 80 + (mentions - 5000) / 500 * 2  # 80 à 100
        elif mentions > 1000:
            base_score = 60 + (mentions - 1000) / 400 * 2  # 60 à 80
        elif mentions > 100:
            base_score = 40 + (mentions - 100) / 90 * 2  # 40 à 60
        elif mentions > 10:
            base_score = 20 + (mentions - 10) / 9 * 2  # 20 à 40
        else:
            base_score = max(0, mentions * 2)  # 0 à 20
        
        # Ajustement selon le sentiment
        sentiment_modifier = sentiment / 2  # -50 à +50 points
        
        # Ajustement selon l'engagement
        engagement_modifier = (engagement / 100) * 20  # 0 à 20 points
        
        # Ajustement selon la croissance
        growth_modifier = 0
        if growth > 100:
            growth_modifier = 30
        elif growth > 50:
            growth_modifier = 20
        elif growth > 25:
            growth_modifier = 15
        elif growth > 10:
            growth_modifier = 10
        elif growth > 0:
            growth_modifier = 5
            
        # Score final (limité entre 0 et 100)
        social_score = base_score + sentiment_modifier + engagement_modifier + growth_modifier
        return max(0, min(100, social_score))
    
    # Alternative: estimer à partir d'autres données
    elif 'marketplace' in data:
        marketplace_data = data.get('marketplace', {})
        review_count = marketplace_data.get('review_count', 0)
        avg_rating = marketplace_data.get('avg_rating', 0)
        
        # Estimer un score social basé sur les avis clients
        if review_count > 0 and avg_rating > 0:
            # Score de base sur le nombre d'avis
            if review_count > 1000:
                base_score = 70
            elif review_count > 500:
                base_score = 60
            elif review_count > 100:
                base_score = 50
            elif review_count > 50:
                base_score = 40
            elif review_count > 10:
                base_score = 30
            else:
                base_score = 20
            
            # Ajustement selon la note moyenne (1-5)
            rating_modifier = (avg_rating - 3) * 10  # -20 à +20
            
            return max(0, min(100, base_score + rating_modifier))
    
    # Aucune donnée disponible
    return None
