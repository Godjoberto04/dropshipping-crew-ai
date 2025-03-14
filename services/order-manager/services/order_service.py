#!/usr/bin/env python3
"""
Service de gestion des commandes pour l'agent Order Manager
Fait partie du projet Dropshipping Crew AI

Ce module contient la classe OrderService qui fournit les fonctionnalités principales
de gestion des commandes pour l'agent Order Manager.
"""

import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from loguru import logger

from models import Order, OrderStatus, SupplierOrder, SupplierType, ShippingInfo
from storage import OrderRepository
from integrations.shopify import ShopifyClient
from integrations.suppliers import SupplierCommunicator
from notifications import NotificationManager, NotificationType

# Import des méthodes externes
from .order_service_suppliers import (
    _group_products_by_supplier, _determine_supplier_type, _extract_supplier_data,
    _create_supplier_order, _send_order_to_supplier, _check_supplier_order_updates,
    _update_supplier_order_status
)
from .order_service_delivery import (
    _check_delivered_orders, _verify_delivery_status, _compile_shipping_info, _check_shipped_orders
)

class OrderService:
    """
    Service principal pour la gestion des commandes dropshipping.
    
    Ce service s'occupe de la coordination entre la boutique en ligne,
    les fournisseurs et le stockage des commandes.
    """
    
    # Import des méthodes externes
    _group_products_by_supplier = _group_products_by_supplier
    _determine_supplier_type = _determine_supplier_type
    _extract_supplier_data = _extract_supplier_data
    _create_supplier_order = _create_supplier_order
    _send_order_to_supplier = _send_order_to_supplier
    _check_supplier_order_updates = _check_supplier_order_updates
    _update_supplier_order_status = _update_supplier_order_status
    _check_delivered_orders = _check_delivered_orders
    _verify_delivery_status = _verify_delivery_status
    _compile_shipping_info = _compile_shipping_info
    _check_shipped_orders = _check_shipped_orders
    
    def __init__(
        self, 
        repository: OrderRepository,
        shopify_client: ShopifyClient,
        supplier_communicator: SupplierCommunicator,
        notification_manager: NotificationManager
    ):
        """
        Initialise le service de gestion des commandes.
        
        Args:
            repository: Repository pour l'accès aux données des commandes
            shopify_client: Client pour interagir avec Shopify
            supplier_communicator: Communicateur avec les fournisseurs
            notification_manager: Gestionnaire de notifications
        """
        self.repository = repository
        self.shopify_client = shopify_client
        self.supplier_communicator = supplier_communicator
        self.notification_manager = notification_manager
        self.running = False
        self.polling_task = None
    
    async def start(self):
        """
        Démarre le service et initialise la boucle de polling des commandes.
        """
        if self.running:
            logger.warning("Tentative de démarrage d'un service déjà en cours d'exécution")
            return
        
        self.running = True
        self.polling_task = asyncio.create_task(self._polling_loop())
        logger.info("Service de gestion des commandes démarré")
    
    async def stop(self):
        """
        Arrête le service et la boucle de polling.
        """
        if not self.running:
            logger.warning("Tentative d'arrêt d'un service qui n'est pas en cours d'exécution")
            return
        
        self.running = False
        if self.polling_task:
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
            self.polling_task = None
        
        logger.info("Service de gestion des commandes arrêté")
    
    async def _polling_loop(self):
        """
        Boucle de polling pour vérifier les nouvelles commandes et les mises à jour.
        """
        try:
            while self.running:
                try:
                    # Vérification des nouvelles commandes sur Shopify
                    await self._check_new_orders()
                    
                    # Vérification des mises à jour des commandes fournisseurs
                    await self._check_supplier_order_updates()
                    
                    # Vérification des commandes expédiées pour notifier les clients
                    await self._check_shipped_orders()
                    
                    # Vérification des commandes livrées pour finalisation
                    await self._check_delivered_orders()
                    
                    # Pause avant la prochaine itération
                    await asyncio.sleep(300)  # 5 minutes
                    
                except Exception as e:
                    logger.error(f"Erreur dans la boucle de polling: {str(e)}")
                    await asyncio.sleep(60)  # Pause courte en cas d'erreur
        
        except asyncio.CancelledError:
            logger.info("Boucle de polling arrêtée")
            raise
    
    async def _check_new_orders(self):
        """
        Vérifie les nouvelles commandes sur Shopify et les traite.
        """
        # Récupération de la dernière commande traitée
        last_processed_order = await self.repository.get_last_processed_order_id()
        
        # Récupération des nouvelles commandes depuis Shopify
        new_orders = await self.shopify_client.get_new_orders(since_id=last_processed_order)
        
        if not new_orders:
            logger.info("Aucune nouvelle commande trouvée")
            return
        
        logger.info(f"{len(new_orders)} nouvelles commandes trouvées")
        
        # Traitement de chaque nouvelle commande
        for shopify_order in new_orders:
            try:
                # Conversion en modèle interne
                order = self._convert_shopify_to_order(shopify_order)
                
                # Enregistrement de la commande dans le repository
                success = await self.repository.add_order(order)
                
                if not success:
                    logger.error(f"Échec de l'enregistrement de la commande {order.id}")
                    continue
                
                # Notification de réception de commande
                await self._send_order_received_notification(order)
                
                # Traitement de la commande
                await self._process_new_order(order)
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement de la commande Shopify {shopify_order.get('id')}: {str(e)}")
    
    async def _send_order_received_notification(self, order: Order):
        """
        Envoie une notification de réception de commande au client.
        
        Args:
            order: Commande reçue
        """
        try:
            customer_name = f"{order.customer.get('first_name', '')} {order.customer.get('last_name', '')}".strip()
            customer_email = order.customer.get('email')
            
            if not customer_email:
                logger.warning(f"Impossible d'envoyer une notification pour la commande {order.id}: email client manquant")
                return
            
            await self.notification_manager.notify_order_status(
                order_id=order.id,
                customer_email=customer_email,
                customer_name=customer_name if customer_name else "Client",
                status=NotificationType.ORDER_PLACED
            )
            
            logger.info(f"Notification de réception envoyée pour la commande {order.id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification de réception pour la commande {order.id}: {str(e)}")
    
    def _convert_shopify_to_order(self, shopify_order: Dict[str, Any]) -> Order:
        """
        Convertit une commande Shopify en modèle interne Order.
        
        Args:
            shopify_order: Commande Shopify au format JSON
            
        Returns:
            Commande au format interne
        """
        # Extraction des informations de base de la commande
        order_id = str(shopify_order.get('id'))
        shopify_created_at = shopify_order.get('created_at')
        customer = shopify_order.get('customer', {})
        shipping_address = shopify_order.get('shipping_address', {})
        line_items = shopify_order.get('line_items', [])
        
        # Création de l'objet Order
        order = Order(
            id=order_id,
            shopify_id=order_id,
            status=OrderStatus.NEW,
            customer={
                'id': str(customer.get('id')) if customer.get('id') else None,
                'email': customer.get('email'),
                'first_name': customer.get('first_name'),
                'last_name': customer.get('last_name'),
                'phone': customer.get('phone')
            },
            shipping_address={
                'first_name': shipping_address.get('first_name'),
                'last_name': shipping_address.get('last_name'),
                'address1': shipping_address.get('address1'),
                'address2': shipping_address.get('address2'),
                'city': shipping_address.get('city'),
                'province': shipping_address.get('province'),
                'country': shipping_address.get('country'),
                'zip': shipping_address.get('zip'),
                'phone': shipping_address.get('phone')
            },
            line_items=line_items,
            total_price=float(shopify_order.get('total_price', 0)),
            currency=shopify_order.get('currency', 'USD'),
            created_at=shopify_created_at or datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            error_message=None
        )
        
        return order
    
    async def _process_new_order(self, order: Order):
        """
        Traite une nouvelle commande.
        
        Args:
            order: Commande à traiter
        """
        try:
            # Répartition des produits par fournisseur
            supplier_groups = await self._group_products_by_supplier(order)
            
            # Création des commandes fournisseurs
            for supplier_type, line_items in supplier_groups.items():
                supplier_order = await self._create_supplier_order(order, supplier_type, line_items)
                
                # Enregistrement de la commande fournisseur
                success = await self.repository.add_supplier_order(supplier_order)
                
                if not success:
                    logger.error(f"Échec de l'enregistrement de la commande fournisseur {supplier_order.id}")
                    continue
                
                # Envoi de la commande au fournisseur
                await self._send_order_to_supplier(supplier_order)
            
            # Mise à jour du statut de la commande principale
            order.status = OrderStatus.PROCESSING
            await self.repository.update_order(order)
            
            # Notification au client de confirmation de commande
            await self._send_order_confirmed_notification(order)
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la commande {order.id}: {str(e)}")
            order.status = OrderStatus.ERROR
            order.error_message = str(e)
            await self.repository.update_order(order)
            
            # Notification d'erreur aux administrateurs
            await self._send_order_issue_notification(order, str(e))
    
    async def _send_order_confirmed_notification(self, order: Order):
        """
        Envoie une notification de confirmation de commande au client.
        
        Args:
            order: Commande confirmée
        """
        try:
            customer_name = f"{order.customer.get('first_name', '')} {order.customer.get('last_name', '')}".strip()
            customer_email = order.customer.get('email')
            
            if not customer_email:
                logger.warning(f"Impossible d'envoyer une notification pour la commande {order.id}: email client manquant")
                return
            
            await self.notification_manager.notify_order_status(
                order_id=order.id,
                customer_email=customer_email,
                customer_name=customer_name if customer_name else "Client",
                status=NotificationType.ORDER_CONFIRMED
            )
            
            logger.info(f"Notification de confirmation envoyée pour la commande {order.id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification de confirmation pour la commande {order.id}: {str(e)}")
    
    async def _send_order_issue_notification(self, order: Order, issue_details: str):
        """
        Envoie une notification d'erreur de commande aux administrateurs.
        
        Args:
            order: Commande en erreur
            issue_details: Détails du problème
        """
        try:
            customer_name = f"{order.customer.get('first_name', '')} {order.customer.get('last_name', '')}".strip()
            
            # Extraction des noms de produits concernés
            product_names = [item.get('title', 'Produit inconnu') for item in order.line_items]
            
            # Notification aux administrateurs
            await self.notification_manager.notify_stock_issue(
                order_id=order.id,
                customer_name=customer_name if customer_name else "Client",
                product_names=product_names,
                supplier="Multiple", # Générique car nous ne savons pas quel fournisseur a causé le problème
                issue_details=issue_details
            )
            
            logger.info(f"Notification d'erreur envoyée aux administrateurs pour la commande {order.id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification d'erreur pour la commande {order.id}: {str(e)}")
    
    async def _update_original_order_status(self, order_id: str):
        """
        Met à jour le statut de la commande principale en fonction des commandes fournisseurs.
        
        Args:
            order_id: Identifiant de la commande principale
        """
        # Récupération de la commande principale
        order = await self.repository.get_order(order_id)
        if not order:
            logger.error(f"Commande {order_id} introuvable")
            return
        
        # Récupération de toutes les commandes fournisseurs associées
        supplier_orders = await self.repository.get_supplier_orders_for_order(order_id)
        
        if not supplier_orders:
            logger.warning(f"Aucune commande fournisseur trouvée pour la commande {order_id}")
            return
        
        # Vérification si toutes les commandes sont expédiées
        all_shipped = all(so.status in ["shipped", "delivered"] for so in supplier_orders)
        all_delivered = all(so.status == "delivered" for so in supplier_orders)
        
        # Mise à jour du statut de la commande principale
        status_changed = False
        
        if all_delivered and order.status != OrderStatus.DELIVERED:
            order.status = OrderStatus.DELIVERED
            status_changed = True
            
            # Notification de livraison
            await self._send_delivery_notification(order)
            
        elif all_shipped and order.status != OrderStatus.SHIPPED and not all_delivered:
            order.status = OrderStatus.SHIPPED
            status_changed = True
            
            # Notification d'expédition
            shipping_info = self._compile_shipping_info(supplier_orders)
            await self._send_shipping_notification(order, shipping_info)
        
        if status_changed:
            # Mise à jour de la commande principale
            order.updated_at = datetime.now().isoformat()
            await self.repository.update_order(order)
    
    async def _send_shipping_notification(self, order: Order, shipping_info: Dict[str, Any]):
        """
        Envoie une notification d'expédition au client.
        
        Args:
            order: Commande expédiée
            shipping_info: Informations d'expédition
        """
        try:
            customer_name = f"{order.customer.get('first_name', '')} {order.customer.get('last_name', '')}".strip()
            customer_email = order.customer.get('email')
            
            if not customer_email:
                logger.warning(f"Impossible d'envoyer une notification d'expédition pour la commande {order.id}: email client manquant")
                return
            
            # Préparation des données pour la notification
            tracking_info = shipping_info.get('tracking_info', [])
            if tracking_info:
                # Si plusieurs numéros de suivi, utiliser le premier pour la notification
                first_tracking = tracking_info[0]
                additional_data = {
                    "tracking_number": first_tracking.get('tracking_number', 'N/A'),
                    "carrier": first_tracking.get('carrier', 'N/A'),
                    "tracking_url": first_tracking.get('tracking_url', '#'),
                    "ship_date": first_tracking.get('ship_date', datetime.now().strftime("%Y-%m-%d")),
                    "delivery_date": first_tracking.get('estimated_delivery', 'À déterminer')
                }
                
                # Si plusieurs numéros de suivi, les ajouter en complément
                if len(tracking_info) > 1:
                    additional_tracking = "\n\nInformations de suivi supplémentaires:\n"
                    for i, track in enumerate(tracking_info[1:], 2):
                        additional_tracking += f"Colis {i}: {track.get('tracking_number', 'N/A')} - {track.get('carrier', 'N/A')} - {track.get('tracking_url', '#')}\n"
                    additional_data["additional_tracking"] = additional_tracking
            else:
                additional_data = {
                    "tracking_number": "N/A",
                    "carrier": "N/A",
                    "tracking_url": "#",
                    "ship_date": datetime.now().strftime("%Y-%m-%d"),
                    "delivery_date": "À déterminer"
                }
            
            await self.notification_manager.notify_order_status(
                order_id=order.id,
                customer_email=customer_email,
                customer_name=customer_name if customer_name else "Client",
                status=NotificationType.SHIPPED,
                additional_data=additional_data
            )
            
            logger.info(f"Notification d'expédition envoyée pour la commande {order.id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification d'expédition pour la commande {order.id}: {str(e)}")
    
    async def _send_delivery_notification(self, order: Order):
        """
        Envoie une notification de livraison au client.
        
        Args:
            order: Commande livrée
        """
        try:
            customer_name = f"{order.customer.get('first_name', '')} {order.customer.get('last_name', '')}".strip()
            customer_email = order.customer.get('email')
            
            if not customer_email:
                logger.warning(f"Impossible d'envoyer une notification de livraison pour la commande {order.id}: email client manquant")
                return
            
            await self.notification_manager.notify_order_status(
                order_id=order.id,
                customer_email=customer_email,
                customer_name=customer_name if customer_name else "Client",
                status=NotificationType.DELIVERED
            )
            
            logger.info(f"Notification de livraison envoyée pour la commande {order.id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification de livraison pour la commande {order.id}: {str(e)}")
    
    async def _send_delivery_update_notification(self, order: Order, tracking_info: Dict[str, Any]):
        """
        Envoie une notification de mise à jour de livraison au client.
        
        Args:
            order: Commande en cours de livraison
            tracking_info: Informations de suivi mises à jour
        """
        try:
            customer_name = f"{order.customer.get('first_name', '')} {order.customer.get('last_name', '')}".strip()
            customer_email = order.customer.get('email')
            
            if not customer_email:
                logger.warning(f"Impossible d'envoyer une notification de mise à jour pour la commande {order.id}: email client manquant")
                return
            
            additional_data = {
                "status": tracking_info.get('status', 'En transit'),
                "location": tracking_info.get('location', 'Inconnu'),
                "tracking_url": tracking_info.get('tracking_url', '#'),
                "delivery_date": tracking_info.get('estimated_delivery', 'À déterminer')
            }
            
            await self.notification_manager.notify_order_status(
                order_id=order.id,
                customer_email=customer_email,
                customer_name=customer_name if customer_name else "Client",
                status=NotificationType.DELIVERY_UPDATE,
                additional_data=additional_data
            )
            
            logger.info(f"Notification de mise à jour de livraison envoyée pour la commande {order.id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification de mise à jour pour la commande {order.id}: {str(e)}")
    
    # Méthodes publiques pour les API
    
    async def get_order(self, order_id: str) -> Optional[Order]:
        """
        Récupère une commande par son identifiant.
        
        Args:
            order_id: Identifiant de la commande
            
        Returns:
            Commande ou None si non trouvée
        """
        return await self.repository.get_order(order_id)
    
    async def get_orders_by_status(self, status: str) -> List[Order]:
        """
        Récupère les commandes par statut.
        
        Args:
            status: Statut des commandes à récupérer
            
        Returns:
            Liste des commandes ayant le statut spécifié
        """
        return await self.repository.get_orders_by_status(status)
    
    async def get_order_with_suppliers(self, order_id: str) -> Tuple[Optional[Order], List[SupplierOrder]]:
        """
        Récupère une commande et ses commandes fournisseurs associées.
        
        Args:
            order_id: Identifiant de la commande
            
        Returns:
            Tuple (commande, liste des commandes fournisseurs)
        """
        order = await self.repository.get_order(order_id)
        if not order:
            return None, []
        
        supplier_orders = await self.repository.get_supplier_orders_for_order(order_id)
        return order, supplier_orders
    
    async def retry_failed_order(self, order_id: str) -> bool:
        """
        Retente le traitement d'une commande en échec.
        
        Args:
            order_id: Identifiant de la commande
            
        Returns:
            Succès de l'opération
        """
        order = await self.repository.get_order(order_id)
        if not order or order.status != OrderStatus.ERROR:
            logger.error(f"Impossible de retenter la commande {order_id}: commande introuvable ou non en échec")
            return False
        
        # Réinitialisation de la commande
        order.status = OrderStatus.NEW
        order.error_message = None
        order.updated_at = datetime.now().isoformat()
        
        # Mise à jour dans le repository
        success = await self.repository.update_order(order)
        if not success:
            logger.error(f"Erreur lors de la mise à jour de la commande {order_id} avant nouvelle tentative")
            return False
        
        # Nouvelle tentative de traitement
        try:
            await self._process_new_order(order)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la nouvelle tentative de traitement de la commande {order_id}: {str(e)}")
            return False
    
    async def retry_failed_supplier_order(self, supplier_order_id: str) -> bool:
        """
        Retente l'envoi d'une commande fournisseur en échec.
        
        Args:
            supplier_order_id: Identifiant de la commande fournisseur
            
        Returns:
            Succès de l'opération
        """
        supplier_order = await self.repository.get_supplier_order(supplier_order_id)
        if not supplier_order or supplier_order.status != "error":
            logger.error(f"Impossible de retenter la commande fournisseur {supplier_order_id}: commande introuvable ou non en échec")
            return False
        
        # Réinitialisation de la commande fournisseur
        supplier_order.status = "pending"
        supplier_order.updated_at = datetime.now().isoformat()
        supplier_order.errors.append({
            "timestamp": datetime.now().isoformat(),
            "message": "Nouvelle tentative manuelle"
        })
        
        # Mise à jour dans le repository
        success = await self.repository.update_supplier_order(supplier_order)
        if not success:
            logger.error(f"Erreur lors de la mise à jour de la commande fournisseur {supplier_order_id} avant nouvelle tentative")
            return False
        
        # Nouvelle tentative d'envoi
        return await self._send_order_to_supplier(supplier_order)
    
    async def cancel_order(self, order_id: str, reason: str) -> bool:
        """
        Annule une commande et ses commandes fournisseurs associées.
        
        Args:
            order_id: Identifiant de la commande
            reason: Raison de l'annulation
            
        Returns:
            Succès de l'opération
        """
        # Récupération de la commande
        order = await self.repository.get_order(order_id)
        if not order:
            logger.error(f"Impossible d'annuler la commande {order_id}: commande introuvable")
            return False
        
        # Vérification que la commande n'est pas déjà expédiée ou livrée
        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            logger.error(f"Impossible d'annuler la commande {order_id}: commande déjà expédiée ou livrée")
            return False
        
        # Récupération des commandes fournisseurs
        supplier_orders = await self.repository.get_supplier_orders_for_order(order_id)
        
        # Annulation des commandes fournisseurs
        supplier_cancel_success = True
        for supplier_order in supplier_orders:
            # On peut annuler uniquement les commandes en attente ou en traitement
            if supplier_order.status in ["pending", "processing"]:
                # Tentative d'annulation auprès du fournisseur si la commande a un ID fournisseur
                if supplier_order.supplier_order_id:
                    cancel_result = await self.supplier_communicator.cancel_order(
                        supplier_order.supplier_type,
                        supplier_order.supplier_order_id,
                        reason
                    )
                    
                    if not cancel_result.success:
                        logger.error(f"Erreur lors de l'annulation de la commande fournisseur {supplier_order.id}: {cancel_result.error_message}")
                        supplier_cancel_success = False
                        continue
                
                # Mise à jour du statut de la commande fournisseur
                supplier_order.status = "cancelled"
                supplier_order.updated_at = datetime.now().isoformat()
                supplier_order.errors.append({
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Annulation: {reason}"
                })
                
                await self.repository.update_supplier_order(supplier_order)
        
        # Mise à jour du statut de la commande principale
        order.status = OrderStatus.CANCELLED
        order.error_message = f"Annulation: {reason}"
        order.updated_at = datetime.now().isoformat()
        
        order_update_success = await self.repository.update_order(order)
        
        # Notification au client d'annulation
        try:
            customer_name = f"{order.customer.get('first_name', '')} {order.customer.get('last_name', '')}".strip()
            customer_email = order.customer.get('email')
            
            if customer_email:
                await self.notification_manager.notify_order_status(
                    order_id=order.id,
                    customer_email=customer_email,
                    customer_name=customer_name if customer_name else "Client",
                    status=NotificationType.ORDER_ISSUE,
                    additional_data={"issue_details": f"Votre commande a été annulée. Raison: {reason}"}
                )
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification d'annulation: {str(e)}")
        
        return supplier_cancel_success and order_update_success
