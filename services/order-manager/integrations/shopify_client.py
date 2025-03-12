import shopify
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

class ShopifyClient:
    """Client pour interagir avec l'API Shopify"""
    
    def __init__(self, shop_url: str, api_key: str, api_password: str):
        """Initialise le client Shopify
        
        Args:
            shop_url: URL de la boutique Shopify
            api_key: Clé API Shopify
            api_password: Mot de passe API Shopify
        """
        self.shop_url = shop_url
        self.api_key = api_key
        self.api_password = api_password
        self.logger = logging.getLogger("order-manager.shopify_client")
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialise la session Shopify"""
        try:
            shopify.ShopifyResource.set_user(self.api_key)
            shopify.ShopifyResource.set_password(self.api_password)
            shopify.ShopifyResource.set_site(f"https://{self.shop_url}")
            self.session = shopify.Session(self.shop_url, "2023-07", self.api_password)
            shopify.ShopifyResource.activate_session(self.session)
            self.logger.info("Session Shopify initialisée avec succès")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation de la session Shopify: {str(e)}")
            raise
    
    def is_connected(self) -> bool:
        """Vérifie si la connexion à Shopify est fonctionnelle
        
        Returns:
            bool: True si la connexion est fonctionnelle, False sinon
        """
        try:
            # Essaie de récupérer le magasin pour vérifier la connexion
            shop = shopify.Shop.current()
            return shop is not None
        except Exception as e:
            self.logger.error(f"Erreur de connexion à Shopify: {str(e)}")
            return False
    
    async def get_order(self, order_id: int) -> Dict:
        """Récupère les détails d'une commande Shopify
        
        Args:
            order_id: Identifiant de la commande
            
        Returns:
            Dict: Détails de la commande
            
        Raises:
            Exception: Si une erreur survient lors de la requête
        """
        try:
            order = shopify.Order.find(order_id)
            return order.to_dict()
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération de la commande {order_id}: {str(e)}")
            raise Exception(f"Erreur lors de la récupération de la commande: {str(e)}")
    
    async def update_order_status(self, order_id: int, status: str, fulfillment_status: Optional[str] = None) -> Dict:
        """Met à jour le statut d'une commande Shopify
        
        Args:
            order_id: Identifiant de la commande
            status: Nouveau statut financier de la commande
            fulfillment_status: Nouveau statut d'exécution de la commande (optionnel)
            
        Returns:
            Dict: Commande mise à jour
            
        Raises:
            Exception: Si une erreur survient lors de la mise à jour
        """
        try:
            order = shopify.Order.find(order_id)
            
            # Mise à jour du statut financier si fourni
            if status:
                order.financial_status = status
            
            # Mise à jour du statut d'exécution si fourni
            if fulfillment_status:
                order.fulfillment_status = fulfillment_status
            
            # Sauvegarde des modifications
            if order.save():
                return order.to_dict()
            else:
                raise Exception(f"Erreur lors de la sauvegarde de la commande: {order.errors.full_messages()}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du statut de la commande {order_id}: {str(e)}")
            raise Exception(f"Erreur lors de la mise à jour du statut: {str(e)}")
    
    async def create_fulfillment(self, order_id: int, tracking_number: str, tracking_company: str) -> Dict:
        """Crée une exécution de commande (fulfillment) dans Shopify
        
        Args:
            order_id: Identifiant de la commande
            tracking_number: Numéro de suivi du colis
            tracking_company: Nom de la société de transport
            
        Returns:
            Dict: Détails de l'exécution créée
            
        Raises:
            Exception: Si une erreur survient lors de la création
        """
        try:
            order = shopify.Order.find(order_id)
            fulfillment = shopify.Fulfillment({
                "order_id": order_id,
                "tracking_number": tracking_number,
                "tracking_company": tracking_company,
                "notify_customer": True
            })
            
            # Ajoute tous les articles de la commande à l'exécution
            line_items = []
            for item in order.line_items:
                line_items.append({
                    "id": item.id,
                    "quantity": item.quantity
                })
            fulfillment.line_items = line_items
            
            # Sauvegarde de l'exécution
            if fulfillment.save():
                return fulfillment.to_dict()
            else:
                raise Exception(f"Erreur lors de la sauvegarde de l'exécution: {fulfillment.errors.full_messages()}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la création de l'exécution pour la commande {order_id}: {str(e)}")
            raise Exception(f"Erreur lors de la création de l'exécution: {str(e)}")
    
    async def get_fulfilled_orders(self, limit: int = 50) -> List[Dict]:
        """Récupère les commandes exécutées
        
        Args:
            limit: Nombre maximum de commandes à récupérer
            
        Returns:
            List[Dict]: Liste des commandes exécutées
            
        Raises:
            Exception: Si une erreur survient lors de la requête
        """
        try:
            orders = shopify.Order.find(
                fulfillment_status="fulfilled",
                limit=limit,
                order="created_at DESC"
            )
            return [order.to_dict() for order in orders]
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des commandes exécutées: {str(e)}")
            raise Exception(f"Erreur lors de la récupération des commandes exécutées: {str(e)}")
    
    async def get_unfulfilled_orders(self, limit: int = 50) -> List[Dict]:
        """Récupère les commandes non exécutées
        
        Args:
            limit: Nombre maximum de commandes à récupérer
            
        Returns:
            List[Dict]: Liste des commandes non exécutées
            
        Raises:
            Exception: Si une erreur survient lors de la requête
        """
        try:
            orders = shopify.Order.find(
                fulfillment_status="null",
                financial_status="paid",
                limit=limit,
                order="created_at DESC"
            )
            return [order.to_dict() for order in orders]
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des commandes non exécutées: {str(e)}")
            raise Exception(f"Erreur lors de la récupération des commandes non exécutées: {str(e)}")
    
    async def cancel_order(self, order_id: int, reason: str = "Customer request") -> Dict:
        """Annule une commande Shopify
        
        Args:
            order_id: Identifiant de la commande
            reason: Raison de l'annulation
            
        Returns:
            Dict: Détails de la commande annulée
            
        Raises:
            Exception: Si une erreur survient lors de l'annulation
        """
        try:
            order = shopify.Order.find(order_id)
            if order.cancel(reason=reason):
                return order.to_dict()
            else:
                raise Exception(f"Erreur lors de l'annulation de la commande: {order.errors.full_messages()}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'annulation de la commande {order_id}: {str(e)}")
            raise Exception(f"Erreur lors de l'annulation de la commande: {str(e)}")
    
    async def refund_order(self, order_id: int, amount: float, reason: str = "Customer request") -> Dict:
        """Effectue un remboursement pour une commande Shopify
        
        Args:
            order_id: Identifiant de la commande
            amount: Montant à rembourser
            reason: Raison du remboursement
            
        Returns:
            Dict: Détails du remboursement
            
        Raises:
            Exception: Si une erreur survient lors du remboursement
        """
        try:
            order = shopify.Order.find(order_id)
            refund = shopify.Refund({
                "order_id": order_id,
                "note": reason,
                "restock": True,
                "notify": True
            })
            
            # Créer une transaction de remboursement
            refund.transactions = [{
                "kind": "refund",
                "amount": str(amount),
                "gateway": order.transactions[0].gateway
            }]
            
            if refund.save():
                return refund.to_dict()
            else:
                raise Exception(f"Erreur lors de la sauvegarde du remboursement: {refund.errors.full_messages()}")
        except Exception as e:
            self.logger.error(f"Erreur lors du remboursement de la commande {order_id}: {str(e)}")
            raise Exception(f"Erreur lors du remboursement de la commande: {str(e)}")
