import os
import json
import logging
from typing import Dict, List, Any, Optional
import shopify

logger = logging.getLogger(__name__)

class ShopifyClient:
    """
    Client pour interagir avec l'API Shopify
    """
    
    def __init__(self):
        """
        Initialise le client Shopify avec les crédentiels d'API
        """
        try:
            # Récupérer les crédentiels depuis les variables d'environnement
            self.api_key = os.getenv("SHOPIFY_API_KEY")
            self.api_secret = os.getenv("SHOPIFY_API_SECRET")
            self.store_url = os.getenv("SHOPIFY_STORE_URL")
            self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
            
            if not all([self.api_key, self.api_secret, self.store_url, self.access_token]):
                raise ValueError("Les crédentiels Shopify ne sont pas tous configurés")
            
            # Configuration de la session Shopify
            shopify.Session.setup(api_key=self.api_key, secret=self.api_secret)
            
            # Création de la session
            self.session = shopify.Session(self.store_url, "2023-07", self.access_token)
            shopify.ShopifyResource.activate_session(self.session)
            
            logger.info(f"Client Shopify initialisé pour la boutique: {self.store_url}")
            
            # Vérifier que la connexion fonctionne
            shop = shopify.Shop.current()
            logger.info(f"Connecté à la boutique: {shop.name}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du client Shopify: {str(e)}")
            raise
    
    def get_store_url(self) -> str:
        """
        Retourne l'URL de la boutique
        
        Returns:
            URL de la boutique Shopify
        """
        return self.store_url
    
    def get_shop_details(self) -> Dict[str, Any]:
        """
        Récupère les détails de la boutique
        
        Returns:
            Détails de la boutique Shopify
        """
        try:
            shop = shopify.Shop.current()
            return {
                "id": shop.id,
                "name": shop.name,
                "email": shop.email,
                "domain": shop.domain,
                "currency": shop.currency,
                "money_format": shop.money_format,
                "timezone": shop.timezone,
                "country": shop.country_name,
                "created_at": str(shop.created_at) if shop.created_at else None
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des détails de la boutique: {str(e)}")
            raise
    
    def update_shop_details(self, shop_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Met à jour les détails de la boutique
        
        Args:
            shop_data: Données de la boutique à mettre à jour
            
        Returns:
            Détails mis à jour de la boutique
        """
        try:
            shop = shopify.Shop.current()
            
            # Mettre à jour les champs modifiables
            for key, value in shop_data.items():
                if hasattr(shop, key) and key not in ['id', 'created_at', 'updated_at']:
                    setattr(shop, key, value)
            
            shop.save()
            logger.info(f"Détails de la boutique mis à jour: {shop.name}")
            
            return self.get_shop_details()
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des détails de la boutique: {str(e)}")
            raise
    
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée un nouveau produit dans la boutique
        
        Args:
            product_data: Données du produit à créer
            
        Returns:
            Détails du produit créé
        """
        try:
            product = shopify.Product()
            
            # Configurer les propriétés principales
            product.title = product_data.get('title', 'Nouveau Produit')
            product.body_html = product_data.get('description', '')
            product.vendor = product_data.get('vendor', 'Vendeur par défaut')
            product.product_type = product_data.get('product_type', 'Autre')
            product.tags = product_data.get('tags', [])
            
            # Configurer les variantes
            variants_data = product_data.get('variants', [{}])
            for variant_data in variants_data:
                variant = shopify.Variant()
                variant.price = variant_data.get('price', '0.00')
                variant.compare_at_price = variant_data.get('compare_at_price')
                variant.sku = variant_data.get('sku', '')
                variant.inventory_quantity = variant_data.get('inventory_quantity', 0)
                variant.inventory_management = variant_data.get('inventory_management', 'shopify')
                variant.weight = variant_data.get('weight', 0.0)
                variant.weight_unit = variant_data.get('weight_unit', 'kg')
                product.variants = [variant]
            
            # Ajouter des images si spécifiées
            images_data = product_data.get('images', [])
            for image_data in images_data:
                image = shopify.Image()
                image.src = image_data.get('src', '')
                image.alt = image_data.get('alt', '')
                product.images.append(image)
            
            # Enregistrer le produit
            product.save()
            
            logger.info(f"Produit créé avec succès: {product.title} (ID: {product.id})")
            
            # Retourner les détails du produit créé
            return {
                "id": product.id,
                "title": product.title,
                "handle": product.handle,
                "product_type": product.product_type,
                "created_at": str(product.created_at),
                "updated_at": str(product.updated_at),
                "vendor": product.vendor,
                "tags": product.tags,
                "variants": [
                    {
                        "id": variant.id,
                        "price": variant.price,
                        "sku": variant.sku,
                        "inventory_quantity": variant.inventory_quantity
                    } for variant in product.variants
                ],
                "images": [
                    {
                        "id": image.id,
                        "src": image.src,
                        "alt": image.alt
                    } for image in product.images
                ]
            }
        except Exception as e:
            logger.error(f"Erreur lors de la création du produit: {str(e)}")
            raise
    
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Met à jour un produit existant
        
        Args:
            product_id: ID du produit à mettre à jour
            product_data: Données du produit à mettre à jour
            
        Returns:
            Détails du produit mis à jour
        """
        try:
            product = shopify.Product.find(product_id)
            
            # Mettre à jour les propriétés principales
            for key, value in product_data.items():
                if hasattr(product, key) and key not in ['id', 'created_at', 'updated_at']:
                    setattr(product, key, value)
            
            # Mettre à jour les variantes si spécifiées
            if 'variants' in product_data:
                for i, variant_data in enumerate(product_data['variants']):
                    if i < len(product.variants):
                        variant = product.variants[i]
                        for key, value in variant_data.items():
                            if hasattr(variant, key) and key not in ['id', 'created_at', 'updated_at']:
                                setattr(variant, key, value)
            
            # Enregistrer les modifications
            product.save()
            
            logger.info(f"Produit mis à jour avec succès: {product.title} (ID: {product.id})")
            
            # Retourner les détails du produit mis à jour
            return {
                "id": product.id,
                "title": product.title,
                "handle": product.handle,
                "product_type": product.product_type,
                "created_at": str(product.created_at),
                "updated_at": str(product.updated_at),
                "vendor": product.vendor,
                "tags": product.tags,
                "variants": [
                    {
                        "id": variant.id,
                        "price": variant.price,
                        "sku": variant.sku,
                        "inventory_quantity": variant.inventory_quantity
                    } for variant in product.variants
                ],
                "images": [
                    {
                        "id": image.id,
                        "src": image.src,
                        "alt": image.alt
                    } for image in product.images
                ]
            }
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du produit {product_id}: {str(e)}")
            raise
    
    def delete_product(self, product_id: int) -> bool:
        """
        Supprime un produit
        
        Args:
            product_id: ID du produit à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        try:
            product = shopify.Product.find(product_id)
            result = product.destroy()
            
            logger.info(f"Produit supprimé: ID {product_id}")
            return result
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du produit {product_id}: {str(e)}")
            raise
    
    def get_themes(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste des thèmes disponibles
        
        Returns:
            Liste des thèmes disponibles
        """
        try:
            themes = shopify.Theme.find()
            return [
                {
                    "id": theme.id,
                    "name": theme.name,
                    "role": theme.role,
                    "created_at": str(theme.created_at),
                    "updated_at": str(theme.updated_at)
                } for theme in themes
            ]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des thèmes: {str(e)}")
            raise
    
    def get_collections(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste des collections
        
        Returns:
            Liste des collections
        """
        try:
            custom_collections = shopify.CustomCollection.find()
            smart_collections = shopify.SmartCollection.find()
            
            collections = []
            
            # Ajouter les collections personnalisées
            for collection in custom_collections:
                collections.append({
                    "id": collection.id,
                    "title": collection.title,
                    "handle": collection.handle,
                    "type": "custom",
                    "created_at": str(collection.created_at),
                    "updated_at": str(collection.updated_at)
                })
            
            # Ajouter les collections intelligentes
            for collection in smart_collections:
                collections.append({
                    "id": collection.id,
                    "title": collection.title,
                    "handle": collection.handle,
                    "type": "smart",
                    "rules": collection.rules,
                    "created_at": str(collection.created_at),
                    "updated_at": str(collection.updated_at)
                })
            
            return collections
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des collections: {str(e)}")
            raise
    
    def create_custom_collection(self, collection_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée une nouvelle collection personnalisée
        
        Args:
            collection_data: Données de la collection à créer
            
        Returns:
            Détails de la collection créée
        """
        try:
            collection = shopify.CustomCollection()
            
            # Configurer les propriétés principales
            collection.title = collection_data.get('title', 'Nouvelle Collection')
            collection.body_html = collection_data.get('description', '')
            collection.image = collection_data.get('image', {})
            collection.published = collection_data.get('published', True)
            
            # Enregistrer la collection
            collection.save()
            
            logger.info(f"Collection créée avec succès: {collection.title} (ID: {collection.id})")
            
            # Retourner les détails de la collection créée
            return {
                "id": collection.id,
                "title": collection.title,
                "handle": collection.handle,
                "body_html": collection.body_html,
                "published": collection.published,
                "created_at": str(collection.created_at),
                "updated_at": str(collection.updated_at),
                "type": "custom"
            }
        except Exception as e:
            logger.error(f"Erreur lors de la création de la collection: {str(e)}")
            raise
    
    def add_product_to_collection(self, collection_id: int, product_id: int) -> bool:
        """
        Ajoute un produit à une collection personnalisée
        
        Args:
            collection_id: ID de la collection
            product_id: ID du produit à ajouter
            
        Returns:
            True si l'ajout a réussi, False sinon
        """
        try:
            collect = shopify.Collect({
                "collection_id": collection_id,
                "product_id": product_id
            })
            
            result = collect.save()
            
            if result:
                logger.info(f"Produit {product_id} ajouté à la collection {collection_id}")
            else:
                logger.warning(f"Échec de l'ajout du produit {product_id} à la collection {collection_id}")
            
            return result
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du produit à la collection: {str(e)}")
            raise