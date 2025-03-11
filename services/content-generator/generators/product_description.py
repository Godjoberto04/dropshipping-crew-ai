"""
Générateur de descriptions de produits
"""

import logging
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import re
import asyncio

from tools.claude_client import ClaudeClient

logger = logging.getLogger("content_generator.product_description")

class ProductDescriptionGenerator:
    """
    Générateur de descriptions de produits optimisées pour la conversion.
    
    Cette classe utilise Claude pour générer des descriptions de produits
    attrayantes et optimisées SEO à partir de données produit.
    """
    
    def __init__(
        self,
        claude_client: ClaudeClient,
        templates_dir: Path
    ):
        """
        Initialise le générateur de descriptions produit.
        
        Args:
            claude_client: Instance du client Claude pour la génération
            templates_dir: Répertoire contenant les templates de prompts
        """
        self.claude_client = claude_client
        self.templates_dir = templates_dir
        self.prompt_templates = self._load_prompt_templates()
        
        logger.info("Générateur de descriptions produit initialisé")
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """
        Charge les templates de prompts depuis les fichiers.
        
        Returns:
            Dictionnaire de templates par nom
        """
        templates = {}
        template_file = self.templates_dir / "product_templates.py"
        
        # Si le fichier existe, charger les templates
        if template_file.exists():
            try:
                # Importer le module dynamiquement
                import importlib.util
                spec = importlib.util.spec_from_file_location("product_templates", template_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Récupérer les templates définis dans le module
                templates = {name: getattr(module, name) for name in dir(module) 
                           if name.startswith('TEMPLATE_') and isinstance(getattr(module, name), str)}
                
                logger.info(f"Templates chargés: {list(templates.keys())}")
            except Exception as e:
                logger.error(f"Erreur lors du chargement des templates: {str(e)}")
        else:
            # Définir des templates par défaut
            templates = {
                "TEMPLATE_PRODUCT_DESCRIPTION_STANDARD": self._get_default_template()
            }
            logger.warning("Fichier de templates non trouvé, utilisation des templates par défaut")
        
        return templates
    
    def _get_default_template(self) -> str:
        """
        Renvoie le template de prompt par défaut pour les descriptions produit.
        
        Returns:
            Template de prompt par défaut
        """
        return """
        Tu es un rédacteur de descriptions produit professionnel pour une boutique e-commerce. 
        Tu dois créer une description de produit convaincante et optimisée SEO basée sur les informations suivantes.

        # Informations sur le produit
        {{product_info}}

        # Ton et style
        Ton: {{tone}}
        Langue: {{language}}
        Niche: {{niche}}

        # Instructions
        1. Commence par un titre accrocheur qui inclut le nom du produit
        2. Crée une introduction captivante qui présente le produit et ses principaux avantages
        3. Divise la description en sections avec des sous-titres (utilise le format Markdown)
        4. Inclus une section sur les caractéristiques principales du produit
        5. Explique les bénéfices du produit pour l'utilisateur, pas seulement ses caractéristiques
        6. Ajoute une section sur la qualité ou les matériaux si pertinent
        7. Termine par un appel à l'action convaincant
        8. Utilise un style {{tone}} et adapté à la niche {{niche}}
        9. N'invente pas de caractéristiques qui ne sont pas mentionnées dans les informations du produit
        10. Garde un format clair et facile à lire avec des paragraphes courts et des listes à puces

        # Format de la réponse
        Utilise le format Markdown avec des titres (##), des listes à puces (*) et des emphases (**) de manière appropriée.
        La description doit faire entre 300 et 500 mots, être engageante et persuasive.
        """
    
    def _format_product_info(self, product_data: Dict[str, Any]) -> str:
        """
        Formate les données produit en texte pour le prompt.
        
        Args:
            product_data: Données du produit
            
        Returns:
            Texte formaté avec les informations produit
        """
        formatted_info = []
        
        # Informations de base
        formatted_info.append(f"Nom du produit: {product_data.get('name', '')}")
        
        if 'description' in product_data:
            formatted_info.append(f"Description existante: {product_data.get('description', '')}")
        
        if 'price' in product_data:
            formatted_info.append(f"Prix: {product_data.get('price', '')}")
        
        if 'brand' in product_data:
            formatted_info.append(f"Marque: {product_data.get('brand', '')}")
        
        # Caractéristiques et spécifications
        if 'features' in product_data and product_data['features']:
            formatted_info.append("Caractéristiques:")
            for feature in product_data['features']:
                formatted_info.append(f"- {feature}")
        
        if 'specifications' in product_data and product_data['specifications']:
            formatted_info.append("Spécifications techniques:")
            for key, value in product_data['specifications'].items():
                formatted_info.append(f"- {key}: {value}")
        
        # Matériaux
        if 'materials' in product_data and product_data['materials']:
            formatted_info.append("Matériaux:")
            for material in product_data['materials']:
                formatted_info.append(f"- {material}")
        
        # Dimensions et poids
        if 'dimensions' in product_data:
            formatted_info.append(f"Dimensions: {product_data.get('dimensions', '')}")
        
        if 'weight' in product_data:
            formatted_info.append(f"Poids: {product_data.get('weight', '')}")
        
        # Autres informations
        if 'target_audience' in product_data:
            formatted_info.append(f"Public cible: {product_data.get('target_audience', '')}")
        
        if 'use_cases' in product_data and product_data['use_cases']:
            formatted_info.append("Cas d'utilisation:")
            for use_case in product_data['use_cases']:
                formatted_info.append(f"- {use_case}")
        
        if 'benefits' in product_data and product_data['benefits']:
            formatted_info.append("Bénéfices:")
            for benefit in product_data['benefits']:
                formatted_info.append(f"- {benefit}")
        
        return "\n".join(formatted_info)
    
    def _prepare_prompt(
        self,
        product_data: Dict[str, Any],
        tone: str,
        language: str,
        niche: str,
        template_key: Optional[str] = None
    ) -> str:
        """
        Prépare le prompt pour la génération de description produit.
        
        Args:
            product_data: Données du produit
            tone: Ton de la description (persuasif, informatif, etc.)
            language: Langue de la description
            niche: Niche ou catégorie du produit
            template_key: Clé du template à utiliser (si None, utilise le standard)
            
        Returns:
            Prompt formaté pour Claude
        """
        # Sélectionner le template
        if template_key and template_key in self.prompt_templates:
            template = self.prompt_templates[template_key]
        else:
            template = self.prompt_templates.get("TEMPLATE_PRODUCT_DESCRIPTION_STANDARD", self._get_default_template())
        
        # Formatter les informations produit
        product_info = self._format_product_info(product_data)
        
        # Remplacer les variables dans le template
        prompt = template.replace("{{product_info}}", product_info)
        prompt = prompt.replace("{{tone}}", tone)
        prompt = prompt.replace("{{language}}", language)
        prompt = prompt.replace("{{niche}}", niche)
        
        return prompt
    
    def _get_system_prompt(self, language: str, niche: str) -> str:
        """
        Génère le prompt système pour guider Claude.
        
        Args:
            language: Langue cible
            niche: Niche ou catégorie du produit
            
        Returns:
            Prompt système
        """
        return f"""
        Tu es un rédacteur de descriptions produit e-commerce expert, spécialisé dans la niche {niche}.
        Tu dois générer une description produit persuasive, en {language}, optimisée pour la conversion et le SEO.
        Concentre-toi sur les bénéfices pour l'utilisateur tout en mettant en avant les caractéristiques techniques importantes.
        Utilise un ton adapté à la niche et au type de produit. Structure clairement le contenu avec des titres et listes.
        """
    
    async def generate(
        self,
        product_data: Dict[str, Any],
        tone: str = "persuasive",
        language: str = "fr",
        niche: str = "general",
        template_key: Optional[str] = None
    ) -> str:
        """
        Génère une description de produit optimisée.
        
        Args:
            product_data: Données du produit
            tone: Ton de la description (persuasif, informatif, expert, etc.)
            language: Langue de la description
            niche: Niche ou catégorie du produit
            template_key: Clé du template à utiliser (si None, utilise le standard)
            
        Returns:
            Description de produit générée
        """
        logger.info(f"Génération de description pour produit: {product_data.get('name', 'Inconnu')}")
        
        # Vérification des données minimales requises
        if not product_data.get('name'):
            logger.warning("Nom du produit manquant dans les données")
            product_data['name'] = "Produit"
        
        # Adapter le template en fonction de la niche si nécessaire
        niche_specific_template = f"TEMPLATE_PRODUCT_DESCRIPTION_{niche.upper()}"
        if niche_specific_template in self.prompt_templates and not template_key:
            template_key = niche_specific_template
            logger.info(f"Utilisation du template spécifique à la niche: {template_key}")
        
        # Préparer le prompt
        prompt = self._prepare_prompt(
            product_data=product_data,
            tone=tone,
            language=language,
            niche=niche,
            template_key=template_key
        )
        
        # Obtenir le prompt système
        system_prompt = self._get_system_prompt(language, niche)
        
        # Générer la description
        try:
            description = await self.claude_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,  # Légère créativité pour les descriptions
                max_tokens=1500  # Limite adaptée aux descriptions de produits
            )
            
            # Nettoyer le résultat si nécessaire
            description = self._clean_description(description)
            
            logger.info(f"Description générée avec succès ({len(description)} caractères)")
            return description
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la description: {str(e)}", exc_info=True)
            raise
    
    def _clean_description(self, description: str) -> str:
        """
        Nettoie la description générée pour assurer une formatage cohérent.
        
        Args:
            description: Description brute générée par Claude
            
        Returns:
            Description nettoyée
        """
        # Supprimer les lignes vides multiples
        description = re.sub(r'\n{3,}', '\n\n', description)
        
        # Standardiser les titres markdown
        description = re.sub(r'^# ', '## ', description, flags=re.MULTILINE)
        
        # Standardiser les listes à puces
        description = re.sub(r'^[•◦▪-] ', '* ', description, flags=re.MULTILINE)
        
        # Vérifier si la description a un titre principal
        if not description.strip().startswith('#'):
            # Ajouter un titre par défaut si nécessaire
            first_line = description.strip().split('\n')[0]
            if not first_line.startswith('##'):
                description = f"## {first_line}\n\n" + '\n'.join(description.strip().split('\n')[1:])
        
        return description.strip()