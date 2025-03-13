#!/usr/bin/env python3
"""
Module d'analyse SEO pour l'agent Data Analyzer.
Ce module fournit des classes et fonctions pour analyser les données SEO
de différentes sources (SEMrush, Ahrefs, etc.).
"""

__version__ = '0.1.0'

# Import des analyseurs
try:
    from .semrush_analyzer import SEMrushAnalyzer
except ImportError:
    SEMrushAnalyzer = None

try:
    from .ahrefs_analyzer import AhrefsAnalyzer
except ImportError:
    AhrefsAnalyzer = None

# Factory function pour créer l'analyseur SEO approprié
def create_seo_analyzer(source='semrush', **kwargs):
    """
    Crée une instance de l'analyseur SEO approprié.
    
    Args:
        source (str): Source des données SEO ('semrush', 'ahrefs', etc.)
        **kwargs: Arguments supplémentaires pour l'analyseur
        
    Returns:
        Un analyseur SEO configurable
        
    Raises:
        ImportError: Si l'analyseur demandé n'est pas disponible
    """
    if source.lower() == 'semrush':
        if SEMrushAnalyzer is None:
            raise ImportError("SEMrushAnalyzer n'est pas disponible")
        return SEMrushAnalyzer(**kwargs)
    
    elif source.lower() == 'ahrefs':
        if AhrefsAnalyzer is None:
            raise ImportError("AhrefsAnalyzer n'est pas disponible")
        return AhrefsAnalyzer(**kwargs)
    
    else:
        raise ValueError(f"Source SEO inconnue: {source}")
