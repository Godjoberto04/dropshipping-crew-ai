"""
Module d'extraction de règles d'association entre produits.

Ce module implémente l'algorithme Apriori pour extraire les règles d'association
entre produits à partir de données de transactions historiques.
"""

import pandas as pd
import numpy as np
from itertools import combinations
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class AssociationRulesMiner:
    """
    Classe pour l'extraction de règles d'association entre produits.
    
    Implémente l'algorithme Apriori pour identifier les produits qui sont
    fréquemment achetés ensemble, ce qui permet d'optimiser les stratégies
    de cross-selling et up-selling.
    """
    
    def __init__(self, min_support=0.01, min_confidence=0.3, min_lift=1.0):
        """
        Initialise le mineur de règles d'association.
        
        Args:
            min_support (float): Support minimal pour qu'un ensemble d'items soit considéré fréquent
                                (0.01 = 1% des transactions)
            min_confidence (float): Confiance minimale pour qu'une règle soit retenue
                                  (0.3 = 30% de confiance)
            min_lift (float): Lift minimal pour qu'une règle soit considérée intéressante
                             (>1.0 indique une association positive)
        """
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.min_lift = min_lift
        self.frequent_itemsets = {}
        self.rules = []
        self.transaction_count = 0
    
    def fit(self, transactions):
        """
        Extrait les règles d'association à partir des données de transactions.
        
        Args:
            transactions (list): Liste de transactions où chaque transaction est une liste d'items
                               (par exemple [['produit1', 'produit2'], ['produit1', 'produit3']])
        
        Returns:
            self: Instance de la classe pour permettre le chaînage
        """
        self.transaction_count = len(transactions)
        logger.info(f"Début de l'analyse de {self.transaction_count} transactions")
        
        # Création des ensembles d'items fréquents de taille 1
        item_counts = defaultdict(int)
        for transaction in transactions:
            for item in transaction:
                item_counts[frozenset([item])] += 1
        
        # Filtrage selon le support minimal
        k1_items = {item: count for item, count in item_counts.items() 
                   if count / self.transaction_count >= self.min_support}
        
        self.frequent_itemsets[1] = k1_items
        
        # Génération des ensembles d'items fréquents de taille k>1
        k = 2
        while self.frequent_itemsets.get(k-1):
            logger.debug(f"Recherche d'ensembles d'items fréquents de taille {k}")
            candidate_itemsets = self._generate_candidates(self.frequent_itemsets[k-1], k)
            
            # Comptage des occurrences de candidats
            itemset_counts = defaultdict(int)
            for transaction in transactions:
                transaction_set = frozenset(transaction)
                for candidate in candidate_itemsets:
                    if candidate.issubset(transaction_set):
                        itemset_counts[candidate] += 1
            
            # Filtrage selon le support minimal
            k_itemsets = {itemset: count for itemset, count in itemset_counts.items() 
                         if count / self.transaction_count >= self.min_support}
            
            if k_itemsets:
                self.frequent_itemsets[k] = k_itemsets
                k += 1
            else:
                break
        
        # Génération des règles d'association
        self._generate_rules()
        
        logger.info(f"Analyse terminée: {len(self.rules)} règles d'association trouvées")
        return self
    
    def _generate_candidates(self, prev_frequent_itemsets, k):
        """
        Génère les candidats d'ensembles d'items de taille k.
        
        Args:
            prev_frequent_itemsets (dict): Ensembles d'items fréquents de taille k-1
            k (int): Taille des candidats à générer
        
        Returns:
            set: Ensemble des candidats de taille k
        """
        candidates = set()
        prev_items = list(prev_frequent_itemsets.keys())
        
        for i in range(len(prev_items)):
            for j in range(i+1, len(prev_items)):
                # Si les k-2 premiers éléments sont identiques, on peut générer un candidat
                item1 = list(prev_items[i])
                item2 = list(prev_items[j])
                
                # Vérification pour k>2
                if k > 2:
                    if item1[:-1] != item2[:-1]:
                        continue
                
                # Création du nouveau candidat
                new_candidate = frozenset(list(prev_items[i]) + [item for item in prev_items[j] if item not in prev_items[i]])
                
                # Vérification que tous les sous-ensembles sont fréquents
                is_valid = True
                if k > 2:
                    for subset in combinations(new_candidate, k-1):
                        if frozenset(subset) not in prev_frequent_itemsets:
                            is_valid = False
                            break
                
                if is_valid and len(new_candidate) == k:
                    candidates.add(new_candidate)
        
        logger.debug(f"Génération de {len(candidates)} candidats de taille {k}")
        return candidates
    
    def _generate_rules(self):
        """
        Génère les règles d'association à partir des ensembles d'items fréquents.
        """
        self.rules = []
        
        # Parcours des ensembles d'items fréquents de taille >= 2
        for k in range(2, len(self.frequent_itemsets) + 1):
            for itemset, count in self.frequent_itemsets[k].items():
                # Pour chaque sous-ensemble possible comme antécédent
                for i in range(1, k):
                    for antecedent in combinations(itemset, i):
                        antecedent = frozenset(antecedent)
                        consequent = itemset - antecedent
                        
                        # Calcul de la confiance
                        antecedent_support = self.frequent_itemsets[len(antecedent)][antecedent]
                        confidence = count / antecedent_support
                        
                        if confidence >= self.min_confidence:
                            # Calcul du lift
                            consequent_support = self.frequent_itemsets[len(consequent)][consequent]
                            lift = (confidence * self.transaction_count) / consequent_support
                            
                            if lift >= self.min_lift:
                                support = count / self.transaction_count
                                self.rules.append({
                                    'antecedent': list(antecedent),
                                    'consequent': list(consequent),
                                    'support': support,
                                    'confidence': confidence,
                                    'lift': lift
                                })
        
        # Tri par lift décroissant
        self.rules.sort(key=lambda x: x['lift'], reverse=True)
    
    def get_rules(self, top_n=None):
        """
        Retourne les règles d'association trouvées.
        
        Args:
            top_n (int, optional): Nombre de règles à retourner. Si None, retourne toutes les règles.
        
        Returns:
            list: Liste des règles d'association
        """
        if top_n:
            return self.rules[:top_n]
        return self.rules
    
    def get_product_recommendations(self, products, top_n=5):
        """
        Retourne les recommandations de produits complémentaires.
        
        Args:
            products (list): Liste des produits pour lesquels on cherche des compléments
            top_n (int): Nombre de recommandations à retourner
        
        Returns:
            list: Liste des produits recommandés avec scores
        """
        products_set = frozenset(products)
        recommendations = []
        
        for rule in self.rules:
            antecedent_set = frozenset(rule['antecedent'])
            # Si l'antécédent est inclus dans les produits fournis
            if antecedent_set.issubset(products_set):
                # Ajoute les conséquents qui ne sont pas déjà dans les produits
                for item in rule['consequent']:
                    if item not in products_set:
                        recommendations.append({
                            'product': item,
                            'confidence': rule['confidence'],
                            'lift': rule['lift'],
                            'support': rule['support']
                        })
        
        # Déduplique les recommandations et garde les scores les plus élevés
        deduplicated = {}
        for rec in recommendations:
            product = rec['product']
            if product not in deduplicated or rec['lift'] > deduplicated[product]['lift']:
                deduplicated[product] = rec
        
        # Tri et limitation
        result = list(deduplicated.values())
        result.sort(key=lambda x: x['lift'], reverse=True)
        return result[:top_n]
