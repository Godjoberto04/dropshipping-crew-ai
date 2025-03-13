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

def calculate_confidence(
    data: Dict[str, Any], 
    category_scores: Dict[str, float],
    critical_criteria: List[str]
) -> float:
    """
    Calcule un niveau de confiance pour le score généré.
    
    Args:
        data: Données collectées pour le produit
        category_scores: Scores par catégorie
        critical_criteria: Liste des critères considérés comme critiques
        
    Returns:
        Score de confiance (0-100)
    """
    # Vérifier la complétude des données
    data_completeness = calculate_data_completeness(data, critical_criteria)
    
    # Vérifier la cohérence des scores
    data_consistency = calculate_data_consistency(category_scores)
    
    # Calculer la confiance globale (60% complétude, 40% cohérence)
    confidence = (data_completeness * 0.6) + (data_consistency * 0.4)
    
    return confidence

def calculate_data_completeness(data: Dict[str, Any], critical_criteria: List[str]) -> float:
    """
    Évalue la complétude des données disponibles.
    
    Args:
        data: Données collectées pour le produit
        critical_criteria: Liste des critères considérés comme critiques
        
    Returns:
        Score de complétude (0-100)
    """
    # Calculer la disponibilité des principales sources de données
    sources = ['trends', 'marketplace', 'seo', 'social', 'supplier']
    available_sources = sum(1 for source in sources if source in data and not isinstance(data[source], dict) or not data[source].get('error'))
    source_completeness = (available_sources / len(sources)) * 100
    
    # Vérifier la disponibilité des critères critiques
    critical_available = 0
    
    for criterion in critical_criteria:
        # Cette vérification est simplifiée, en réalité il faudrait vérifier de manière plus précise
        if criterion == 'search_volume' and 'seo' in data and 'search_volume' in data['seo']:
            critical_available += 1
        elif criterion == 'margin' and 'marketplace' in data and 'margin_percentage' in data['marketplace']:
            critical_available += 1
        elif criterion == 'competitor_count' and 'marketplace' in data and 'competitor_count' in data['marketplace']:
            critical_available += 1
    
    critical_completeness = (critical_available / len(critical_criteria)) * 100 if critical_criteria else 100
    
    # Combinaison des scores (70% critiques, 30% sources)
    return (critical_completeness * 0.7) + (source_completeness * 0.3)

def calculate_data_consistency(category_scores: Dict[str, float]) -> float:
    """
    Évalue la cohérence entre les différents scores catégorie.
    
    Args:
        category_scores: Scores par catégorie
        
    Returns:
        Score de cohérence (0-100)
    """
    if not category_scores:
        return 0
    
    scores = list(category_scores.values())
    mean = sum(scores) / len(scores)
    variance = sum((score - mean) ** 2 for score in scores) / len(scores)
    std_dev = variance ** 0.5
    
    # Convertir l'écart-type en score de cohérence
    # Plus l'écart-type est faible, plus les scores sont cohérents
    max_std_dev = 40  # Écart-type maximal attendu (scores entre 0 et 100)
    consistency = max(0, 100 - (std_dev / max_std_dev) * 100)
    
    return consistency

def identify_strengths_weaknesses(
    category_scores: Dict[str, float], 
    config: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Identifie les points forts et les points faibles du produit.
    
    Args:
        category_scores: Scores par catégorie
        config: Configuration du scorer
        
    Returns:
        Tuple avec deux listes: (points forts, points faibles)
    """
    strengths = []
    weaknesses = []
    
    # Seuils pour les forces et faiblesses
    strength_threshold = 70
    weakness_threshold = 40
    
    # Analyser les scores par catégorie
    for category, score in category_scores.items():
        category_display = {
            'market_potential': 'Potentiel de marché',
            'competition': 'Niveau de concurrence',
            'profitability': 'Rentabilité',
            'operational': 'Aspects opérationnels',
            'trend': 'Tendance'
        }
        
        display_name = category_display.get(category, category)
        
        if score >= strength_threshold:
            strengths.append({
                'category': category,
                'display_name': display_name,
                'score': score,
                'description': f"Fort {display_name.lower()}"
            })
        elif score <= weakness_threshold:
            weaknesses.append({
                'category': category,
                'display_name': display_name,
                'score': score,
                'description': f"Faible {display_name.lower()}"
            })
    
    # Trier par score (décroissant pour forces, croissant pour faiblesses)
    strengths.sort(key=lambda x: x['score'], reverse=True)
    weaknesses.sort(key=lambda x: x['score'])
    
    return strengths, weaknesses

def generate_score_explanation(
    overall_score: float,
    category_scores: Dict[str, float],
    strengths: List[Dict[str, Any]],
    weaknesses: List[Dict[str, Any]],
    confidence: float
) -> Dict[str, Any]:
    """
    Génère une explication détaillée du score.
    
    Args:
        overall_score: Score global du produit
        category_scores: Scores par catégorie
        strengths: Liste des points forts
        weaknesses: Liste des points faibles
        confidence: Niveau de confiance dans le score
        
    Returns:
        Explication structurée du score
    """
    explanation = {
        'summary': "",
        'key_factors': [],
        'confidence_statement': ""
    }
    
    # Résumé basé sur le score global
    if overall_score >= 75:
        explanation['summary'] = "Ce produit présente un excellent potentiel pour le dropshipping avec un score global élevé."
    elif overall_score >= 60:
        explanation['summary'] = "Ce produit présente un bon potentiel pour le dropshipping avec un score global satisfaisant."
    elif overall_score >= 40:
        explanation['summary'] = "Ce produit présente un potentiel limité pour le dropshipping avec un score global moyen."
    else:
        explanation['summary'] = "Ce produit présente un faible potentiel pour le dropshipping avec un score global bas."
    
    # Facteurs clés basés sur les forces et faiblesses
    for strength in strengths[:2]:  # Limiter aux 2 principales forces
        explanation['key_factors'].append(
            f"+ {strength['display_name']} ({strength['score']}/100): {strength['description']}"
        )
    
    for weakness in weaknesses[:2]:  # Limiter aux 2 principales faiblesses
        explanation['key_factors'].append(
            f"- {weakness['display_name']} ({weakness['score']}/100): {weakness['description']}"
        )
    
    # Déclaration de confiance
    if confidence >= 80:
        explanation['confidence_statement'] = f"L'évaluation est très fiable avec un niveau de confiance de {confidence:.0f}%."
    elif confidence >= 60:
        explanation['confidence_statement'] = f"L'évaluation est fiable avec un niveau de confiance de {confidence:.0f}%."
    elif confidence >= 40:
        explanation['confidence_statement'] = f"L'évaluation est modérément fiable avec un niveau de confiance de {confidence:.0f}%. Des données supplémentaires amélioreraient la précision."
    else:
        explanation['confidence_statement'] = f"L'évaluation a une fiabilité limitée avec un niveau de confiance de {confidence:.0f}%. Des données supplémentaires sont nécessaires pour une évaluation plus précise."
    
    return explanation
