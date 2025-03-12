#!/usr/bin/env python3
"""
Fonctionnalités de gestion des livraisons pour l'agent Order Manager
Fait partie du projet Dropshipping Crew AI

Ce module contient les méthodes de OrderService liées à la vérification des livraisons.
"""

from datetime import datetime, timedelta
from typing import List
from loguru import logger

from models import Order, OrderStatus, SupplierOrder, ShippingInfo

async def _check_delivered_orders(self):
    """
    Vérifie les commandes livrées pour finalisation.
    """
    # Récupération des commandes en statut "shipped"
    shipped_orders = await self.repository.get_orders_by_status(OrderStatus.SHIPPED)
    
    if not shipped_orders:
        return
    
    for order in shipped_orders:
        try:
            # Récupération des commandes fournisseurs associées
            supplier_orders = await self.repository.get_supplier_orders_for_order(order.id)
            
            # Vérification du statut des commandes fournisseurs
            all_delivered = all(so.status == "delivered" for so in supplier_orders)
            
            if all_delivered:
                # Mise à jour du statut de la commande principale
                order.status = OrderStatus.DELIVERED
                order.updated_at = datetime.now().isoformat()
                await self.repository.update_order(order)
                
                # Envoi d'une notification de livraison
                await self.notification_manager.send_delivery_confirmation(order)
            
            # Vérification des commandes expédiées depuis longtemps (plus de 30 jours)
            else:
                shipping_date = datetime.fromisoformat(order.updated_at)
                days_since_shipping = (datetime.now() - shipping_date).days
                
                if days_since_shipping > 30:
                    # Vérification manuelle des statuts auprès des fournisseurs
                    await self._verify_delivery_status(order, supplier_orders)
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la commande expédiée {order.id}: {str(e)}")

async def _verify_delivery_status(self, order: Order, supplier_orders: List[SupplierOrder]):
    """
    Vérifie manuellement le statut de livraison des commandes fournisseurs.
    
    Args:
        order: Commande principale
        supplier_orders: Liste des commandes fournisseurs associées
    """
    status_updated = False
    
    for supplier_order in supplier_orders:
        if supplier_order.status != "delivered":
            # Vérification du statut auprès du fournisseur
            status_result = await self.supplier_communicator.check_order_status(
                supplier_order.supplier_type,
                supplier_order.supplier_order_id
            )
            
            if status_result.success and status_result.status == "delivered":
                # Mise à jour du statut de la commande fournisseur
                supplier_order.status = "delivered"
                supplier_order.updated_at = datetime.now().isoformat()
                await self.repository.update_supplier_order(supplier_order)
                status_updated = True
    
    # Si toutes les commandes sont maintenant livrées, mise à jour de la commande principale
    if status_updated:
        supplier_orders = await self.repository.get_supplier_orders_for_order(order.id)
        all_delivered = all(so.status == "delivered" for so in supplier_orders)
        
        if all_delivered:
            order.status = OrderStatus.DELIVERED
            order.updated_at = datetime.now().isoformat()
            await self.repository.update_order(order)
            
            # Envoi d'une notification de livraison
            await self.notification_manager.send_delivery_confirmation(order)

def _compile_shipping_info(self, supplier_orders: List[SupplierOrder]) -> ShippingInfo:
    """
    Compile les informations d'expédition à partir des commandes fournisseurs.
    
    Args:
        supplier_orders: Liste des commandes fournisseurs
        
    Returns:
        Informations d'expédition compilées
    """
    tracking_numbers = []
    carriers = []
    estimated_delivery_dates = []
    tracking_urls = []
    
    for so in supplier_orders:
        if so.tracking_info:
            tracking_numbers.append(so.tracking_info.get("tracking_number", ""))
            carriers.append(so.tracking_info.get("carrier", ""))
            
            if "estimated_delivery_date" in so.tracking_info:
                estimated_delivery_dates.append(so.tracking_info.get("estimated_delivery_date"))
            
            if "tracking_url" in so.tracking_info:
                tracking_urls.append(so.tracking_info.get("tracking_url"))
    
    # Détermination de la date de livraison estimée (la plus éloignée)
    estimated_delivery = None
    if estimated_delivery_dates:
        try:
            dates = [datetime.fromisoformat(date) for date in estimated_delivery_dates if date]
            if dates:
                estimated_delivery = max(dates).isoformat()
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la date de livraison estimée: {str(e)}")
    
    # Si pas de date estimée, estimation standard (15 jours)
    if not estimated_delivery:
        estimated_delivery = (datetime.now() + timedelta(days=15)).isoformat()
    
    return ShippingInfo(
        tracking_numbers=tracking_numbers,
        carriers=carriers,
        estimated_delivery=estimated_delivery,
        tracking_urls=tracking_urls
    )

async def _check_shipped_orders(self):
    """
    Vérifie les commandes expédiées pour notifier les clients.
    """
    # Récupération des commandes expédiées récemment (moins de 24h)
    cutoff_time = (datetime.now() - timedelta(hours=24)).isoformat()
    shipped_orders = await self.repository.get_recently_shipped_orders(cutoff_time)
    
    if not shipped_orders:
        return
    
    # Traitement de chaque commande expédiée
    for order in shipped_orders:
        try:
            # Vérification si la notification a déjà été envoyée
            if await self.notification_manager.is_notification_sent(order.id, "shipping"):
                continue
            
            # Récupération des commandes fournisseurs associées
            supplier_orders = await self.repository.get_supplier_orders_for_order(order.id)
            
            # Compilation des informations d'expédition
            shipping_info = self._compile_shipping_info(supplier_orders)
            
            # Envoi de la notification d'expédition
            await self.notification_manager.send_shipping_confirmation(order, shipping_info)
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la commande expédiée {order.id}: {str(e)}")
