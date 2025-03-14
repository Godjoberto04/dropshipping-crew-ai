#!/usr/bin/env python3
"""
Service de gestion des commandes - Module fournisseurs
Fait partie du projet Dropshipping Crew AI
"""

import os
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger

from models import SupplierType
from storage import OrderRepository
from integrations.suppliers.communicator import SupplierCommunicator
from integrations.suppliers.supplier_selector import SupplierSelector


class OrderServiceSuppliers:
    """
    Service pour la gestion des commandes côté fournisseurs.
    
    Ce service gère les interactions avec les fournisseurs dropshipping,
    y compris la sélection automatique du meilleur fournisseur pour une commande.
    """
    
    def __init__(self, repository: OrderRepository, communicator: SupplierCommunicator = None):
        """
        Initialise le service des fournisseurs.
        
        Args:
            repository: Référentiel pour les données de commande
            communicator: Communicateur avec les fournisseurs (facultatif)
        """
        self.repository = repository
        self.communicator = communicator or SupplierCommunicator()
        self.supplier_selector = SupplierSelector(self.communicator)
        
        # Configuration de la préférence de fournisseur
        self.default_supplier = os.getenv("DEFAULT_SUPPLIER", SupplierType.ALIEXPRESS)
        
        # Configuration des stratégies de sélection de fournisseur
        self.supplier_selection_strategies = {
            "auto": self._auto_select_supplier,
            "cheapest": self._select_cheapest_supplier,
            "fastest": self._select_fastest_supplier,
            "default": self._select_default_supplier
        }
    
    async def process_supplier_order(self, order_data: Dict[str, Any], strategy: str = "auto") -> Dict[str, Any]:
        """
        Traite une commande côté fournisseur, en sélectionnant le meilleur fournisseur.
        
        Args:
            order_data: Données de la commande
            strategy: Stratégie de sélection du fournisseur ("auto", "cheapest", "fastest", "default")
            
        Returns:
            Résultat du traitement
        """
        logger.info(f"Traitement de la commande {order_data.get('id')} avec la stratégie '{strategy}'")
        
        # Vérifier si la stratégie est valide
        if strategy not in self.supplier_selection_strategies:
            strategy = "auto"
            logger.warning(f"Stratégie '{strategy}' non reconnue, utilisation de 'auto' à la place")
        
        # Sélectionner le fournisseur selon la stratégie
        try:
            suppliers_details = await self._get_suppliers_for_products(order_data["line_items"], strategy)
            
            if not suppliers_details:
                return {
                    "success": False,
                    "error": "Aucun fournisseur disponible pour les produits commandés"
                }
            
            # Organiser les produits par fournisseur
            supplier_orders = self._organize_products_by_supplier(order_data, suppliers_details)
            
            # Traiter les commandes pour chaque fournisseur
            results = await self._place_supplier_orders(supplier_orders)
            
            # Enregistrer les résultats dans la base de données
            await self._save_supplier_orders(order_data["id"], results)
            
            return {
                "success": True,
                "orders": results
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la commande {order_data.get('id')}: {str(e)}")
            return {
                "success": False,
                "error": f"Erreur lors du traitement: {str(e)}"
            }
    
    async def _get_suppliers_for_products(
        self, line_items: List[Dict[str, Any]], strategy: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Obtient les fournisseurs pour chaque produit selon la stratégie choisie.
        
        Args:
            line_items: Éléments de la commande
            strategy: Stratégie de sélection
            
        Returns:
            Dictionnaire des fournisseurs par produit
        """
        suppliers = {}
        
        for item in line_items:
            product_id = item.get("product_id")
            variant_id = item.get("variant_id")
            
            if not product_id:
                logger.warning(f"Element de commande sans product_id: {item}")
                continue
            
            try:
                # Sélectionner le fournisseur selon la stratégie
                select_strategy = self.supplier_selection_strategies[strategy]
                supplier, details = await select_strategy(product_id, variant_id)
                
                if supplier:
                    # Stocker les détails du fournisseur pour ce produit
                    key = f"{product_id}:{variant_id}" if variant_id else product_id
                    suppliers[key] = {
                        "supplier": supplier,
                        "details": details
                    }
                else:
                    logger.warning(f"Aucun fournisseur trouvé pour le produit {product_id}")
            
            except Exception as e:
                logger.error(f"Erreur lors de la sélection du fournisseur pour {product_id}: {str(e)}")
        
        return suppliers
    
    def _organize_products_by_supplier(
        self, order_data: Dict[str, Any], suppliers_details: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Organise les produits par fournisseur pour passer des commandes groupées.
        
        Args:
            order_data: Données de la commande
            suppliers_details: Détails des fournisseurs par produit
            
        Returns:
            Commandes organisées par fournisseur
        """
        supplier_orders = {}
        
        # Adresse de livraison commune
        shipping_address = order_data.get("shipping_address", {})
        
        for item in order_data["line_items"]:
            product_id = item.get("product_id")
            variant_id = item.get("variant_id")
            
            key = f"{product_id}:{variant_id}" if variant_id else product_id
            
            if key not in suppliers_details:
                logger.warning(f"Pas de détails fournisseur pour le produit {key}, ignoré")
                continue
            
            supplier = suppliers_details[key]["supplier"]
            
            # Initialiser la commande pour ce fournisseur si nécessaire
            if supplier not in supplier_orders:
                supplier_orders[supplier] = {
                    "order_id": order_data["id"],
                    "shipping_address": shipping_address,
                    "line_items": [],
                    "customer": order_data.get("customer", {})
                }
            
            # Ajouter l'item à la commande du fournisseur
            supplier_orders[supplier]["line_items"].append(item)
        
        return supplier_orders
    
    async def _place_supplier_orders(self, supplier_orders: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Place les commandes auprès des fournisseurs.
        
        Args:
            supplier_orders: Commandes organisées par fournisseur
            
        Returns:
            Résultats des commandes passées
        """
        results = []
        
        for supplier, order_data in supplier_orders.items():
            try:
                # Placer la commande chez le fournisseur
                result = await self.communicator.place_order(supplier, order_data)
                
                # Ajouter le résultat à la liste
                results.append({
                    "supplier": supplier,
                    "supplier_order_id": result.supplier_order_id,
                    "status": result.status,
                    "success": result.success,
                    "error_message": result.error_message,
                    "details": result.details
                })
                
            except Exception as e:
                logger.error(f"Erreur lors de la commande chez {supplier}: {str(e)}")
                results.append({
                    "supplier": supplier,
                    "success": False,
                    "status": "error",
                    "error_message": f"Erreur: {str(e)}"
                })
        
        return results
    
    async def _save_supplier_orders(self, order_id: str, results: List[Dict[str, Any]]) -> None:
        """
        Enregistre les résultats des commandes fournisseurs dans la base de données.
        
        Args:
            order_id: ID de la commande client
            results: Résultats des commandes fournisseurs
        """
        # Pour chaque résultat de commande fournisseur
        for result in results:
            if result.get("success"):
                # Enregistrer les détails de la commande fournisseur
                await self.repository.create_supplier_order(
                    order_id=order_id,
                    supplier=result["supplier"],
                    supplier_order_id=result["supplier_order_id"],
                    status=result["status"],
                    details=result.get("details", {})
                )
    
    async def get_supplier_order_status(self, supplier_order_id: str, supplier: str) -> Dict[str, Any]:
        """
        Récupère le statut d'une commande fournisseur.
        
        Args:
            supplier_order_id: ID de la commande chez le fournisseur
            supplier: Type de fournisseur
            
        Returns:
            Statut de la commande
        """
        try:
            result = await self.communicator.get_order_status(supplier, supplier_order_id)
            
            if result.success:
                # Mettre à jour le statut dans la base de données
                await self.repository.update_supplier_order_status(
                    supplier_order_id=supplier_order_id,
                    status=result.status,
                    details=result.details
                )
            
            return {
                "success": result.success,
                "supplier_order_id": supplier_order_id,
                "status": result.status,
                "details": result.details,
                "error_message": result.error_message
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut {supplier_order_id}: {str(e)}")
            return {
                "success": False,
                "supplier_order_id": supplier_order_id,
                "error_message": f"Erreur: {str(e)}"
            }
    
    async def get_tracking_info(self, supplier_order_id: str, supplier: str) -> Dict[str, Any]:
        """
        Récupère les informations de suivi d'une commande fournisseur.
        
        Args:
            supplier_order_id: ID de la commande chez le fournisseur
            supplier: Type de fournisseur
            
        Returns:
            Informations de suivi
        """
        try:
            result = await self.communicator.get_tracking_info(supplier, supplier_order_id)
            
            if result.success and result.tracking_number:
                # Mettre à jour les informations de suivi dans la base de données
                await self.repository.update_supplier_order_tracking(
                    supplier_order_id=supplier_order_id,
                    tracking_number=result.tracking_number,
                    tracking_url=result.tracking_url,
                    shipping_company=result.shipping_company,
                    details=result.details
                )
            
            return {
                "success": result.success,
                "supplier_order_id": supplier_order_id,
                "tracking_number": result.tracking_number,
                "tracking_url": result.tracking_url,
                "shipping_company": result.shipping_company,
                "status": result.status,
                "details": result.details,
                "error_message": result.error_message
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du suivi {supplier_order_id}: {str(e)}")
            return {
                "success": False,
                "supplier_order_id": supplier_order_id,
                "error_message": f"Erreur: {str(e)}"
            }
    
    async def cancel_supplier_order(self, supplier_order_id: str, supplier: str, reason: str) -> Dict[str, Any]:
        """
        Annule une commande fournisseur.
        
        Args:
            supplier_order_id: ID de la commande chez le fournisseur
            supplier: Type de fournisseur
            reason: Raison de l'annulation
            
        Returns:
            Résultat de l'annulation
        """
        try:
            result = await self.communicator.cancel_order(supplier, supplier_order_id, reason)
            
            if result.success:
                # Mettre à jour le statut dans la base de données
                await self.repository.update_supplier_order_status(
                    supplier_order_id=supplier_order_id,
                    status="cancelled",
                    details=result.details
                )
            
            return {
                "success": result.success,
                "supplier_order_id": supplier_order_id,
                "status": result.status,
                "details": result.details,
                "error_message": result.error_message
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'annulation {supplier_order_id}: {str(e)}")
            return {
                "success": False,
                "supplier_order_id": supplier_order_id,
                "error_message": f"Erreur: {str(e)}"
            }
    
    async def search_products(self, query: str, supplier: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """
        Recherche des produits chez les fournisseurs.
        
        Args:
            query: Termes de recherche
            supplier: Type de fournisseur (optionnel)
            limit: Nombre de résultats par fournisseur
            
        Returns:
            Résultats de la recherche
        """
        try:
            if supplier:
                # Recherche chez un fournisseur spécifique
                results = await self.communicator.search_products(supplier, query, page=1, limit=limit)
                return results
            else:
                # Recherche chez tous les fournisseurs
                results = await self.supplier_selector.find_product_across_suppliers(query, limit)
                return {
                    "success": True,
                    "products": results,
                    "total": len(results)
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la recherche '{query}': {str(e)}")
            return {
                "success": False,
                "error": f"Erreur lors de la recherche: {str(e)}",
                "products": []
            }
    
    # Stratégies de sélection de fournisseur
    
    async def _auto_select_supplier(self, product_id: str, variant_id: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Sélectionne automatiquement le meilleur fournisseur pour un produit.
        
        Args:
            product_id: ID du produit
            variant_id: ID de la variante (optionnel)
            
        Returns:
            Tuple avec le fournisseur sélectionné et les détails du produit
        """
        return await self.supplier_selector.select_optimal_supplier(product_id, variant_id)
    
    async def _select_cheapest_supplier(self, product_id: str, variant_id: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Sélectionne le fournisseur le moins cher pour un produit.
        
        Args:
            product_id: ID du produit
            variant_id: ID de la variante (optionnel)
            
        Returns:
            Tuple avec le fournisseur sélectionné et les détails du produit
        """
        # Récupérer les détails chez tous les fournisseurs disponibles
        suppliers = [SupplierType.ALIEXPRESS, SupplierType.CJ_DROPSHIPPING]
        product_details = {}
        cheapest_supplier = None
        cheapest_price = float("inf")
        
        for supplier in suppliers:
            try:
                details = await self.communicator.get_product_details(supplier, product_id)
                
                if not details.get("success", False):
                    continue
                
                product_details[supplier] = details
                
                # Déterminer le prix
                price = 0
                if variant_id and "variations" in details:
                    # Recherche du prix pour la variante spécifiée
                    for variation in details.get("variations", []):
                        if variation.get("id") == variant_id:
                            price = variation.get("price", 0)
                            break
                else:
                    # Si pas de variante, utiliser le prix minimum
                    price = details.get("price", {}).get("min", 0)
                
                # Ajouter le coût d'expédition le moins cher
                shipping_methods = details.get("shipping_info", {}).get("methods", [])
                if shipping_methods:
                    shipping_cost = min(method.get("price", 0) for method in shipping_methods)
                    price += shipping_cost
                
                # Comparer avec le prix le plus bas trouvé
                if price < cheapest_price:
                    cheapest_price = price
                    cheapest_supplier = supplier
                
            except Exception as e:
                logger.warning(f"Erreur lors de la récupération des détails chez {supplier}: {str(e)}")
        
        if cheapest_supplier:
            return cheapest_supplier, product_details[cheapest_supplier]
        else:
            return None, {"error": "Aucun fournisseur disponible pour ce produit"}
    
    async def _select_fastest_supplier(self, product_id: str, variant_id: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Sélectionne le fournisseur avec la livraison la plus rapide pour un produit.
        
        Args:
            product_id: ID du produit
            variant_id: ID de la variante (optionnel)
            
        Returns:
            Tuple avec le fournisseur sélectionné et les détails du produit
        """
        # Récupérer les détails chez tous les fournisseurs disponibles
        suppliers = [SupplierType.ALIEXPRESS, SupplierType.CJ_DROPSHIPPING]
        product_details = {}
        fastest_supplier = None
        fastest_delivery = float("inf")
        
        for supplier in suppliers:
            try:
                details = await self.communicator.get_product_details(supplier, product_id)
                
                if not details.get("success", False):
                    continue
                
                product_details[supplier] = details
                
                # Déterminer le délai de livraison
                shipping_methods = details.get("shipping_info", {}).get("methods", [])
                if not shipping_methods:
                    continue
                
                # Extraire les délais de livraison (format habituel: "10-15 days")
                min_delivery_time = float("inf")
                for method in shipping_methods:
                    delivery_time = method.get("delivery_time", "")
                    if delivery_time:
                        try:
                            # Extraire le délai minimum
                            parts = delivery_time.split("-")
                            if len(parts) >= 1 and "days" in delivery_time:
                                try:
                                    min_days = int(parts[0].replace("days", "").strip())
                                    min_delivery_time = min(min_delivery_time, min_days)
                                except ValueError:
                                    pass
                        except (ValueError, IndexError):
                            pass
                
                # Comparer avec le délai le plus court trouvé
                if min_delivery_time < fastest_delivery:
                    fastest_delivery = min_delivery_time
                    fastest_supplier = supplier
                
            except Exception as e:
                logger.warning(f"Erreur lors de la récupération des détails chez {supplier}: {str(e)}")
        
        if fastest_supplier:
            return fastest_supplier, product_details[fastest_supplier]
        else:
            return None, {"error": "Aucun fournisseur disponible pour ce produit"}
    
    async def _select_default_supplier(self, product_id: str, variant_id: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Sélectionne le fournisseur par défaut pour un produit.
        
        Args:
            product_id: ID du produit
            variant_id: ID de la variante (optionnel)
            
        Returns:
            Tuple avec le fournisseur sélectionné et les détails du produit
        """
        try:
            details = await self.communicator.get_product_details(self.default_supplier, product_id)
            
            if details.get("success", False):
                return self.default_supplier, details
            else:
                # Si pas disponible chez le fournisseur par défaut, essayer l'autre fournisseur
                other_supplier = SupplierType.CJ_DROPSHIPPING if self.default_supplier == SupplierType.ALIEXPRESS else SupplierType.ALIEXPRESS
                
                details = await self.communicator.get_product_details(other_supplier, product_id)
                
                if details.get("success", False):
                    return other_supplier, details
                else:
                    return None, {"error": "Produit non disponible"}
                
        except Exception as e:
            logger.error(f"Erreur lors de la sélection du fournisseur par défaut: {str(e)}")
            return None, {"error": f"Erreur: {str(e)}"}
