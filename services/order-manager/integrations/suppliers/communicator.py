#!/usr/bin/env python3
"""
Communicateur avec les fournisseurs dropshipping
Fait partie du projet Dropshipping Crew AI
"""

import os
from typing import Dict, Optional, Any, List, Type
from loguru import logger

from models import SupplierType
from .base import SupplierInterface, OrderResult


class SupplierCommunicator:
    """
    Façade pour toutes les intégrations de fournisseurs dropshipping.
    
    Cette classe sert de point d'entrée unique pour toutes les communications
    avec les différents fournisseurs dropshipping.
    """
    
    def __init__(self):
        """
        Initialise le communicateur avec les fournisseurs.
        
        Les fournisseurs sont chargés dynamiquement lors de la première utilisation.
        """
        self._suppliers: Dict[str, SupplierInterface] = {}
        self._supplier_classes: Dict[str, Type[SupplierInterface]] = {}
    
    async def _ensure_supplier_loaded(self, supplier_type: str) -> bool:
        """
        S'assure que le fournisseur spécifié est chargé.
        
        Args:
            supplier_type: Type de fournisseur à charger
            
        Returns:
            True si le fournisseur est chargé avec succès, False sinon
        """
        if supplier_type in self._suppliers:
            return True
        
        try:
            if supplier_type == SupplierType.ALIEXPRESS:
                # Import dynamique pour éviter les dépendances circulaires
                from .aliexpress import AliExpressSupplier
                
                api_key = os.getenv("ALIEXPRESS_API_KEY")
                api_url = os.getenv("ALIEXPRESS_API_URL", "https://api.aliexpress.com")
                
                if not api_key:
                    logger.error("Clé API AliExpress manquante. Impossible d'initialiser le fournisseur.")
                    return False
                
                self._suppliers[supplier_type] = AliExpressSupplier(api_key, api_url)
                self._supplier_classes[supplier_type] = AliExpressSupplier
                
            elif supplier_type == SupplierType.CJ_DROPSHIPPING:
                # Import dynamique pour éviter les dépendances circulaires
                from .cj_dropshipping import CJDropshippingSupplier
                
                api_key = os.getenv("CJ_DROPSHIPPING_API_KEY")
                api_url = os.getenv("CJ_DROPSHIPPING_API_URL", "https://api.cjdropshipping.com")
                
                if not api_key:
                    logger.error("Clé API CJ Dropshipping manquante. Impossible d'initialiser le fournisseur.")
                    return False
                
                self._suppliers[supplier_type] = CJDropshippingSupplier(api_key, api_url)
                self._supplier_classes[supplier_type] = CJDropshippingSupplier
                
            else:
                logger.error(f"Type de fournisseur non supporté: {supplier_type}")
                return False
            
            return True
            
        except ImportError as e:
            logger.error(f"Impossible de charger le fournisseur {supplier_type}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du fournisseur {supplier_type}: {str(e)}")
            return False
    
    async def place_order(self, supplier_type: str, order_data: Dict[str, Any]) -> OrderResult:
        """
        Place une commande auprès du fournisseur spécifié.
        
        Args:
            supplier_type: Type de fournisseur
            order_data: Données de la commande
            
        Returns:
            Résultat de l'opération
        """
        if not await self._ensure_supplier_loaded(supplier_type):
            return OrderResult(
                success=False,
                error_message=f"Fournisseur {supplier_type} non disponible"
            )
        
        try:
            return await self._suppliers[supplier_type].place_order(order_data)
        except Exception as e:
            logger.error(f"Erreur lors de la commande auprès du fournisseur {supplier_type}: {str(e)}")
            return OrderResult(
                success=False,
                error_message=f"Erreur lors de la commande: {str(e)}"
            )
    
    async def get_order_status(self, supplier_type: str, supplier_order_id: str) -> OrderResult:
        """
        Récupère le statut d'une commande auprès du fournisseur spécifié.
        
        Args:
            supplier_type: Type de fournisseur
            supplier_order_id: Identifiant de la commande chez le fournisseur
            
        Returns:
            Résultat de l'opération avec le statut
        """
        if not await self._ensure_supplier_loaded(supplier_type):
            return OrderResult(
                success=False,
                error_message=f"Fournisseur {supplier_type} non disponible"
            )
        
        try:
            return await self._suppliers[supplier_type].get_order_status(supplier_order_id)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut auprès du fournisseur {supplier_type}: {str(e)}")
            return OrderResult(
                success=False,
                error_message=f"Erreur lors de la récupération du statut: {str(e)}"
            )
    
    async def get_tracking_info(self, supplier_type: str, supplier_order_id: str) -> OrderResult:
        """
        Récupère les informations de suivi d'une commande.
        
        Args:
            supplier_type: Type de fournisseur
            supplier_order_id: Identifiant de la commande chez le fournisseur
            
        Returns:
            Résultat de l'opération avec les informations de suivi
        """
        if not await self._ensure_supplier_loaded(supplier_type):
            return OrderResult(
                success=False,
                error_message=f"Fournisseur {supplier_type} non disponible"
            )
        
        try:
            return await self._suppliers[supplier_type].get_tracking_info(supplier_order_id)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du suivi auprès du fournisseur {supplier_type}: {str(e)}")
            return OrderResult(
                success=False,
                error_message=f"Erreur lors de la récupération du suivi: {str(e)}"
            )
    
    async def cancel_order(self, supplier_type: str, supplier_order_id: str, reason: str) -> OrderResult:
        """
        Annule une commande auprès du fournisseur spécifié.
        
        Args:
            supplier_type: Type de fournisseur
            supplier_order_id: Identifiant de la commande chez le fournisseur
            reason: Raison de l'annulation
            
        Returns:
            Résultat de l'opération
        """
        if not await self._ensure_supplier_loaded(supplier_type):
            return OrderResult(
                success=False,
                error_message=f"Fournisseur {supplier_type} non disponible"
            )
        
        try:
            return await self._suppliers[supplier_type].cancel_order(supplier_order_id, reason)
        except Exception as e:
            logger.error(f"Erreur lors de l'annulation auprès du fournisseur {supplier_type}: {str(e)}")
            return OrderResult(
                success=False,
                error_message=f"Erreur lors de l'annulation: {str(e)}"
            )
    
    async def search_products(self, supplier_type: str, query: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Recherche des produits chez le fournisseur spécifié.
        
        Args:
            supplier_type: Type de fournisseur
            query: Termes de recherche
            page: Numéro de page
            limit: Nombre de résultats par page
            
        Returns:
            Résultats de la recherche
        """
        if not await self._ensure_supplier_loaded(supplier_type):
            return {
                "success": False,
                "error": f"Fournisseur {supplier_type} non disponible",
                "products": []
            }
        
        try:
            return await self._suppliers[supplier_type].search_products(query, page, limit)
        except Exception as e:
            logger.error(f"Erreur lors de la recherche auprès du fournisseur {supplier_type}: {str(e)}")
            return {
                "success": False,
                "error": f"Erreur lors de la recherche: {str(e)}",
                "products": []
            }
    
    async def get_product_details(self, supplier_type: str, product_id: str) -> Dict[str, Any]:
        """
        Récupère les détails d'un produit spécifique.
        
        Args:
            supplier_type: Type de fournisseur
            product_id: Identifiant du produit chez le fournisseur
            
        Returns:
            Détails du produit
        """
        if not await self._ensure_supplier_loaded(supplier_type):
            return {
                "success": False,
                "error": f"Fournisseur {supplier_type} non disponible"
            }
        
        try:
            return await self._suppliers[supplier_type].get_product_details(product_id)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des détails auprès du fournisseur {supplier_type}: {str(e)}")
            return {
                "success": False,
                "error": f"Erreur lors de la récupération des détails: {str(e)}"
            }
    
    def get_supported_suppliers(self) -> List[str]:
        """
        Retourne la liste des fournisseurs supportés.
        
        Returns:
            Liste des types de fournisseurs supportés
        """
        return [supplier_type for supplier_type in dir(SupplierType) if not supplier_type.startswith("_")]
