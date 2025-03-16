import os
import json
import logging
import re
import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SEOMetaGenerator:
    """
    Générateur de méta-données SEO intelligent pour les pages e-commerce
    
    Cette classe génère des balises meta optimisées pour les différents types de pages
    d'une boutique de dropshipping, en se basant sur les données produits, la niche,
    et l'analyse concurrentielle.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialise le générateur de méta-données SEO
        
        Args:
            config: Configuration optionnelle pour personnaliser le comportement du générateur
        """
        self.config = {
            'maxTitleLength': 60,
            'maxDescriptionLength': 160,
            'includeBrand': True,
            'includePrice': False,
            'includeBenefits': True,
            'includeEmotionalTriggers': True,
            'maxKeywords': 10,
            'shop_name': os.getenv('SHOP_NAME', 'Notre Boutique')
        }
        
        # Fusionner avec la configuration fournie
        if config:
            self.config.update(config)
        
        # Dictionnaire d'accroches émotionnelles par niche
        self.emotional_triggers = {
            'fashion': ['Tendance', 'Élégant', 'Stylé', 'Luxueux', 'Incontournable'],
            'electronics': ['Innovant', 'Puissant', 'Intelligent', 'High-Tech', 'Performant'],
            'homeDecor': ['Élégant', 'Unique', 'Cosy', 'Moderne', 'Intemporel'],
            'beauty': ['Rajeunissant', 'Naturel', 'Efficace', 'Professionnel', 'Revitalisant'],
            'fitness': ['Performant', 'Efficace', 'Professionnel', 'Révolutionnaire', 'Énergisant']
        }
        
        # Templates pour les titres et descriptions
        self.templates = {
            'title': {
                'default': '{emotionalTrigger} {productName} | {shopName}',
                'withPrice': '{emotionalTrigger} {productName} - {price} | {shopName}',
                'withBenefit': '{emotionalTrigger} {productName} - {primaryBenefit} | {shopName}'
            },
            'description': {
                'default': 'Découvrez notre {emotionalTrigger} {productName}. {primaryBenefit} et {secondaryBenefit}. Livraison rapide, paiement sécurisé, satisfaction garantie !',
                'withFeatures': 'Notre {emotionalTrigger} {productName} vous impressionnera. Caractéristiques : {keyFeatures}. {primaryBenefit} et plus. Commandez maintenant !',
                'withTestimonial': 'Nos clients adorent notre {productName} : "{testimonialSnippet}". {primaryBenefit} et {secondaryBenefit}. Commandez aujourd\'hui !'
            }
        }
        
        logger.info("Générateur de méta-données SEO initialisé")
    
    def generate_metadata(self, page_data: Dict[str, Any], shop_info: Dict[str, Any], niche: str) -> Dict[str, Any]:
        """
        Génère les méta-données SEO complètes pour une page
        
        Args:
            page_data: Données de la page (produit, catégorie, etc.)
            shop_info: Informations sur la boutique
            niche: Niche ou catégorie principale de la boutique
            
        Returns:
            Dictionnaire contenant toutes les méta-données générées
        """
        logger.info(f"Génération de méta-données SEO pour : {page_data.get('name', 'Page inconnue')}")
        
        # Déterminer le type de page
        page_type = page_data.get('type', 'product')
        
        # Générer les différentes méta-données selon le type de page
        if page_type == 'product':
            title = self._generate_product_title(page_data, shop_info, niche)
            description = self._generate_product_description(page_data, shop_info, niche)
            canonical_url = self._generate_canonical_url(page_data, shop_info)
            structured_data = self._generate_product_structured_data(page_data, shop_info)
        elif page_type == 'collection':
            title = self._generate_collection_title(page_data, shop_info, niche)
            description = self._generate_collection_description(page_data, shop_info, niche)
            canonical_url = self._generate_canonical_url(page_data, shop_info)
            structured_data = self._generate_collection_structured_data(page_data, shop_info)
        elif page_type == 'page':
            title = self._generate_page_title(page_data, shop_info)
            description = self._generate_page_description(page_data, shop_info)
            canonical_url = self._generate_canonical_url(page_data, shop_info)
            structured_data = self._generate_page_structured_data(page_data, shop_info)
        elif page_type == 'blog':
            title = self._generate_blog_title(page_data, shop_info)
            description = self._generate_blog_description(page_data, shop_info)
            canonical_url = self._generate_canonical_url(page_data, shop_info)
            structured_data = self._generate_blog_structured_data(page_data, shop_info)
        else:
            title = self._generate_default_title(page_data, shop_info)
            description = self._generate_default_description(page_data, shop_info)
            canonical_url = self._generate_canonical_url(page_data, shop_info)
            structured_data = {}
        
        # Générer Open Graph et Twitter Card
        open_graph = self._generate_open_graph(page_data, shop_info, title, description)
        twitter_card = self._generate_twitter_card(page_data, shop_info, title, description)
        
        # Générer les keywords
        keywords = self._generate_keywords(page_data, niche)
        
        # Assembler toutes les méta-données
        return {
            'title': title,
            'description': description,
            'canonical': canonical_url,
            'structuredData': structured_data,
            'openGraph': open_graph,
            'twitterCard': twitter_card,
            'keywords': keywords
        }
    
    def _generate_product_title(self, product: Dict[str, Any], shop_info: Dict[str, Any], niche: str) -> str:
        """
        Génère un titre optimisé pour une page produit
        
        Args:
            product: Données du produit
            shop_info: Informations sur la boutique
            niche: Niche ou catégorie principale
            
        Returns:
            Titre optimisé pour le SEO
        """
        # Sélectionner un déclencheur émotionnel basé sur la niche
        emotional_trigger = self._get_emotional_trigger(niche)
        
        # Choisir le template en fonction de la configuration
        template = self.templates['title']['default']
        if self.config['includePrice'] and product.get('price'):
            template = self.templates['title']['withPrice']
        elif self.config['includeBenefits'] and product.get('benefits') and len(product.get('benefits', [])) > 0:
            template = self.templates['title']['withBenefit']
        
        # Remplir le template avec les données
        title = template.replace('{emotionalTrigger}', emotional_trigger)
        title = title.replace('{productName}', product.get('name', product.get('title', 'Produit')))
        title = title.replace('{shopName}', shop_info.get('name', self.config['shop_name']))
        
        if '{price}' in title and product.get('price'):
            price_str = f"{product['price']} {product.get('currency', '€')}"
            title = title.replace('{price}', price_str)
        
        if '{primaryBenefit}' in title and product.get('benefits') and len(product.get('benefits', [])) > 0:
            title = title.replace('{primaryBenefit}', product['benefits'][0])
        
        # S'assurer que le titre n'est pas trop long
        if len(title) > self.config['maxTitleLength']:
            title = title[:self.config['maxTitleLength'] - 3] + '...'
        
        return title
    
    def _generate_product_description(self, product: Dict[str, Any], shop_info: Dict[str, Any], niche: str) -> str:
        """
        Génère une méta-description optimisée pour une page produit
        
        Args:
            product: Données du produit
            shop_info: Informations sur la boutique
            niche: Niche ou catégorie principale
            
        Returns:
            Description optimisée pour le SEO
        """
        # Sélectionner un déclencheur émotionnel basé sur la niche
        emotional_trigger = self._get_emotional_trigger(niche)
        
        # Choisir le template en fonction des données disponibles
        template = self.templates['description']['default']
        if product.get('features') and len(product.get('features', [])) >= 3:
            template = self.templates['description']['withFeatures']
        elif product.get('testimonials') and len(product.get('testimonials', [])) > 0:
            template = self.templates['description']['withTestimonial']
        
        # Remplir le template avec les données
        description = template.replace('{emotionalTrigger}', emotional_trigger.lower())
        description = description.replace('{productName}', product.get('name', product.get('title', 'produit')))
        
        # Gestion des avantages principaux et secondaires
        primary_benefit = "produit de haute qualité"
        secondary_benefit = "excellent rapport qualité-prix"
        
        if product.get('benefits') and len(product.get('benefits', [])) > 0:
            primary_benefit = product['benefits'][0]
            if len(product.get('benefits', [])) > 1:
                secondary_benefit = product['benefits'][1]
        
        description = description.replace('{primaryBenefit}', primary_benefit)
        description = description.replace('{secondaryBenefit}', secondary_benefit)
        
        # Gestion des caractéristiques clés
        if '{keyFeatures}' in description and product.get('features'):
            key_features = ', '.join(product['features'][:3])
            description = description.replace('{keyFeatures}', key_features)
        
        # Gestion des témoignages
        if '{testimonialSnippet}' in description and product.get('testimonials'):
            testimonial_text = product['testimonials'][0].get('text', '')
            if len(testimonial_text) > 50:
                testimonial_text = testimonial_text[:47] + '...'
            description = description.replace('{testimonialSnippet}', testimonial_text)
        
        # S'assurer que la description n'est pas trop longue
        if len(description) > self.config['maxDescriptionLength']:
            description = description[:self.config['maxDescriptionLength'] - 3] + '...'
        
        return description