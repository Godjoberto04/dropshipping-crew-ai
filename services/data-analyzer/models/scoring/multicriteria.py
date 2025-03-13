#!/usr/bin/env python3
"""
Système de scoring multicritères avancé pour évaluer les produits de dropshipping.
Ce module implémente une évaluation sophistiquée basée sur différentes catégories de critères
pondérés dynamiquement.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import math

from config import settings, get_logger
from models.scoring.base import ProductScorer
from models.scoring.criteria import (
    # Potentiel de marché
    score_search_volume, score_growth_rate, score_market_size,
    # Concurrence
    score_competitor_count, score_price_competition, score_barriers_to_entry,
    # Profitabilité
    score_margin, score_price_stability, score_upsell_potential,
    # Aspects opérationnels
    score_shipping_complexity, score_return_rate, score_supplier_reliability,
    # Tendances
    score_trend_consistency, score_seasonality, score_social_mentions
)
from models.scoring.multicriteria_core import (
    apply_niche_optimizations,
    calculate_category_score,
    calculate_confidence,
    identify_strengths_weaknesses,
    generate_score_explanation,
    get_recommendation
)

logger = get_logger("advanced_scorer")

class AdvancedProductScorer(ProductScorer):
    """
    Système de scoring multicritères avancé pour les produits de dropshipping.
    Évalue les produits sur 10-15 critères répartis en 5 catégories principales
    avec une pondération dynamique.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le système de scoring avancé.
        
        Args:
            config: Configuration optionnelle pour le scorer
        """
        super().__init__(config)
        
        # Initialisation des adaptateurs pour les sources de données
        self.data_sources = {}
        
        # Chargement des optimisations par niche
        self.niche_optimizations = self._load_niche_optimizations()
        
        # Mapping des critères vers les fonctions d'évaluation
        self.criterion_functions = {
            'search_volume': score_search_volume,
            'growth_rate': score_growth_rate,
            'market_size': score_market_size,
            'competitor_count': score_competitor_count,
            'price_competition': score_price_competition,
            'barriers_to_entry': score_barriers_to_entry,
            'margin': score_margin,
            'price_stability': score_price_stability,
            'upsell_potential': score_upsell_potential,
            'shipping_complexity': score_shipping_complexity,
            'return_rate': score_return_rate,
            'supplier_reliability': score_supplier_reliability,
            'trend_consistency': score_trend_consistency,
            'seasonality': score_seasonality,
            'social_mentions': score_social_mentions
        }
        
        logger.info(f"Système de scoring multicritères initialisé avec {len(self.config['criteria'])} catégories")
    
    def _default_config(self) -> Dict[str, Any]:
        """
        Retourne la configuration par défaut du scorer.
        
        Returns:
            Dictionnaire de configuration par défaut
        """
        return {
            'weights': {
                'market_potential': 0.30,  # Potentiel de marché
                'competition': 0.20,       # Niveau de concurrence
                'profitability': 0.25,     # Rentabilité
                'operational': 0.15,       # Complexité opérationnelle
                'trend': 0.10              # Tendance et timing
            },
            'criteria': {
                'market_potential': [
                    {'name': 'search_volume', 'weight': 0.4, 'description': 'Volume de recherche mensuel'},
                    {'name': 'growth_rate', 'weight': 0.3, 'description': 'Taux de croissance du marché'},
                    {'name': 'market_size', 'weight': 0.3, 'description': 'Taille estimée du marché'}
                ],
                'competition': [
                    {'name': 'competitor_count', 'weight': 0.3, 'description': 'Nombre de concurrents directs'},
                    {'name': 'price_competition', 'weight': 0.4, 'description': 'Intensité de la concurrence par les prix'},
                    {'name': 'barriers_to_entry', 'weight': 0.3, 'description': 'Barrières à l\'entrée'}
                ],
                'profitability': [
                    {'name': 'margin', 'weight': 0.5, 'description': 'Marge brute estimée'},
                    {'name': 'price_stability', 'weight': 0.3, 'description': 'Stabilité des prix'},
                    {'name': 'upsell_potential', 'weight': 0.2, 'description': 'Potentiel de ventes additionnelles'}
                ],
                'operational': [
                    {'name': 'shipping_complexity', 'weight': 0.4, 'description': 'Complexité d\'expédition'},
                    {'name': 'return_rate', 'weight': 0.3, 'description': 'Taux de retour anticipé'},
                    {'name': 'supplier_reliability', 'weight': 0.3, 'description': 'Fiabilité du fournisseur'}
                ],
                'trend': [
                    {'name': 'trend_consistency', 'weight': 0.4, 'description': 'Consistance de la tendance'},
                    {'name': 'seasonality', 'weight': 0.3, 'description': 'Impact de la saisonnalité'},
                    {'name': 'social_mentions', 'weight': 0.3, 'description': 'Mentions sur les réseaux sociaux'}
                ]
            },
            'thresholds': {
                'high_potential': 75,     # Seuil pour le potentiel élevé
                'medium_potential': 60,   # Seuil pour le potentiel moyen
                'low_potential': 40       # Seuil pour le potentiel faible
            },
            'niche_adjustments': True,    # Activer les ajustements par niche
            'data_requirements': {
                'minimum_data_points': 7,  # Nombre minimum de données requises
                'critical_criteria': [     # Critères considérés comme critiques
                    'search_volume',
                    'margin',
                    'competitor_count'
                ]
            }
        }
    
    def _load_niche_optimizations(self) -> Dict[str, Dict[str, Any]]:
        """
        Charge les optimisations spécifiques par niche.
        
        Returns:
            Dictionnaire d'optimisations par niche
        """
        # Implémentation basique des optimisations par niche
        return {
            'fashion': {
                'weights': {
                    'trend': 0.15,           # La tendance est plus importante
                    'profitability': 0.20    # La profitabilité est légèrement réduite
                },
                'criteria_adjustments': {
                    'seasonality': 1.2,      # Importance accrue de la saisonnalité
                    'social_mentions': 1.5   # Importance accrue des mentions sociales
                }
            },
            'electronics': {
                'weights': {
                    'operational': 0.20,     # Les aspects opérationnels sont plus importants
                    'profitability': 0.20    # La profitabilité est légèrement réduite
                },
                'criteria_adjustments': {
                    'return_rate': 1.5,      # Importance accrue du taux de retour
                    'supplier_reliability': 1.4  # Importance accrue de la fiabilité fournisseur
                }
            },
            'home_decor': {
                'weights': {
                    'operational': 0.20,     # Les aspects opérationnels sont plus importants
                    'competition': 0.15      # La concurrence est moins importante
                },
                'criteria_adjustments': {
                    'shipping_complexity': 1.5,  # Importance accrue de la complexité d'expédition
                    'seasonality': 0.8       # Importance réduite de la saisonnalité
                }
            },
            'beauty': {
                'weights': {
                    'market_potential': 0.35, # Potentiel de marché plus important
                    'trend': 0.15            # La tendance est plus importante
                },
                'criteria_adjustments': {
                    'social_mentions': 1.8,   # Importance fortement accrue des mentions sociales
                    'margin': 1.2            # Importance accrue de la marge
                }
            },
            'fitness': {
                'weights': {
                    'market_potential': 0.35, # Potentiel de marché plus important
                    'competition': 0.15      # La concurrence est moins importante
                },
                'criteria_adjustments': {
                    'seasonality': 1.3,      # Importance accrue de la saisonnalité
                    'growth_rate': 1.2       # Importance accrue du taux de croissance
                }
            }
        }
    
    def register_data_source(self, source_name: str, source_instance: Any) -> None:
        """
        Enregistre une source de données à utiliser pour le scoring.
        
        Args:
            source_name: Nom de la source
            source_instance: Instance de la source de données
        """
        self.data_sources[source_name] = source_instance
        logger.info(f"Source de données '{source_name}' enregistrée")
    
    def gather_data(self, product_id: str, product_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Collecte toutes les données nécessaires auprès des différentes sources.
        
        Args:
            product_id: Identifiant du produit
            product_info: Informations de base sur le produit (optionnel)
            
        Returns:
            Dictionnaire avec toutes les données collectées
        """
        data = {'product_id': product_id}
        
        if product_info:
            data['basic_info'] = product_info
        
        # Collecte des données auprès de chaque source enregistrée
        for source_name, source in self.data_sources.items():
            try:
                if hasattr(source, 'analyze') and callable(source.analyze):
                    # Pour les analyseurs génériques
                    if source_name == 'trends' and product_info and 'keywords' in product_info:
                        # Cas spécial pour l'analyseur de tendances
                        data[source_name] = source.analyze(product_info.get('keywords', []))
                    elif source_name == 'marketplace':
                        # Cas spécial pour l'analyseur de marketplace
                        data[source_name] = source.analyze(product_id)
                    else:
                        # Cas général
                        data[source_name] = source.analyze(product_id)
                elif hasattr(source, f'analyze_{source_name}') and callable(getattr(source, f'analyze_{source_name}')):
                    # Pour les méthodes spécifiques
                    method = getattr(source, f'analyze_{source_name}')
                    data[source_name] = method(product_id)
                else:
                    logger.warning(f"Source '{source_name}' n'a pas de méthode d'analyse adaptée")
            except Exception as e:
                logger.warning(f"Erreur lors de la collecte des données depuis '{source_name}': {str(e)}")
                data[source_name] = {"error": str(e)}
        
        return data
    
    def score_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule le score d'un produit selon les différents critères.
        
        Args:
            product_data: Données du produit à évaluer
            
        Returns:
            Dictionnaire contenant le score global et les scores détaillés
        """
        product_id = product_data.get('id', 'unknown')
        product_name = product_data.get('name', 'Produit inconnu')
        niche = product_data.get('niche', '').lower()
        
        logger.info(f"Évaluation du produit: {product_name} (ID: {product_id})")
        
        # Collecter les données si pas déjà incluses
        if not any(k in product_data for k in ['trends', 'marketplace', 'seo', 'social']):
            data = self.gather_data(product_id, product_data)
        else:
            data = product_data
        
        # Appliquer les optimisations spécifiques à la niche si disponibles
        adjusted_config = apply_niche_optimizations(self.config, niche, self.niche_optimizations)
        
        # Initialiser les scores par catégorie
        category_scores = {}
        
        # Calculer le score pour chaque catégorie principale
        for category, criteria in adjusted_config['criteria'].items():
            category_scores[category] = calculate_category_score(
                category, 
                criteria, 
                data, 
                self.criterion_functions
            )
        
        # Calculer le score global pondéré
        overall_score = sum(
            category_scores[category] * adjusted_config['weights'][category]
            for category in category_scores
        )
        
        # Arrondir à une décimale
        overall_score = round(overall_score, 1)
        
        # Déterminer la recommandation
        recommendation = get_recommendation(overall_score, adjusted_config['thresholds'])
        
        # Calculer le score de confiance
        confidence_score = calculate_confidence(
            data, 
            category_scores, 
            adjusted_config['data_requirements'].get('critical_criteria', [])
        )
        
        # Identifier les points forts et points faibles
        strengths, weaknesses = identify_strengths_weaknesses(category_scores, adjusted_config)
        
        # Générer l'explication détaillée
        explanation = generate_score_explanation(
            overall_score,
            category_scores,
            strengths,
            weaknesses,
            confidence_score
        )
        
        # Préparer le résultat
        result = {
            'product_id': product_id,
            'product_name': product_name,
            'overall_score': overall_score,
            'category_scores': category_scores,
            'recommendation': recommendation,
            'confidence': confidence_score,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'explanation': explanation,
            'niche': niche,
            'niche_optimized': niche in self.niche_optimizations,
            'data_completeness': explanation.get('confidence_statement'),
            'scoring_timestamp': time.time()
        }
        
        return result
    
    def explain_score(self, score_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère une explication textuelle du score.
        
        Args:
            score_result: Résultat du scoring retourné par score_product
            
        Returns:
            Dictionnaire contenant des explications structurées du scoring
        """
        # Vérifier si l'explication est déjà incluse dans le résultat
        if 'explanation' in score_result:
            return score_result['explanation']
        
        # Sinon, générer une nouvelle explication
        overall_score = score_result.get('overall_score', 0)
        category_scores = score_result.get('category_scores', {})
        strengths = score_result.get('strengths', [])
        weaknesses = score_result.get('weaknesses', [])
        confidence = score_result.get('confidence', 0)
        
        return generate_score_explanation(
            overall_score,
            category_scores,
            strengths,
            weaknesses,
            confidence
        )
    
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
    
    def _apply_niche_optimizations(self, niche: str) -> Dict[str, Any]:
        """
        Applique les optimisations spécifiques à une niche.
        
        Args:
            niche: Niche du produit
            
        Returns:
            Configuration ajustée selon la niche
        """
        return apply_niche_optimizations(self.config, niche, self.niche_optimizations)
