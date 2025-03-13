#!/usr/bin/env python3
"""
Méthodes de scoring pour évaluer la profitabilité des produits.
"""

from typing import Dict, Any, Optional
import math
from config import get_logger

logger = get_logger("criteria.profitability")

def score_margin(data: Dict[str, Any]) -> Optional[float]:
    """
    Évalue la marge brute potentielle d'un produit.
    
    Args:
        data: Données collectées pour le produit
        
    Returns:
        Score de la marge (0-100) ou None si non disponible
    """
    # Vérifier les données de marketplace
    if 'marketplace' in data and 'margin_percentage' in data['marketplace']:
        margin = data['marketplace'].get('margin_percentage', 0)
        
        # Échelle linéaire pour la marge
        if margin > 70:
            return 100
        elif margin > 50:
            return 80 + (margin - 50) * 1
        elif margin > 30:
            return 60 + (margin - 30) * 1
        elif margin > 20:
            return 40 + (margin - 20) * 2
        elif margin > 10:
            return 20 + (margin - 10) * 2
        else:
            return max(0, margin * 2)
    
    # Alternative: calcul à partir du prix de vente et du prix fournisseur
    elif 'marketplace' in data:
        marketplace_data = data.get('marketplace', {})
        retail_price = marketplace_data.get('retail_price', 0)
        supplier_price = marketplace_data.get('supplier_price', 0)
        
        if retail_price > 0 and supplier_price > 0 and retail_price > supplier_price:
            # Calcul de la marge brute en pourcentage
            margin_percentage = ((retail_price - supplier_price) / retail_price) * 100
            
            # Appliquer la même échelle
            if margin_percentage > 70:
                return 100
            elif margin_percentage > 50:
                return 80 + (margin_percentage - 50) * 1
            elif margin_percentage > 30:
                return 60 + (margin_percentage - 30) * 1
            elif margin_percentage > 20:
                return 40 + (margin_percentage - 20) * 2
            elif margin_percentage > 10:
                return 20 + (margin_percentage - 10) * 2
            else:
                return max(0, margin_percentage * 2)
    
    # Aucune donnée disponible
    return None

def score_price_stability(data: Dict[str, Any]) -> Optional[float]:
    """
    Évalue la stabilité des prix d'un produit.
    
    Args:
        data: Données collectées pour le produit
        
    Returns:
        Score de la stabilité des prix (0-100) ou None si non disponible
    """
    # Vérifier les données de marketplace
    if 'marketplace' in data and 'price_volatility' in data['marketplace']:
        volatility = data['marketplace'].get('price_volatility', 50)
        
        # Convertir la volatilité (0-100) en score de stabilité (0-100)
        stability = 100 - volatility
        return stability
    
    # Alternative: estimer à partir de l'historique des prix
    elif 'marketplace' in data and 'price_history' in data['marketplace']:
        price_history = data['marketplace'].get('price_history', [])
        
        if len(price_history) > 1:
            # Calculer la volatilité comme l'écart-type normalisé
            prices = [p.get('price', 0) for p in price_history]
            avg_price = sum(prices) / len(prices)
            
            if avg_price > 0:
                # Écart-type
                variance = sum((p - avg_price) ** 2 for p in prices) / len(prices)
                std_dev = math.sqrt(variance)
                
                # Coefficient de variation (écart-type / moyenne)
                cv = (std_dev / avg_price) * 100
                
                # Convertir en score de stabilité
                if cv < 5:
                    return 100  # Très stable
                elif cv < 10:
                    return 80 + (10 - cv) * 4  # 80 à 100
                elif cv < 20:
                    return 60 + (20 - cv) * 2  # 60 à 80
                elif cv < 30:
                    return 40 + (30 - cv) * 2  # 40 à 60
                elif cv < 50:
                    return 20 + (50 - cv) * 1  # 20 à 40
                else:
                    return max(0, 20 - (cv - 50) * 0.4)  # 20 à 0
    
    # Aucune donnée disponible
    return None

def score_upsell_potential(data: Dict[str, Any]) -> Optional[float]:
    """
    Évalue le potentiel de ventes additionnelles (upsell/cross-sell).
    
    Args:
        data: Données collectées pour le produit
        
    Returns:
        Score du potentiel d'upsell (0-100) ou None si non disponible
    """
    # Vérifier les données d'analyse de marché
    if 'market' in data and 'upsell_potential' in data['market']:
        potential = data['market'].get('upsell_potential', 50)
        return potential
    
    # Alternative: estimer à partir des produits complémentaires
    elif 'marketplace' in data and 'complementary_products' in data['marketplace']:
        complementary = data['marketplace'].get('complementary_products', [])
        
        # Évaluer le nombre et la qualité des produits complémentaires
        complementary_count = len(complementary)
        
        if complementary_count > 10:
            return 100
        elif complementary_count > 5:
            return 80 + (complementary_count - 5) * 4  # 80 à 100
        elif complementary_count > 2:
            return 60 + (complementary_count - 2) * 6.67  # 60 à 80
        elif complementary_count > 0:
            return 30 + complementary_count * 15  # 30 à 60
        else:
            return 30  # Potentiel minimal
    
    # Aucune donnée disponible
    return None
