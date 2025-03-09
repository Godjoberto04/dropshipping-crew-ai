import logging
import time
import random
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class SimpleTrendAnalysisTool:
    """Outil pour analyser les tendances des produits et la concurrence"""
    
    def analyze_trends(self, products: List[Dict], market_segment: str = None) -> Dict[str, Any]:
        """
        Analyse les tendances des produits et évalue le niveau de concurrence
        
        Args:
            products: Liste de produits à analyser
            market_segment: Segment de marché ciblé (optionnel)
            
        Returns:
            Dictionnaire contenant l'analyse des tendances et de la concurrence
        """
        if not products:
            return {"error": "Aucun produit à analyser"}
        
        logger.info(f"Analyse des tendances pour {len(products)} produits")
        
        # Simulation de données de tendances pour chaque produit
        # Dans une implémentation réelle, cette partie ferait appel à des APIs externes
        # ou à des modèles d'apprentissage automatique
        
        results = []
        for product in products:
            # Évaluation de la concurrence (Low, Medium, High)
            competition_level, competition_score = self._evaluate_competition(product)
            
            # Détermination de la direction de la tendance (Up, Stable, Down)
            trend_direction, trend_score = self._evaluate_trend(product, market_segment)
            
            # Calcul du score de recommandation global (0-10)
            # On combine le score de marge (si disponible) avec les scores de concurrence et de tendance
            margin_score = product.get('margin_score', 0)
            recommendation_score = self._calculate_recommendation_score(
                margin_score, competition_score, trend_score
            )
            
            # Génération d'une justification détaillée
            justification = self._generate_justification(
                product, competition_level, trend_direction, recommendation_score
            )
            
            # Construction du résultat pour ce produit
            product_result = {
                "name": product.get('name', 'Produit inconnu'),
                "supplier_price": product.get('supplier_price', product.get('estimated_supplier_price', 0)),
                "market_price": product.get('price', product.get('market_price', 0)),
                "recommended_price": product.get('recommended_price', 0),
                "potential_margin_percent": product.get('potential_margin_percent', 0),
                "competition_level": competition_level,
                "trend_direction": trend_direction,
                "recommendation_score": round(recommendation_score, 1),
                "justification": justification
            }
            
            # Ajouter d'autres métadonnées si disponibles
            if 'image_url' in product:
                product_result['image_url'] = product['image_url']
            
            results.append(product_result)
        
        # Trier les résultats par score de recommandation
        results = sorted(results, key=lambda x: x['recommendation_score'], reverse=True)
        
        logger.info(f"Analyse des tendances terminée: {len(results)} produits analysés")
        
        return {
            "analyzed_count": len(products),
            "top_products": results[:10],  # Limiter aux 10 meilleurs produits
            "market_segment": market_segment,
            "timestamp": time.time()
        }
    
    def _evaluate_competition(self, product: Dict) -> Tuple[str, float]:
        """
        Évalue le niveau de concurrence pour un produit
        
        Args:
            product: Données du produit
            
        Returns:
            Tuple (niveau de concurrence, score numérique)
        """
        # Simuler une évaluation de la concurrence
        # Dans une implémentation réelle, cette fonction utiliserait des données réelles
        
        # Facteurs qui augmentent la concurrence potentielle:
        # - Prix bas (produits bon marché ont généralement plus de concurrence)
        # - Produits "génériques" ou accessoires communs
        
        price = product.get('price', product.get('market_price', 0))
        name = product.get('name', '').lower()
        
        # Détection des mots-clés génériques qui suggèrent une forte concurrence
        high_competition_keywords = ['basic', 'simple', 'standard', 'case', 'cover', 'charger', 
                                    'cable', 'protector', 'support', 'holder', 'generic']
        
        # Détection des mots-clés suggérant une concurrence moyenne
        medium_competition_keywords = ['premium', 'advanced', 'wireless', 'smart', 'fast', 
                                      'portable', 'professional', 'durable']
        
        # Détection des mots-clés suggérant une faible concurrence
        low_competition_keywords = ['unique', 'exclusive', 'proprietary', 'innovative', 
                                   'specialized', 'custom', 'limited', 'patented']
        
        # Score de base basé sur le prix (0-100, plus c'est élevé, plus la concurrence est forte)
        # Les produits moins chers ont généralement plus de concurrence
        if price < 10:
            base_score = 80  # Concurrence potentiellement élevée pour les produits peu coûteux
        elif price < 30:
            base_score = 60  # Concurrence moyenne
        else:
            base_score = 40  # Concurrence potentiellement plus faible pour les produits coûteux
        
        # Ajustement du score en fonction des mots-clés dans le nom du produit
        for keyword in high_competition_keywords:
            if keyword in name:
                base_score += 15
                break
                
        for keyword in medium_competition_keywords:
            if keyword in name:
                base_score += 0  # Neutre
                break
                
        for keyword in low_competition_keywords:
            if keyword in name:
                base_score -= 20
                break
        
        # Normaliser le score sur 0-100
        competition_score = max(0, min(100, base_score))
        
        # Convertir le score en niveau de concurrence
        if competition_score >= 70:
            return "High", competition_score
        elif competition_score >= 40:
            return "Medium", competition_score
        else:
            return "Low", competition_score
    
    def _evaluate_trend(self, product: Dict, market_segment: str = None) -> Tuple[str, float]:
        """
        Évalue la direction de la tendance pour un produit
        
        Args:
            product: Données du produit
            market_segment: Segment de marché ciblé (optionnel)
            
        Returns:
            Tuple (direction de la tendance, score numérique)
        """
        # Simuler une évaluation de tendance
        # Dans une implémentation réelle, cette fonction utiliserait des données
        # de recherche Google Trends, de médias sociaux, etc.
        
        name = product.get('name', '').lower()
        
        # Mots-clés tendance pour les produits tech en 2025 (simulation)
        up_trend_keywords = ['wireless', 'magsafe', 'qi3', 'usb-c', 'fast charging', 
                            'foldable', 'ai', 'sustainable', 'eco', 'biodegradable',
                            'recycled', 'argent', 'premium', 'luxe', 'minimalist']
        
        # Mots-clés pour les produits stables
        stable_trend_keywords = ['case', 'stand', 'screen protector', 'power bank',
                                'bluetooth', 'portable', 'durable', 'waterproof']
        
        # Mots-clés pour les produits en déclin
        down_trend_keywords = ['wired', 'micro-usb', 'basic', 'lightning', 'non-magnetic',
                              'plastic', 'standard', 'bulky', 'generic']
        
        # Score de base (50 = stable)
        base_score = 50
        
        # Ajustement du score en fonction des mots-clés dans le nom du produit
        for keyword in up_trend_keywords:
            if keyword in name:
                base_score += 20
                break
                
        for keyword in stable_trend_keywords:
            if keyword in name:
                base_score += 0  # Neutre
                break
                
        for keyword in down_trend_keywords:
            if keyword in name:
                base_score -= 20
                break
        
        # Ajustement aléatoire avec une légère tendance positive
        # (simule l'incertitude du marché)
        randomness = np.random.normal(5, 10)  # Moyenne +5, écart-type 10
        base_score += randomness
        
        # Ajustement en fonction du segment de marché (si spécifié)
        if market_segment:
            market_segment = market_segment.lower()
            
            # Segments tendance en 2025 (simulation)
            trend_segments = ['smartphone accessories', 'sustainable tech', 
                             'wireless charging', 'smart home', 'eco-friendly']
            
            # Segments stables
            stable_segments = ['phone cases', 'screen protectors', 'cables', 
                              'power banks', 'phone stands']
            
            # Segments en déclin
            decline_segments = ['wired headphones', 'dvd accessories', 
                               'cd accessories', 'mp3 accessories']
            
            if any(segment in market_segment for segment in trend_segments):
                base_score += 15
            elif any(segment in market_segment for segment in stable_segments):
                base_score += 0  # Neutre
            elif any(segment in market_segment for segment in decline_segments):
                base_score -= 15
        
        # Normaliser le score sur 0-100
        trend_score = max(0, min(100, base_score))
        
        # Convertir le score en direction de tendance
        if trend_score >= 65:
            return "Up", trend_score
        elif trend_score >= 35:
            return "Stable", trend_score
        else:
            return "Down", trend_score
    
    def _calculate_recommendation_score(self, margin_score: float, 
                                      competition_score: float, 
                                      trend_score: float) -> float:
        """
        Calcule un score de recommandation global
        
        Args:
            margin_score: Score basé sur la marge (0-10)
            competition_score: Score basé sur la concurrence (0-100)
            trend_score: Score basé sur la tendance (0-100)
            
        Returns:
            Score de recommandation global (0-10)
        """
        # Normaliser les scores de concurrence et de tendance sur 0-10
        competition_score_norm = (100 - competition_score) / 10  # Inverser car un score de concurrence bas est meilleur
        trend_score_norm = trend_score / 10
        
        # Formule de recommandation: 
        # 50% marge + 25% concurrence inverse + 25% tendance
        recommendation_score = (
            0.5 * margin_score + 
            0.25 * competition_score_norm + 
            0.25 * trend_score_norm
        )
        
        # Limiter le score entre 0 et 10
        return max(0, min(10, recommendation_score))
    
    def _generate_justification(self, product: Dict, competition_level: str, 
                              trend_direction: str, recommendation_score: float) -> str:
        """
        Génère une justification détaillée pour un produit
        
        Args:
            product: Données du produit
            competition_level: Niveau de concurrence
            trend_direction: Direction de la tendance
            recommendation_score: Score de recommandation
            
        Returns:
            Justification textuelle
        """
        name = product.get('name', 'Ce produit')
        margin = product.get('potential_margin_percent', 0)
        
        # Modèle de justification
        justification = f"{name} "
        
        # Partie sur la marge
        if margin >= 70:
            justification += f"offre une marge exceptionnelle de {margin:.1f}%. "
        elif margin >= 50:
            justification += f"présente une très bonne marge de {margin:.1f}%. "
        elif margin >= 30:
            justification += f"a une marge acceptable de {margin:.1f}%. "
        else:
            justification += f"a une marge limitée de {margin:.1f}%. "
        
        # Partie sur la concurrence
        if competition_level == "Low":
            justification += "La concurrence est faible, ce qui représente une excellente opportunité. "
        elif competition_level == "Medium":
            justification += "La concurrence est modérée, ce qui laisse une place pour se différencier. "
        else:
            justification += "La concurrence est élevée, une stratégie de différenciation sera nécessaire. "
        
        # Partie sur la tendance
        if trend_direction == "Up":
            justification += "Ce produit est en tendance à la hausse, ce qui suggère un bon potentiel de croissance. "
        elif trend_direction == "Stable":
            justification += "La tendance est stable, ce qui indique une demande constante. "
        else:
            justification += "La tendance est à la baisse, ce qui pourrait limiter le potentiel à long terme. "
        
        # Conclusion basée sur le score de recommandation
        if recommendation_score >= 8.5:
            justification += "C'est une excellente opportunité de dropshipping avec un très fort potentiel de rentabilité."
        elif recommendation_score >= 7:
            justification += "C'est une bonne opportunité de dropshipping avec un bon potentiel de rentabilité."
        elif recommendation_score >= 5:
            justification += "C'est une opportunité moyenne de dropshipping qui mérite d'être considérée."
        else:
            justification += "C'est une opportunité limitée de dropshipping à considérer avec prudence."
        
        return justification
