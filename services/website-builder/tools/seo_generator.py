import os
import json
import logging
import re
import datetime
import random
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
        
        # Mots-clés communs par niche
        self.common_keywords = {
            'fashion': ['vêtement', 'mode', 'tendance', 'style', 'collection'],
            'electronics': ['électronique', 'tech', 'gadget', 'innovation', 'connecté'],
            'homeDecor': ['décoration', 'intérieur', 'maison', 'design', 'ameublement'],
            'beauty': ['beauté', 'soin', 'cosmétique', 'naturel', 'bio'],
            'fitness': ['sport', 'exercice', 'entraînement', 'santé', 'performance']
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
        
    def _generate_collection_title(self, collection: Dict[str, Any], shop_info: Dict[str, Any], niche: str) -> str:
        """
        Génère un titre optimisé pour une page de collection
        
        Args:
            collection: Données de la collection
            shop_info: Informations sur la boutique
            niche: Niche ou catégorie principale
            
        Returns:
            Titre optimisé pour le SEO
        """
        collection_name = collection.get('name', collection.get('title', 'Collection'))
        shop_name = shop_info.get('name', self.config['shop_name'])
        
        # Ajouter un élément émotionnel si configuré
        if self.config['includeEmotionalTriggers']:
            emotional_trigger = self._get_emotional_trigger(niche)
            title = f"{collection_name} {emotional_trigger} | {shop_name}"
        else:
            title = f"{collection_name} | {shop_name}"
        
        # S'assurer que le titre n'est pas trop long
        if len(title) > self.config['maxTitleLength']:
            title = title[:self.config['maxTitleLength'] - 3] + '...'
        
        return title
    
    def _generate_collection_description(self, collection: Dict[str, Any], shop_info: Dict[str, Any], niche: str) -> str:
        """
        Génère une méta-description optimisée pour une page de collection
        
        Args:
            collection: Données de la collection
            shop_info: Informations sur la boutique
            niche: Niche ou catégorie principale
            
        Returns:
            Description optimisée pour le SEO
        """
        collection_name = collection.get('name', collection.get('title', 'Collection'))
        shop_name = shop_info.get('name', self.config['shop_name'])
        
        # Obtenir un déclencheur émotionnel si configuré
        emotional_trigger = ""
        if self.config['includeEmotionalTriggers']:
            emotional_trigger = self._get_emotional_trigger(niche).lower() + "s "
        
        # Description par défaut
        description = f"Découvrez notre collection de {emotional_trigger}{collection_name} sur {shop_name}. "
        
        # Ajouter une partie de la description de la collection si disponible
        if collection.get('description'):
            # Nettoyer le HTML s'il est présent
            content = self._strip_html(collection['description'])
            
            if len(content) > 100:
                description += content[:100] + '...'
            else:
                description += content
        else:
            description += f"Produits de qualité, prix compétitifs, livraison rapide. Visitez notre boutique en ligne dès maintenant !"
        
        # S'assurer que la description n'est pas trop longue
        if len(description) > self.config['maxDescriptionLength']:
            description = description[:self.config['maxDescriptionLength'] - 3] + '...'
        
        return description
    
    def _generate_open_graph(self, page_data: Dict[str, Any], shop_info: Dict[str, Any], title: str, description: str) -> Dict[str, str]:
        """
        Génère les méta-données Open Graph pour le partage sur les réseaux sociaux
        
        Args:
            page_data: Données de la page
            shop_info: Informations sur la boutique
            title: Titre SEO déjà généré
            description: Description SEO déjà générée
            
        Returns:
            Dictionnaire des balises Open Graph
        """
        page_type = page_data.get('type', 'product')
        
        # Déterminer le type OG
        og_type = 'website'
        if page_type == 'product':
            og_type = 'product'
        elif page_type == 'blog':
            og_type = 'article'
        
        # Créer les balises Open Graph de base
        open_graph = {
            'og:title': title,
            'og:description': description,
            'og:type': og_type,
            'og:url': self._generate_canonical_url(page_data, shop_info),
            'og:site_name': shop_info.get('name', self.config['shop_name'])
        }
        
        # Ajouter une image si disponible
        if page_data.get('image') and isinstance(page_data['image'], dict) and 'src' in page_data['image']:
            open_graph['og:image'] = page_data['image']['src']
        elif page_data.get('image') and isinstance(page_data['image'], str):
            open_graph['og:image'] = page_data['image']
        elif page_data.get('images') and len(page_data.get('images', [])) > 0:
            image = page_data['images'][0]
            if isinstance(image, dict) and 'src' in image:
                open_graph['og:image'] = image['src']
            elif isinstance(image, str):
                open_graph['og:image'] = image
                
        # Ajouter des informations spécifiques au type de contenu
        if page_type == 'product' and page_data.get('price'):
            open_graph['product:price:amount'] = str(page_data['price'])
            open_graph['product:price:currency'] = page_data.get('currency', 'EUR')
        elif page_type == 'blog' and page_data.get('published_at'):
            open_graph['article:published_time'] = page_data['published_at']
            if page_data.get('updated_at'):
                open_graph['article:modified_time'] = page_data['updated_at']
            if page_data.get('author'):
                open_graph['article:author'] = page_data['author']
        
        return open_graph
    
    def _generate_twitter_card(self, page_data: Dict[str, Any], shop_info: Dict[str, Any], title: str, description: str) -> Dict[str, str]:
        """
        Génère les méta-données Twitter Card pour le partage sur Twitter
        
        Args:
            page_data: Données de la page
            shop_info: Informations sur la boutique
            title: Titre SEO déjà généré
            description: Description SEO déjà générée
            
        Returns:
            Dictionnaire des balises Twitter Card
        """
        page_type = page_data.get('type', 'product')
        
        # Déterminer le type de carte Twitter
        card_type = 'summary'
        if page_data.get('image') or (page_data.get('images') and len(page_data.get('images', [])) > 0):
            card_type = 'summary_large_image'
        
        # Créer les balises Twitter Card de base
        twitter_card = {
            'twitter:card': card_type,
            'twitter:title': title,
            'twitter:description': description
        }
        
        # Ajouter une image si disponible
        if page_data.get('image') and isinstance(page_data['image'], dict) and 'src' in page_data['image']:
            twitter_card['twitter:image'] = page_data['image']['src']
        elif page_data.get('image') and isinstance(page_data['image'], str):
            twitter_card['twitter:image'] = page_data['image']
        elif page_data.get('images') and len(page_data.get('images', [])) > 0:
            image = page_data['images'][0]
            if isinstance(image, dict) and 'src' in image:
                twitter_card['twitter:image'] = image['src']
            elif isinstance(image, str):
                twitter_card['twitter:image'] = image
        
        # Ajouter le site et le créateur si disponibles
        if shop_info.get('twitter_handle'):
            twitter_card['twitter:site'] = shop_info['twitter_handle']
        
        # Ajouter des informations spécifiques au type de contenu
        if page_type == 'product':
            twitter_card['twitter:label1'] = 'Prix'
            twitter_card['twitter:data1'] = f"{page_data.get('price', '')} {page_data.get('currency', 'EUR')}"
            
            if page_data.get('availability'):
                twitter_card['twitter:label2'] = 'Disponibilité'
                twitter_card['twitter:data2'] = 'En stock' if page_data['availability'] else 'Rupture de stock'
        elif page_type == 'blog' and page_data.get('author'):
            twitter_card['twitter:creator'] = page_data.get('author')
        
        return twitter_card
    
    def _generate_keywords(self, page_data: Dict[str, Any], niche: str) -> List[str]:
        """
        Génère une liste de mots-clés pertinents pour la page
        
        Args:
            page_data: Données de la page
            niche: Niche ou catégorie principale
            
        Returns:
            Liste de mots-clés optimisés
        """
        page_type = page_data.get('type', 'product')
        
        # Commencer avec les mots-clés communs de la niche
        keywords = []
        for key in self.common_keywords:
            if key in niche.lower():
                keywords.extend(self.common_keywords[key])
                break
        
        # Ajouter des mots-clés spécifiques selon le type de page
        if page_type == 'product':
            # Ajouter le nom du produit et ses variantes
            product_name = page_data.get('name', page_data.get('title', ''))
            if product_name:
                keywords.append(product_name)
                
                # Ajouter des variations avec le nom de la boutique
                shop_name = self.config['shop_name']
                keywords.append(f"{product_name} {shop_name}")
            
            # Ajouter la marque si disponible
            if page_data.get('brand'):
                keywords.append(page_data['brand'])
                
                # Combiner marque et nom de produit
                if product_name:
                    keywords.append(f"{page_data['brand']} {product_name}")
            
            # Ajouter les caractéristiques comme mots-clés
            if page_data.get('features'):
                keywords.extend(page_data['features'][:3])
            
            # Ajouter les bénéfices comme mots-clés
            if page_data.get('benefits'):
                keywords.extend(page_data['benefits'][:3])
                
        elif page_type == 'collection':
            # Ajouter le nom de la collection
            collection_name = page_data.get('name', page_data.get('title', ''))
            if collection_name:
                keywords.append(collection_name)
                
                # Variations avec "collection" et le nom de la boutique
                keywords.append(f"collection {collection_name}")
                keywords.append(f"{collection_name} {self.config['shop_name']}")
                
        elif page_type == 'blog':
            # Ajouter le titre du blog
            blog_title = page_data.get('name', page_data.get('title', ''))
            if blog_title:
                keywords.append(blog_title)
                
            # Ajouter les tags si disponibles
            if page_data.get('tags'):
                keywords.extend(page_data['tags'][:5])
        
        # Éliminer les doublons et limiter le nombre de mots-clés
        unique_keywords = []
        for keyword in keywords:
            if keyword.lower() not in [k.lower() for k in unique_keywords]:
                unique_keywords.append(keyword)
        
        # Limiter au nombre maximum configuré
        return unique_keywords[:self.config['maxKeywords']]
    
    def _generate_canonical_url(self, page_data: Dict[str, Any], shop_info: Dict[str, Any]) -> str:
        """
        Génère l'URL canonique pour une page
        
        Args:
            page_data: Données de la page
            shop_info: Informations sur la boutique
            
        Returns:
            URL canonique
        """
        domain = shop_info.get('domain', 'example.com')
        handle = page_data.get('handle', self._generate_handle(page_data.get('name', page_data.get('title', 'page'))))
        page_type = page_data.get('type', 'page')
        
        # Construire l'URL selon le type de page
        if page_type == 'product':
            return f"https://{domain}/products/{handle}"
        elif page_type == 'collection':
            return f"https://{domain}/collections/{handle}"
        elif page_type == 'blog':
            blog_handle = page_data.get('blog_handle', 'news')
            return f"https://{domain}/blogs/{blog_handle}/{handle}"
        else:
            return f"https://{domain}/pages/{handle}"
    
    def _generate_handle(self, text: str) -> str:
        """
        Génère un handle SEO-friendly à partir d'un texte
        
        Args:
            text: Texte à convertir en handle
            
        Returns:
            Handle SEO-friendly
        """
        # Convertir en minuscules
        handle = text.lower()
        
        # Remplacer les caractères spéciaux et espaces par des tirets
        handle = re.sub(r'[^\w\s-]', '', handle)
        handle = re.sub(r'[\s_-]+', '-', handle)
        
        # Supprimer les tirets au début et à la fin
        handle = handle.strip('-')
        
        return handle
    
    def _generate_price_valid_date(self) -> str:
        """
        Génère une date d'expiration pour la validité du prix (1 an à partir d'aujourd'hui)
        
        Returns:
            Date au format YYYY-MM-DD
        """
        one_year_later = datetime.datetime.now() + datetime.timedelta(days=365)
        return one_year_later.strftime('%Y-%m-%d')
    
    def _get_emotional_trigger(self, niche: str) -> str:
        """
        Sélectionne un déclencheur émotionnel approprié selon la niche
        
        Args:
            niche: Niche ou catégorie principale
            
        Returns:
            Déclencheur émotionnel
        """
        # Identifier la niche la plus pertinente
        matched_niche = None
        for key in self.emotional_triggers:
            if key.lower() in niche.lower():
                matched_niche = key
                break
        
        # Si aucune niche ne correspond, utiliser fashion par défaut
        if not matched_niche:
            matched_niche = 'fashion'
        
        # Choisir aléatoirement un déclencheur émotionnel dans la liste correspondante
        triggers = self.emotional_triggers[matched_niche]
        return random.choice(triggers)
    
    def _strip_html(self, html: str) -> str:
        """
        Supprime les balises HTML d'un texte
        
        Args:
            html: Texte HTML à nettoyer
            
        Returns:
            Texte sans balises HTML
        """
        # Supprimer toutes les balises HTML
        text = re.sub(r'<[^>]+>', '', html)
        
        # Remplacer les entités HTML communes
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
