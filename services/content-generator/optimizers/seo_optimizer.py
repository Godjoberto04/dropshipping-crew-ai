"""
Module d'optimisation SEO pour le Content Generator
"""

import logging
import re
from typing import Dict, List, Any, Optional
import string
from collections import Counter

logger = logging.getLogger("content_generator.seo_optimizer")

class SEOOptimizer:
    """
    Optimiseur SEO pour différents types de contenu.
    
    Cette classe fournit des méthodes pour optimiser les contenus générés
    selon les meilleures pratiques SEO, analyser la densité des mots-clés,
    et générer des méta-données.
    """
    
    def __init__(self):
        """
        Initialise l'optimiseur SEO avec des paramètres par défaut.
        """
        # Densité de mots-clés cible (en pourcentage)
        self.keyword_density_target = 2.0
        
        # Seuils pour différentes métriques
        self.min_heading_count = 2
        self.min_paragraph_count = 3
        self.optimal_sentence_length = 20
        self.max_sentence_length = 40
        
        # Mots à éviter ou à limiter
        self.stop_words = self._load_stop_words()
        
        logger.info("Optimiseur SEO initialisé")
    
    def _load_stop_words(self) -> List[str]:
        """
        Charge la liste des mots vides (stop words) en français.
        
        Returns:
            Liste des mots vides
        """
        # Liste basique des mots vides en français
        return [
            "le", "la", "les", "un", "une", "des", "du", "de", "a", "au", "aux",
            "ce", "ces", "cette", "et", "ou", "mais", "donc", "car", "pour", "par",
            "dans", "sur", "avec", "sans", "en", "qui", "que", "quoi", "dont", "où",
            "comment", "quand", "pourquoi", "est", "sont", "sera", "seront", "était",
            "étaient", "je", "tu", "il", "elle", "nous", "vous", "ils", "elles",
            "mon", "ton", "son", "notre", "votre", "leur", "mes", "tes", "ses",
            "nos", "vos", "leurs", "se", "si", "plus", "moins", "très", "tout"
        ]
    
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        Extrait automatiquement les mots-clés potentiels d'un texte.
        
        Args:
            text: Texte à analyser
            max_keywords: Nombre maximum de mots-clés à extraire
            
        Returns:
            Liste des mots-clés potentiels
        """
        # Tokenisation simple (séparation des mots)
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filtrer les mots vides et les mots courts
        filtered_words = [word for word in words if word not in self.stop_words and len(word) > 3]
        
        # Compter les occurrences
        word_counts = Counter(filtered_words)
        
        # Renvoyer les N mots les plus fréquents
        return [word for word, _ in word_counts.most_common(max_keywords)]
    
    def analyze_keyword_density(self, text: str, keywords: List[str]) -> Dict[str, float]:
        """
        Analyse la densité des mots-clés dans un texte.
        
        Args:
            text: Texte à analyser
            keywords: Liste des mots-clés à rechercher
            
        Returns:
            Dictionnaire avec la densité de chaque mot-clé
        """
        # Tokenisation simple (séparation des mots)
        words = re.findall(r'\b\w+\b', text.lower())
        total_words = len(words)
        
        if total_words == 0:
            return {keyword: 0.0 for keyword in keywords}
        
        # Calculer la densité pour chaque mot-clé
        densities = {}
        for keyword in keywords:
            # Compter les occurrences du mot-clé (peut être composé de plusieurs mots)
            keyword_parts = keyword.lower().split()
            
            if len(keyword_parts) == 1:
                # Mot-clé simple
                count = sum(1 for word in words if word == keyword.lower())
            else:
                # Mot-clé composé (phrase)
                keyword_pattern = r'\b' + r'\s+'.join(keyword_parts) + r'\b'
                count = len(re.findall(keyword_pattern, text.lower()))
            
            # Calculer la densité en pourcentage
            density = (count / total_words) * 100
            densities[keyword] = density
        
        return densities