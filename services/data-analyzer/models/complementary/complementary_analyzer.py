"""
Module d'analyse de complémentarité de produits.

Ce module permet d'identifier les produits complémentaires pour optimiser
les stratégies de cross-selling et d'up-selling dans un contexte e-commerce.
"""

import pandas as pd
import numpy as np
import logging
from collections import defaultdict
from .association_rules import AssociationRulesMiner

logger = logging.getLogger(__name__)

class ComplementaryAnalyzer:
    """
    Analyseur de complémentarité de produits pour le dropshipping.
    
    Cette classe intègre plusieurs approches pour identifier les produits
    complémentaires, notamment les règles d'association, l'analyse de catégories,
    et les suggestions basées sur les comportements d'achat.
    """
    
    def __init__(self, config=None):
        """
        Initialise l'analyseur de complémentarité.
        
        Args:
            config (dict, optional): Configuration pour l'analyseur
        """
        self.config = config or {}
        self.association_miner = None
        self.category_pairs = {}
        self.product_metadata = {}
        self.cross_sell_mappings = {}
        self.up_sell_mappings = {}
        
        # Paramètres par défaut
        self.default_config = {
            'min_support': 0.01,
            'min_confidence': 0.2,
            'min_lift': 1.5,
            'up_sell_price_factor': 1.3,  # Produit up-sell au moins 30% plus cher
            'max_complementary_products': 5,
            'max_up_sell_products': 3,
            'cache_enabled': True,
            'cache_ttl_days': 7
        }
        
        # Fusion avec la configuration fournie
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        logger.info("Analyseur de complémentarité initialisé")
    
    def load_transaction_data(self, transactions_data):
        """
        Charge les données de transactions pour l'analyse d'association.
        
        Args:
            transactions_data (list): Liste des transactions,
                où chaque transaction est une liste d'identifiants de produits
                
        Returns:
            self: Pour permettre le chaînage
        """
        logger.info(f"Chargement de {len(transactions_data)} transactions")
        
        # Initialisation du mineur de règles d'association
        self.association_miner = AssociationRulesMiner(
            min_support=self.config['min_support'],
            min_confidence=self.config['min_confidence'],
            min_lift=self.config['min_lift']
        )
        
        # Extraction des règles d'association
        self.association_miner.fit(transactions_data)
        
        logger.info(f"{len(self.association_miner.get_rules())} règles d'association extraites")
        return self
    
    def load_product_metadata(self, products_data):
        """
        Charge les métadonnées des produits (catégories, prix, etc.).
        
        Args:
            products_data (dict): Dictionnaire de métadonnées de produits
                {product_id: {category, price, name, etc.}}
                
        Returns:
            self: Pour permettre le chaînage
        """
        logger.info(f"Chargement des métadonnées pour {len(products_data)} produits")
        self.product_metadata = products_data
        
        # Construction des paires de catégories complémentaires
        self._build_category_pairs()
        
        # Construction des mappings d'up-sell
        self._build_upsell_mappings()
        
        return self
    
    def set_category_pairs(self, category_pairs):
        """
        Définit manuellement les paires de catégories complémentaires.
        
        Args:
            category_pairs (dict): Dictionnaire {category: [complementary_categories]}
                
        Returns:
            self: Pour permettre le chaînage
        """
        self.category_pairs = category_pairs
        logger.info(f"Paires de catégories définies manuellement: {len(category_pairs)} catégories principales")
        return self
    
    def get_complementary_products(self, product_id, max_products=None):
        """
        Retourne les produits complémentaires pour un produit donné.
        
        Combine les résultats des différentes méthodes d'analyse (association rules,
        paires de catégories, etc.) pour fournir une liste ordonnée de produits complémentaires.
        
        Args:
            product_id (str): Identifiant du produit
            max_products (int, optional): Nombre maximum de produits à retourner
                
        Returns:
            list: Liste de produits complémentaires avec scores
        """
        if max_products is None:
            max_products = self.config['max_complementary_products']
        
        logger.info(f"Recherche de produits complémentaires pour {product_id}")
        
        all_recommendations = []
        
        # 1. Recommandations par règles d'association
        if self.association_miner:
            assoc_recommendations = self._get_recommendations_by_association([product_id])
            for rec in assoc_recommendations:
                rec['source'] = 'association'
                rec['score'] = rec['lift'] * 0.5 + rec['confidence'] * 0.5  # Score combiné
                all_recommendations.append(rec)
        
        # 2. Recommandations par catégorie
        category_recommendations = self._get_recommendations_by_category(product_id)
        for rec in category_recommendations:
            rec['source'] = 'category'
            # Vérifier les doublons avec les recommandations d'association
            if not any(r['product'] == rec['product'] for r in all_recommendations):
                all_recommendations.append(rec)
        
        # 3. Filtrage des produits inappropriés
        filtered_recommendations = self._filter_recommendations(all_recommendations, product_id)
        
        # 4. Tri par score et limitation
        filtered_recommendations.sort(key=lambda x: x['score'], reverse=True)
        return filtered_recommendations[:max_products]
    
    def get_upsell_products(self, product_id, max_products=None):
        """
        Retourne les produits d'up-sell pour un produit donné.
        
        Identifie les produits de gamme supérieure qui pourraient être proposés
        en remplacement du produit original.
        
        Args:
            product_id (str): Identifiant du produit
            max_products (int, optional): Nombre maximum de produits à retourner
                
        Returns:
            list: Liste de produits d'up-sell avec scores
        """
        if max_products is None:
            max_products = self.config['max_up_sell_products']
        
        logger.info(f"Recherche de produits d'up-sell pour {product_id}")
        
        # Obtenir les produits d'up-sell pertinents
        if product_id not in self.product_metadata:
            logger.warning(f"Métadonnées manquantes pour {product_id}")
            return []
        
        product_data = self.product_metadata[product_id]
        category = product_data.get('category')
        price = product_data.get('price', 0)
        
        if not category or not price:
            logger.warning(f"Données catégorie ou prix manquantes pour {product_id}")
            return []
        
        # Recherche de produits dans la même catégorie mais plus chers
        upsell_candidates = []
        for p_id, p_data in self.product_metadata.items():
            if p_id == product_id:
                continue
                
            p_category = p_data.get('category')
            p_price = p_data.get('price', 0)
            
            if p_category == category and p_price >= price * self.config['up_sell_price_factor']:
                # Score basé sur le rapport qualité-prix et popularité
                quality_score = p_data.get('rating', 3) / 5  # Normalisation des notes
                price_factor = min(p_price / price, 3) / 3  # Éviter les produits trop chers
                popularity = p_data.get('popularity', 50) / 100  # Normalisation de la popularité
                
                score = quality_score * 0.4 + (1 - price_factor) * 0.3 + popularity * 0.3
                
                upsell_candidates.append({
                    'product': p_id,
                    'score': score,
                    'price_difference': p_price - price,
                    'price_ratio': p_price / price,
                    'source': 'category_upsell'
                })
        
        # Ajout des up-sells connus si disponibles
        if product_id in self.up_sell_mappings:
            for p_id in self.up_sell_mappings[product_id]:
                if not any(c['product'] == p_id for c in upsell_candidates):
                    if p_id in self.product_metadata:
                        p_data = self.product_metadata[p_id]
                        p_price = p_data.get('price', 0)
                        
                        upsell_candidates.append({
                            'product': p_id,
                            'score': 0.85,  # Score élevé pour les up-sells manuels
                            'price_difference': p_price - price if p_price else None,
                            'price_ratio': p_price / price if p_price and price else None,
                            'source': 'manual_upsell'
                        })
        
        # Tri et limitation
        upsell_candidates.sort(key=lambda x: x['score'], reverse=True)
        return upsell_candidates[:max_products]
    
    def bundle_products(self, product_ids, max_bundles=3):
        """
        Crée des bundles de produits à partir d'un ensemble de produits.
        
        Analyse les produits fournis et suggère des bundles optimisés
        pour maximiser la valeur du panier.
        
        Args:
            product_ids (list): Liste d'identifiants de produits
            max_bundles (int): Nombre maximum de bundles à retourner
                
        Returns:
            list: Liste de bundles suggérés avec scores
        """
        logger.info(f"Création de bundles pour {len(product_ids)} produits")
        
        # Obtenir les recommandations pour l'ensemble des produits
        complementary_products = self._get_recommendations_by_association(product_ids)
        
        # Calculer le prix total du panier actuel
        current_total = sum(self.product_metadata.get(p_id, {}).get('price', 0) for p_id in product_ids)
        
        # Créer les bundles
        bundles = []
        
        # 1. Bundle avec le meilleur produit complémentaire
        if complementary_products:
            top_complement = complementary_products[0]['product']
            top_price = self.product_metadata.get(top_complement, {}).get('price', 0)
            
            bundles.append({
                'name': "Bundle Essentiel",
                'products': product_ids + [top_complement],
                'original_price': current_total + top_price,
                'bundle_price': (current_total + top_price) * 0.95,  # 5% de réduction
                'discount_percentage': 5,
                'score': complementary_products[0].get('score', 0.8)
            })
        
        # 2. Bundle Premium (avec les 2-3 meilleurs compléments)
        if len(complementary_products) >= 2:
            premium_complements = [cp['product'] for cp in complementary_products[:min(3, len(complementary_products))]]
            premium_price = sum(self.product_metadata.get(p_id, {}).get('price', 0) for p_id in premium_complements)
            
            bundles.append({
                'name': "Bundle Premium",
                'products': product_ids + premium_complements,
                'original_price': current_total + premium_price,
                'bundle_price': (current_total + premium_price) * 0.90,  # 10% de réduction
                'discount_percentage': 10,
                'score': 0.9  # Score plus élevé pour le bundle premium
            })
        
        # 3. Bundle Économique (produit principal + complément le moins cher)
        if len(complementary_products) >= 1:
            # Trouver le complément le moins cher
            complements_with_price = [(cp['product'], self.product_metadata.get(cp['product'], {}).get('price', 0)) 
                                     for cp in complementary_products[:min(5, len(complementary_products))]]
            complements_with_price.sort(key=lambda x: x[1])
            
            if complements_with_price:
                eco_complement, eco_price = complements_with_price[0]
                
                bundles.append({
                    'name': "Bundle Économique",
                    'products': product_ids + [eco_complement],
                    'original_price': current_total + eco_price,
                    'bundle_price': (current_total + eco_price) * 0.93,  # 7% de réduction
                    'discount_percentage': 7,
                    'score': 0.75
                })
        
        # Tri des bundles par score
        bundles.sort(key=lambda x: x['score'], reverse=True)
        return bundles[:max_bundles]
    
    def analyze_cart(self, product_ids):
        """
        Analyse un panier pour suggérer des améliorations.
        
        Évalue le contenu du panier et fournit des suggestions
        pour optimiser sa valeur (produits complémentaires manquants,
        up-sells possibles, etc.).
        
        Args:
            product_ids (list): Liste d'identifiants de produits dans le panier
                
        Returns:
            dict: Résultats d'analyse avec suggestions
        """
        logger.info(f"Analyse du panier contenant {len(product_ids)} produits")
        
        result = {
            'cart_value': 0,
            'product_count': len(product_ids),
            'missing_complementary': [],
            'potential_upsells': [],
            'bundle_opportunities': [],
            'cart_score': 0  # Score global d'optimisation du panier
        }
        
        # Calculer la valeur du panier
        for product_id in product_ids:
            if product_id in self.product_metadata:
                price = self.product_metadata[product_id].get('price', 0)
                result['cart_value'] += price
        
        # 1. Identifier les produits complémentaires manquants
        all_complementary = []
        for product_id in product_ids:
            complements = self.get_complementary_products(product_id, max_products=3)
            for complement in complements:
                # Ne pas suggérer des produits déjà dans le panier
                if complement['product'] not in product_ids:
                    complement['for_product'] = product_id
                    all_complementary.append(complement)
        
        # Dédupliquer et trier
        seen_products = set()
        deduplicated_complementary = []
        for complement in all_complementary:
            if complement['product'] not in seen_products:
                seen_products.add(complement['product'])
                deduplicated_complementary.append(complement)
        
        # Tri par score et limitation
        deduplicated_complementary.sort(key=lambda x: x['score'], reverse=True)
        result['missing_complementary'] = deduplicated_complementary[:5]
        
        # 2. Identifier les opportunités d'up-sell
        for product_id in product_ids:
            upsells = self.get_upsell_products(product_id, max_products=1)
            if upsells:
                upsells[0]['for_product'] = product_id
                result['potential_upsells'].append(upsells[0])
        
        # 3. Suggérer des bundles si pas assez de produits dans le panier
        if len(product_ids) < 3:
            result['bundle_opportunities'] = self.bundle_products(product_ids, max_bundles=2)
        
        # 4. Calculer un score global d'optimisation du panier
        # Plus le score est faible, plus il y a d'opportunités d'amélioration
        complementary_score = min(1.0, len(result['missing_complementary']) / 5)
        upsell_score = min(1.0, len(result['potential_upsells']) / len(product_ids) if product_ids else 0)
        bundle_score = 0 if result['bundle_opportunities'] else 1.0
        
        result['cart_score'] = (1.0 - (complementary_score * 0.4 + upsell_score * 0.4 + bundle_score * 0.2)) * 100
        
        return result
    
    def _build_category_pairs(self):
        """
        Construit les paires de catégories complémentaires à partir des données produit.
        
        Cette méthode est appelée après le chargement des métadonnées produit
        pour établir automatiquement les relations entre catégories.
        """
        # Exemple de paires de catégories prédéfinies pour le dropshipping
        default_pairs = {
            'smartphones': ['phone_cases', 'screen_protectors', 'chargers', 'headphones'],
            'laptops': ['laptop_bags', 'external_drives', 'mice', 'laptop_stands'],
            'cameras': ['camera_bags', 'tripods', 'lenses', 'memory_cards'],
            'watches': ['watch_bands', 'watch_chargers', 'jewelry'],
            'clothing': ['accessories', 'shoes', 'jewelry', 'bags'],
            'beauty': ['makeup_accessories', 'skincare', 'haircare'],
            'home_decor': ['pillows', 'lighting', 'wall_art', 'rugs'],
            'kitchen': ['cookware', 'utensils', 'food_storage', 'kitchen_gadgets']
        }
        
        # Utilisation des paires par défaut si pas de données suffisantes
        if not self.category_pairs:
            self.category_pairs = default_pairs
        
        # TODO: Construire automatiquement des paires de catégories basées sur
        # les comportements d'achat si suffisamment de données disponibles
        
        logger.info(f"Paires de catégories construites: {len(self.category_pairs)} catégories principales")
    
    def _build_upsell_mappings(self):
        """
        Construit les mappings d'up-sell à partir des métadonnées des produits.
        
        Identifie les produits qui peuvent être proposés en up-sell
        en fonction du prix, des caractéristiques et de la catégorie.
        """
        # Organisation des produits par catégorie et prix
        categorized_products = defaultdict(list)
        
        for product_id, metadata in self.product_metadata.items():
            category = metadata.get('category')
            if category:
                price = metadata.get('price', 0)
                quality = metadata.get('rating', 3)
                categorized_products[category].append((product_id, price, quality))
        
        # Pour chaque catégorie, créer des mappings d'up-sell
        for category, products in categorized_products.items():
            # Tri par prix
            products.sort(key=lambda x: x[1])
            
            # Créer les mappings
            for i, (product_id, price, quality) in enumerate(products):
                potential_upsells = []
                
                # Considérer les produits plus chers comme up-sells potentiels
                for j in range(i+1, len(products)):
                    up_id, up_price, up_quality = products[j]
                    
                    # Un produit up-sell doit être au moins X% plus cher mais pas plus de Y fois plus cher
                    if up_price >= price * self.config['up_sell_price_factor'] and up_price <= price * 3:
                        # Plus le rapport qualité/prix est bon, plus le produit est un bon up-sell
                        quality_price_ratio = up_quality / up_price
                        
                        if quality_price_ratio >= (quality / price) * 0.8:  # Au moins 80% du rapport qualité/prix
                            potential_upsells.append(up_id)
                
                # Limiter à 3 up-sells maximum
                if potential_upsells:
                    self.up_sell_mappings[product_id] = potential_upsells[:3]
        
        logger.info(f"Mappings d'up-sell construits pour {len(self.up_sell_mappings)} produits")
    
    def _get_recommendations_by_association(self, product_ids):
        """
        Obtient des recommandations basées sur les règles d'association.
        
        Args:
            product_ids (list): Liste d'identifiants de produits
                
        Returns:
            list: Liste de produits recommandés avec scores
        """
        if not self.association_miner:
            return []
        
        return self.association_miner.get_product_recommendations(product_ids)
    
    def _get_recommendations_by_category(self, product_id):
        """
        Obtient des recommandations basées sur les paires de catégories.
        
        Args:
            product_id (str): Identifiant du produit
                
        Returns:
            list: Liste de produits recommandés avec scores
        """
        if product_id not in self.product_metadata:
            return []
        
        product_data = self.product_metadata[product_id]
        category = product_data.get('category')
        
        if not category or category not in self.category_pairs:
            return []
        
        # Obtenir les catégories complémentaires
        complementary_categories = self.category_pairs[category]
        
        # Trouver les produits dans ces catégories
        recommendations = []
        
        for p_id, p_data in self.product_metadata.items():
            if p_id == product_id:
                continue
                
            p_category = p_data.get('category')
            
            if p_category in complementary_categories:
                # Score basé sur la popularité et les notes
                popularity = p_data.get('popularity', 50) / 100
                rating = p_data.get('rating', 3) / 5
                
                score = popularity * 0.6 + rating * 0.4
                
                recommendations.append({
                    'product': p_id,
                    'score': score,
                    'complementary_category': p_category
                })
        
        # Tri par score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        # Maximum 2 produits par catégorie complémentaire
        result = []
        category_counts = defaultdict(int)
        
        for rec in recommendations:
            cat = rec['complementary_category']
            if category_counts[cat] < 2:
                result.append(rec)
                category_counts[cat] += 1
        
        return result[:5]  # Maximum 5 recommandations au total
    
    def _filter_recommendations(self, recommendations, product_id):
        """
        Filtre les recommandations inappropriées.
        
        Élimine les produits incompatibles ou redondants.
        
        Args:
            recommendations (list): Liste de recommandations
            product_id (str): Identifiant du produit d'origine
                
        Returns:
            list: Liste de recommandations filtrées
        """
        # Obtenir les données du produit d'origine
        if product_id not in self.product_metadata:
            return recommendations
        
        product_data = self.product_metadata[product_id]
        product_category = product_data.get('category')
        product_price = product_data.get('price', 0)
        
        filtered = []
        
        for rec in recommendations:
            rec_id = rec['product']
            
            # Vérifier que le produit existe dans les métadonnées
            if rec_id not in self.product_metadata:
                continue
                
            rec_data = self.product_metadata[rec_id]
            rec_category = rec_data.get('category')
            rec_price = rec_data.get('price', 0)
            
            # Filtres de compatibilité et pertinence
            
            # 1. Éviter de recommander des produits de la même catégorie sauf si la source est "association"
            if rec_category == product_category and rec.get('source') != 'association':
                continue
            
            # 2. Éviter les produits beaucoup plus chers (plus de 3x) sauf pour les up-sells explicites
            if rec_price > product_price * 3 and rec.get('source') != 'manual_upsell':
                continue
            
            # 3. Vérifications spécifiques par catégorie (exemple)
            if product_category == 'smartphones' and rec_category == 'phone_cases':
                # Vérifier la compatibilité du modèle (exemple simplifié)
                if not self._are_compatible(product_id, rec_id):
                    continue
            
            # Ajout à la liste filtrée
            filtered.append(rec)
        
        return filtered
    
    def _are_compatible(self, product1_id, product2_id):
        """
        Vérifie si deux produits sont compatibles entre eux.
        
        Méthode simplifiée utilisée pour l'exemple. Dans une implémentation réelle,
        il faudrait vérifier les attributs spécifiques de compatibilité.
        
        Args:
            product1_id (str): Identifiant du premier produit
            product2_id (str): Identifiant du second produit
                
        Returns:
            bool: True si les produits sont compatibles, False sinon
        """
        # Implémentation simplifiée - toujours compatible dans cet exemple
        return True
