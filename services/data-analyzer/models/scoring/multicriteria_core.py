#!/usr/bin/env python3
"""
Fonctions principales du système de scoring multicritères.
Ce module contient les méthodes clés pour le calcul des scores et les optimisations.
"""

import json
import time
from typing import Dict, Any, List, Optional, Union, Tuple
import logging

from config import get_logger

logger = get_logger("multicriteria_core")

def apply_niche_optimizations(
    config: Dict[str, Any], 
    niche: str, 
    niche_optimizations: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Applique les optimisations spécifiques à une niche.
    
    Args:
        config: Configuration de base
        niche: Niche du produit
        niche_optimizations: Dictionnaire des optimisations par niche
        
    Returns:
        Configuration ajustée selon la niche
    """
    # Copie de la configuration par défaut
    adjusted_config = deep_copy_config(config)
    
    if not config.get('niche_adjustments', True) or not niche:
        return adjusted_config
    
    # Recherche d'une correspondance dans les niches connues
    matching_niche = None
    for niche_key in niche_optimizations:
        if niche_key in niche:
            matching_niche = niche_key
            break
    
    if not matching_niche:
        return adjusted_config
    
    logger.info(f"Application des optimisations pour la niche '{matching_niche}'")
    niche_config = niche_optimizations[matching_niche]
    
    # Ajustement des poids par catégorie
    if 'weights' in niche_config:
        for category, weight in niche_config['weights'].items():
            if category in adjusted_config['weights']:
                adjusted_config['weights'][category] = weight
    
    # Ajustement des poids par critère
    if 'criteria_adjustments' in niche_config:
        for criterion, adjustment in niche_config['criteria_adjustments'].items():
            # Recherche du critère dans toutes les catégories
            for category, criteria in adjusted_config['criteria'].items():
                for i, crit in enumerate(criteria):
                    if crit['name'] == criterion:
                        # Ajuster le poids en le multipliant par le facteur d'ajustement
                        original_weight = crit['weight']
                        adjusted_config['criteria'][category][i]['weight'] = original_weight * adjustment
                        
                        # Normaliser les poids dans cette catégorie
                        normalize_weights(adjusted_config['criteria'][category])
                        break
    
    return adjusted_config

def deep_copy_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crée une copie profonde de la configuration.
    
    Args:
        config: Configuration à copier
        
    Returns:
        Copie profonde de la configuration
    """
    # Utiliser json pour une copie profonde simplifiée
    return json.loads(json.dumps(config))

def normalize_weights(criteria: List[Dict[str, Any]]) -> None:
    """
    Normalise les poids des critères pour qu'ils totalisent 1.0.
    
    Args:
        criteria: Liste de critères avec leurs poids
    """
    total_weight = sum(crit['weight'] for crit in criteria)
    
    if total_weight > 0:
        for crit in criteria:
            crit['weight'] = crit['weight'] / total_weight

def calculate_category_score(
    category: str, 
    criteria: List[Dict[str, Any]], 
    data: Dict[str, Any],
    criterion_functions: Dict[str, callable]
) -> float:
    """
    Calcule le score pour une catégorie spécifique.
    
    Args:
        category: Nom de la catégorie
        criteria: Liste des critères pour cette catégorie
        data: Données collectées pour le produit
        criterion_functions: Dictionnaire de fonctions d'évaluation des critères
        
    Returns:
        Score pour la catégorie (0-100)
    """
    score = 0
    available_criteria = 0
    total_weight = 0
    
    for criterion in criteria:
        criterion_name = criterion['name']
        criterion_weight = criterion['weight']
        
        # Récupérer la fonction d'évaluation pour ce critère
        criterion_function = criterion_functions.get(criterion_name)
        
        if criterion_function:
            # Évaluer le critère
            criterion_score = criterion_function(data)
            
            if criterion_score is not None:
                score += criterion_score * criterion_weight
                available_criteria += 1
                total_weight += criterion_weight
    
    # Si aucun critère n'est disponible, retourner un score neutre
    if available_criteria == 0:
        return 50
        
    # Ajuster le score pour tenir compte des critères manquants
    if total_weight > 0 and total_weight < 1:
        score = score / total_weight
        
    return score

def get_recommendation(score: float, thresholds: Dict[str, float]) -> str:
    """
    Génère une recommandation basée sur le score global.
    
    Args:
        score: Score global du produit
        thresholds: Seuils de classification
        
    Returns:
        Recommandation textuelle
    """
    if score >= thresholds.get('high_potential', 75):
        return "Potentiel élevé - Fortement recommandé"
    elif score >= thresholds.get('medium_potential', 60):
        return "Potentiel moyen - À considérer avec attention"
    elif score >= thresholds.get('low_potential', 40):
        return "Potentiel faible - Non recommandé sauf focus de niche"
    else:
        return "Potentiel très faible - À éviter"
