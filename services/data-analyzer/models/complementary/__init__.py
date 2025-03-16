"""
Module d'analyse de complémentarité pour l'identification des produits associés.

Ce module permet d'identifier les produits complémentaires et les associations
fortes entre produits pour optimiser les stratégies de cross-sell et up-sell.
"""

from .complementary_analyzer import ComplementaryAnalyzer
from .association_rules import AssociationRulesMiner

__all__ = ['ComplementaryAnalyzer', 'AssociationRulesMiner']
