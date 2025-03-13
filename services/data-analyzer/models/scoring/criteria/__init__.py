"""
Module contenant les fonctions d'évaluation pour les différents critères
du système de scoring multicritères.
"""

from models.scoring.criteria.market import score_search_volume, score_growth_rate, score_market_size
from models.scoring.criteria.competition import score_competitor_count, score_price_competition, score_barriers_to_entry
from models.scoring.criteria.profitability import score_margin, score_price_stability, score_upsell_potential
from models.scoring.criteria.operational import score_shipping_complexity, score_return_rate, score_supplier_reliability
from models.scoring.criteria.trend import score_trend_consistency, score_seasonality, score_social_mentions

__all__ = [
    'score_search_volume', 'score_growth_rate', 'score_market_size',
    'score_competitor_count', 'score_price_competition', 'score_barriers_to_entry',
    'score_margin', 'score_price_stability', 'score_upsell_potential',
    'score_shipping_complexity', 'score_return_rate', 'score_supplier_reliability',
    'score_trend_consistency', 'score_seasonality', 'score_social_mentions'
]
