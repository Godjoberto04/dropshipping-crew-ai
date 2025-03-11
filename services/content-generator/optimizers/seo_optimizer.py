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
    
    def optimize(
        self,
        content: str,
        keywords: List[str],
        content_type: str = "product_description"
    ) -> str:
        """
        Optimise un contenu pour le SEO.
        
        Args:
            content: Contenu à optimiser
            keywords: Liste des mots-clés cibles
            content_type: Type de contenu (product_description, category_page, blog_article)
            
        Returns:
            Contenu optimisé
        """
        logger.info(f"Optimisation SEO pour contenu de type {content_type} avec {len(keywords)} mots-clés")
        
        # Analyse initiale
        initial_densities = self.analyze_keyword_density(content, keywords)
        logger.debug(f"Densités initiales: {initial_densities}")
        
        # Version optimisée du contenu (pour l'instant, identique)
        optimized_content = content
        
        # Vérifier la présence des mots-clés dans les titres (h1, h2, h3)
        heading_matches = 0
        headings = re.findall(r'(#{1,3})\s+(.+)$', content, re.MULTILINE)
        
        if headings:
            for heading_level, heading_text in headings:
                if any(keyword.lower() in heading_text.lower() for keyword in keywords):
                    heading_matches += 1
        
        # Si aucun mot-clé dans les titres, suggérer des améliorations
        if len(headings) > 0 and heading_matches == 0:
            logger.debug("Aucun mot-clé trouvé dans les titres")
            # Dans cette version de base, nous ne modifions pas automatiquement les titres
            # Mais une version plus avancée pourrait le faire
        
        # Vérifier la présence des mots-clés dans les premiers et derniers paragraphes
        paragraphs = re.split(r'\n\s*\n', content)
        
        # Vérifications basiques (pour cette version simplifiée)
        if len(paragraphs) < self.min_paragraph_count:
            logger.debug(f"Nombre de paragraphes insuffisant: {len(paragraphs)} < {self.min_paragraph_count}")
        
        # Pour l'instant, cette première version ne modifie pas le contenu
        # mais effectue une analyse et des recommandations.
        # Une future version pourrait automatiquement améliorer le contenu.
        
        return optimized_content
    
    def generate_meta_description(
        self,
        content: str,
        product_name: str,
        max_length: int = 160
    ) -> str:
        """
        Génère une méta-description optimisée SEO à partir du contenu.
        
        Args:
            content: Contenu à analyser
            product_name: Nom du produit ou titre principal
            max_length: Longueur maximale de la méta-description
            
        Returns:
            Méta-description optimisée
        """
        # Extraire le premier paragraphe (généralement l'introduction)
        paragraphs = re.split(r'\n\s*\n', content.strip())
        
        # Supprimer les titres markdown
        paragraphs = [re.sub(r'^#{1,6}\s+.*$', '', p, flags=re.MULTILINE) for p in paragraphs]
        
        # Trouver le premier paragraphe non vide
        first_paragraph = ""
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('*') and not p.startswith('#'):
                first_paragraph = p
                break
        
        if not first_paragraph:
            # Fallback: utiliser le contenu complet
            first_paragraph = re.sub(r'#{1,6}\s+', '', content)
        
        # Nettoyer le paragraphe (supprimer les sauts de ligne, espaces multiples, etc.)
        first_paragraph = re.sub(r'\s+', ' ', first_paragraph).strip()
        
        # S'assurer que le nom du produit est présent
        if product_name.lower() not in first_paragraph.lower():
            first_paragraph = f"{product_name} - {first_paragraph}"
        
        # Tronquer à la bonne longueur en respectant les mots complets
        if len(first_paragraph) <= max_length:
            return first_paragraph
        
        # Trouver le dernier espace avant la limite de longueur
        truncate_index = first_paragraph.rfind(' ', 0, max_length - 3)
        if truncate_index == -1:
            # Si pas d'espace trouvé, simplement tronquer
            truncate_index = max_length - 3
        
        return first_paragraph[:truncate_index] + "..."
    
    def calculate_improvement_score(
        self,
        original_content: str,
        optimized_content: str
    ) -> float:
        """
        Calcule un score d'amélioration entre le contenu original et optimisé.
        
        Args:
            original_content: Contenu original
            optimized_content: Contenu optimisé
            
        Returns:
            Score d'amélioration (0-100)
        """
        # Cette méthode est très simplifiée pour la première version
        # Une version plus complète pourrait analyser plusieurs facteurs
        
        # Pour l'instant, retourne un score basé uniquement sur la différence de longueur
        original_words = len(re.findall(r'\b\w+\b', original_content))
        optimized_words = len(re.findall(r'\b\w+\b', optimized_content))
        
        # Si le contenu optimisé est plus court, considérer qu'il n'y a pas d'amélioration
        if optimized_words <= original_words:
            return 0.0
        
        # Calculer l'amélioration en pourcentage (plafonné à 20%)
        improvement = min((optimized_words - original_words) / original_words * 100, 20.0)
        
        # Attribuer un score de base de 80% + l'amélioration
        return 80.0 + improvement