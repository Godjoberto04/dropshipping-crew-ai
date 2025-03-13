"""
Module de scoring pour évaluer les produits selon plusieurs critères.
"""

from models.scoring.base import ProductScorer
from models.scoring.multicriteria import AdvancedProductScorer

__all__ = ['ProductScorer', 'AdvancedProductScorer']
