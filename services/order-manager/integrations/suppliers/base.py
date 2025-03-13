#!/usr/bin/env python3
"""
Interface de base pour les fournisseurs dropshipping
Fait partie du projet Dropshipping Crew AI
"""

import abc
from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass
class OrderResult:
    """
    Résultat d'une opération liée à une commande fournisseur.
    """
    success: bool
    supplier_order_id: Optional[str] = None
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None
    shipping_company: Optional[str] = None
    status: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class SupplierInterface(abc.ABC):
    """
    Interface abstraite pour tous les fournisseurs dropshipping.
    
    Tous les adaptateurs de fournisseurs doivent implémenter cette interface.
    """
    
    @abc.abstractmethod
    async def place_order(self, order_data: Dict[str, Any]) -> OrderResult:
        """
        Place une commande auprès du fournisseur.
        
        Args:
            order_data: Données de la commande formatées pour le fournisseur
            
        Returns:
            Résultat de l'opération
        """
        pass
    
    @abc.abstractmethod
    async def get_order_status(self, supplier_order_id: str) -> OrderResult:
        """
        Récupère le statut d'une commande auprès du fournisseur.
        
        Args:
            supplier_order_id: Identifiant de la commande chez le fournisseur
            
        Returns:
            Résultat de l'opération avec le statut
        """
        pass
    
    @abc.abstractmethod
    async def get_tracking_info(self, supplier_order_id: str) -> OrderResult:
        """
        Récupère les informations de suivi d'une commande.
        
        Args:
            supplier_order_id: Identifiant de la commande chez le fournisseur
            
        Returns:
            Résultat de l'opération avec les informations de suivi
        """
        pass
    
    @abc.abstractmethod
    async def cancel_order(self, supplier_order_id: str, reason: str) -> OrderResult:
        """
        Annule une commande auprès du fournisseur.
        
        Args:
            supplier_order_id: Identifiant de la commande chez le fournisseur
            reason: Raison de l'annulation
            
        Returns:
            Résultat de l'opération
        """
        pass
    
    @abc.abstractmethod
    async def search_products(self, query: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Recherche des produits chez le fournisseur.
        
        Args:
            query: Termes de recherche
            page: Numéro de page
            limit: Nombre de résultats par page
            
        Returns:
            Résultats de la recherche
        """
        pass
    
    @abc.abstractmethod
    async def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """
        Récupère les détails d'un produit spécifique.
        
        Args:
            product_id: Identifiant du produit chez le fournisseur
            
        Returns:
            Détails du produit
        """
        pass
