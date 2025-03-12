import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

class OrderProcessor:
    """Gestionnaire pour le traitement des commandes"""
    
    def __init__(self, shopify_client, config_manager):
        """Initialise le processeur de commandes
        
        Args:
            shopify_client: Client Shopify pour les opérations sur les commandes
            config_manager: Gestionnaire de configuration
        """
        self.shopify_client = shopify_client
        self.config_manager = config_manager
        self.logger = logging.getLogger("order-manager.order_processor")
    
    async def process_new_order(self, order_data: Dict) -> Dict:
        """Traite une nouvelle commande
        
        Args:
            order_data: Données de la commande à traiter
            
        Returns:
            Dict: Résultat du traitement
            
        Raises:
            Exception: Si une erreur survient lors du traitement
        """
        order_id = order_data.get('id')
        self.logger.info(f"Début du traitement de la commande #{order_id}")
        
        try:
            # Vérifier si la commande nécessite une revue manuelle
            requires_review = await self._requires_manual_review(order_data)
            
            if not requires_review and self.config_manager.get("order_processing.auto_process"):
                # Traitement automatique
                self.logger.info(f"Traitement automatique de la commande #{order_id}")
                return await self.process_order(order_id, "process", False)
            else:
                # Mise en attente pour revue manuelle
                self.logger.info(f"Commande #{order_id} mise en attente pour revue manuelle")
                await self.shopify_client.update_order_status(order_id, "pending", "on_hold")
                return {
                    "status": "pending_review",
                    "order_id": order_id,
                    "message": "Commande en attente de revue manuelle",
                    "requires_review_reason": "Seuil de valeur dépassé" if requires_review else "Traitement automatique désactivé"
                }
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement initial de la commande #{order_id}: {str(e)}")
            raise Exception(f"Erreur lors du traitement initial: {str(e)}")
    
    async def process_order(self, order_id: int, action: str, manual_review: bool = False) -> Dict:
        """Traite une commande spécifique
        
        Args:
            order_id: Identifiant de la commande
            action: Action à effectuer ('process', 'cancel', 'refund')
            manual_review: Indique si la commande a été revue manuellement
            
        Returns:
            Dict: Résultat du traitement
            
        Raises:
            Exception: Si une erreur survient lors du traitement
        """
        self.logger.info(f"Traitement de la commande #{order_id} avec action '{action}'")
        
        try:
            # Récupérer les détails de la commande
            order_details = await self.shopify_client.get_order(order_id)
            
            if action == "process":
                # Traiter la commande auprès du fournisseur
                supplier_info = await self._determine_supplier(order_details)
                processing_result = await self._forward_to_supplier(order_details, supplier_info)
                
                # Mettre à jour le statut de la commande
                await self.shopify_client.update_order_status(
                    order_id, 
                    "processing", 
                    "in_progress"
                )
                
                # Si des informations de suivi sont disponibles, créer un fulfillment
                if processing_result.get("tracking_number") and processing_result.get("carrier"):
                    await self.shopify_client.create_fulfillment(
                        order_id,
                        processing_result.get("tracking_number"),
                        processing_result.get("carrier")
                    )
                
                return {
                    "status": "processed",
                    "order_id": order_id,
                    "supplier": supplier_info.get("name"),
                    "tracking_info": processing_result.get("tracking_info"),
                    "message": "Commande traitée avec succès"
                }
                
            elif action == "cancel":
                # Annuler la commande
                cancel_result = await self.shopify_client.cancel_order(order_id, "Customer request")
                
                return {
                    "status": "cancelled",
                    "order_id": order_id,
                    "message": "Commande annulée avec succès"
                }
                
            elif action == "refund":
                # Effectuer un remboursement
                refund_amount = float(order_details.get("total_price", 0))
                refund_result = await self.shopify_client.refund_order(order_id, refund_amount)
                
                return {
                    "status": "refunded",
                    "order_id": order_id,
                    "amount": refund_amount,
                    "message": "Commande remboursée avec succès"
                }
                
            else:
                raise Exception(f"Action non supportée: {action}")
                
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de l'action '{action}' pour la commande #{order_id}: {str(e)}")
            raise Exception(f"Erreur lors du traitement: {str(e)}")
    
    async def get_order_status(self, order_id: int) -> Dict:
        """Récupère le statut d'une commande
        
        Args:
            order_id: Identifiant de la commande
            
        Returns:
            Dict: Informations sur le statut de la commande
            
        Raises:
            Exception: Si une erreur survient lors de la récupération
        """
        try:
            order = await self.shopify_client.get_order(order_id)
            
            status_info = {
                "order_id": order_id,
                "financial_status": order.get("financial_status"),
                "fulfillment_status": order.get("fulfillment_status"),
                "created_at": order.get("created_at"),
                "updated_at": order.get("updated_at"),
                "processed_at": order.get("processed_at"),
                "cancelled_at": order.get("cancelled_at"),
                "refunds": []
            }
            
            # Ajouter les informations de fulfillment si disponibles
            fulfillments = order.get("fulfillments", [])
            if fulfillments:
                status_info["fulfillments"] = [{
                    "id": f.get("id"),
                    "tracking_number": f.get("tracking_number"),
                    "tracking_company": f.get("tracking_company"),
                    "status": f.get("status"),
                    "created_at": f.get("created_at")
                } for f in fulfillments]
            
            # Ajouter les informations de remboursement si disponibles
            refunds = order.get("refunds", [])
            if refunds:
                status_info["refunds"] = [{
                    "id": r.get("id"),
                    "amount": r.get("transactions", [{}])[0].get("amount") if r.get("transactions") else None,
                    "created_at": r.get("created_at")
                } for r in refunds]
            
            return status_info
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du statut de la commande #{order_id}: {str(e)}")
            raise Exception(f"Erreur lors de la récupération du statut: {str(e)}")
    
    async def _requires_manual_review(self, order_data: Dict) -> bool:
        """Détermine si une commande nécessite une revue manuelle
        
        Args:
            order_data: Données de la commande
            
        Returns:
            bool: True si la commande nécessite une revue manuelle, False sinon
        """
        try:
            # Récupérer le seuil de revue manuelle depuis la configuration
            threshold = self.config_manager.get("order_processing.manual_review_threshold", 100.0)
            
            # Vérifier si le montant total dépasse le seuil
            total_price = float(order_data.get("total_price", 0))
            if total_price > threshold:
                self.logger.info(f"Commande #{order_data.get('id')} nécessite une revue manuelle (montant: {total_price}€, seuil: {threshold}€)")
                return True
            
            # Vérifier d'autres critères si nécessaire...
            # Par exemple, nouvelles adresses de livraison, produits spécifiques, etc.
            
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification de revue manuelle: {str(e)}")
            # En cas d'erreur, on préfère demander une revue manuelle par sécurité
            return True
    
    async def _determine_supplier(self, order_details: Dict) -> Dict:
        """Détermine le fournisseur à utiliser pour la commande
        
        Args:
            order_details: Détails de la commande
            
        Returns:
            Dict: Informations sur le fournisseur
            
        Raises:
            Exception: Si aucun fournisseur n'est trouvé
        """
        # Dans une implémentation réelle, cette logique serait plus complexe
        # et déterminerait le fournisseur en fonction des produits commandés
        
        # Pour simplifier, nous utilisons le premier fournisseur disponible
        suppliers = self.config_manager.get_all_suppliers()
        if not suppliers:
            raise Exception("Aucun fournisseur configuré")
        
        # Prendre le premier fournisseur disponible (AliExpress par défaut)
        supplier_id = "aliexpress" if "aliexpress" in suppliers else list(suppliers.keys())[0]
        supplier_info = suppliers.get(supplier_id, {})
        
        if not supplier_info:
            raise Exception(f"Informations du fournisseur {supplier_id} introuvables")
        
        return {
            "id": supplier_id,
            "name": supplier_info.get("name", supplier_id),
            "api_url": supplier_info.get("api_url", ""),
            "api_key": supplier_info.get("api_key", ""),
            "order_endpoint": supplier_info.get("order_endpoint", "/api/orders"),
            "tracking_endpoint": supplier_info.get("tracking_endpoint", "/api/tracking")
        }
    
    async def _forward_to_supplier(self, order_details: Dict, supplier_info: Dict) -> Dict:
        """Transmet la commande au fournisseur
        
        Args:
            order_details: Détails de la commande
            supplier_info: Informations sur le fournisseur
            
        Returns:
            Dict: Résultat du traitement par le fournisseur
            
        Raises:
            Exception: Si une erreur survient lors de la transmission
        """
        # Dans une implémentation réelle, cette méthode enverrait réellement
        # la commande au fournisseur via son API
        
        # Simulation d'une réponse réussie pour le moment
        self.logger.info(f"Transmission de la commande #{order_details.get('id')} au fournisseur {supplier_info.get('name')}")
        
        # Simuler un délai (dans une implémentation réelle, ce serait une vraie requête API)
        # time.sleep(2)
        
        # Simuler une réponse de l'API du fournisseur
        supplier_order_id = f"SUP-{order_details.get('id')}-{datetime.now().strftime('%Y%m%d')}"
        
        return {
            "success": True,
            "supplier_order_id": supplier_order_id,
            "supplier": supplier_info.get("name"),
            "status": "processing",
            "estimated_shipping_date": (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                                         .strftime("%Y-%m-%d")),
            "tracking_number": None,  # Sera fourni plus tard par le fournisseur
            "carrier": None,  # Sera fourni plus tard par le fournisseur
            "message": "Commande transférée avec succès au fournisseur"
        }
