import logging
import json
import requests
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

class ShipmentTracker:
    """Gestionnaire pour le suivi des expéditions"""
    
    def __init__(self, shopify_client, config_manager):
        """Initialise le tracker d'expédition
        
        Args:
            shopify_client: Client Shopify pour les opérations sur les commandes
            config_manager: Gestionnaire de configuration
        """
        self.shopify_client = shopify_client
        self.config_manager = config_manager
        self.logger = logging.getLogger("order-manager.shipment_tracker")
        
        # Configuration des transporteurs pour le suivi
        self.tracking_providers = self.config_manager.get("tracking_providers", {
            "dhl": "DHL Express",
            "fedex": "FedEx",
            "ups": "UPS",
            "usps": "USPS",
            "post": "La Poste",
            "cainiao": "Cainiao",
            "yanwen": "Yanwen",
            "4px": "4PX Express"
        })
        
        # Base URLs pour le suivi (dans une implémentation réelle, ces URLs seraient utilisées)
        self.tracking_urls = {
            "dhl": "https://www.dhl.com/en/express/tracking.html?AWB={}",
            "fedex": "https://www.fedex.com/fedextrack/?trknbr={}",
            "ups": "https://www.ups.com/track?tracknum={}",
            "usps": "https://tools.usps.com/go/TrackConfirmAction?tLabels={}",
            "post": "https://www.laposte.fr/outils/suivre-vos-envois?code={}",
            "cainiao": "https://global.cainiao.com/detail.htm?mailNoList={}",
            "yanwen": "https://www.trackingmore.com/yanwen-tracking/en.html?number={}",
            "4px": "https://track.4px.com/#/result/0/{}"
        }
    
    async def track_shipment(self, order_id: int, tracking_number: Optional[str] = None, carrier: Optional[str] = None) -> Dict:
        """Suit une expédition pour une commande
        
        Args:
            order_id: Identifiant de la commande
            tracking_number: Numéro de suivi (optionnel, sera récupéré depuis Shopify si non fourni)
            carrier: Code du transporteur (optionnel, sera récupéré depuis Shopify si non fourni)
            
        Returns:
            Dict: Informations sur le statut de l'expédition
            
        Raises:
            Exception: Si une erreur survient lors du suivi
        """
        try:
            # Si le numéro de suivi n'est pas fourni, récupérer depuis Shopify
            if not tracking_number or not carrier:
                tracking_info = await self._get_tracking_from_shopify(order_id)
                tracking_number = tracking_number or tracking_info.get("tracking_number")
                carrier = carrier or tracking_info.get("carrier")
            
            if not tracking_number:
                raise Exception(f"Aucun numéro de suivi trouvé pour la commande {order_id}")
            
            # Récupérer les informations de suivi auprès du transporteur
            shipment_status = await self._get_shipment_status(tracking_number, carrier)
            
            # Mettre à jour le statut dans Shopify si nécessaire
            if shipment_status.get("status") == "delivered":
                await self._update_shopify_fulfillment_status(order_id, "delivered")
            
            # Enrichir les informations de suivi avec des détails suppplémentaires
            tracking_url = self._get_tracking_url(tracking_number, carrier)
            carrier_name = self.tracking_providers.get(carrier.lower(), carrier)
            
            tracking_result = {
                "order_id": order_id,
                "tracking_number": tracking_number,
                "carrier": carrier_name,
                "tracking_url": tracking_url,
                "status": shipment_status.get("status"),
                "status_text": shipment_status.get("status_text"),
                "location": shipment_status.get("location"),
                "last_update": shipment_status.get("last_update"),
                "estimated_delivery": shipment_status.get("estimated_delivery"),
                "events": shipment_status.get("events", [])
            }
            
            self.logger.info(f"Suivi réalisé pour la commande {order_id}: {tracking_result['status']}")
            return tracking_result
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi de l'expédition pour la commande {order_id}: {str(e)}")
            raise Exception(f"Erreur lors du suivi de l'expédition: {str(e)}")
    
    async def update_all_shipments(self, limit: int = 50) -> List[Dict]:
        """Met à jour le statut de toutes les expéditions en cours
        
        Args:
            limit: Nombre maximum de commandes à traiter
            
        Returns:
            List[Dict]: Liste des résultats de mise à jour
        """
        results = []
        try:
            # Récupérer toutes les commandes avec fulfillment
            orders = await self.shopify_client.get_fulfilled_orders(limit)
            
            # Filtrer pour ne garder que les commandes non livrées
            undelivered_orders = [order for order in orders 
                                  if order.get("fulfillment_status") != "delivered" 
                                  and order.get("fulfillments")]
            
            self.logger.info(f"Mise à jour de {len(undelivered_orders)} expéditions en cours")
            
            # Traiter chaque commande
            for order in undelivered_orders:
                try:
                    order_id = order.get("id")
                    tracking_result = await self.track_shipment(order_id)
                    results.append({
                        "order_id": order_id,
                        "status": "updated",
                        "tracking_result": tracking_result
                    })
                except Exception as e:
                    self.logger.error(f"Erreur lors de la mise à jour du suivi pour la commande {order.get('id')}: {str(e)}")
                    results.append({
                        "order_id": order.get("id"),
                        "status": "error",
                        "error": str(e)
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour globale des expéditions: {str(e)}")
            raise Exception(f"Erreur lors de la mise à jour globale: {str(e)}")
    
    async def _get_tracking_from_shopify(self, order_id: int) -> Dict:
        """Récupère les informations de suivi depuis Shopify
        
        Args:
            order_id: Identifiant de la commande
            
        Returns:
            Dict: Informations de suivi
            
        Raises:
            Exception: Si aucune information de suivi n'est trouvée
        """
        try:
            order = await self.shopify_client.get_order(order_id)
            fulfillments = order.get("fulfillments", [])
            
            if not fulfillments:
                raise Exception(f"Aucun fulfillment trouvé pour la commande {order_id}")
            
            # Prendre le dernier fulfillment (le plus récent)
            latest_fulfillment = fulfillments[-1]
            
            tracking_number = latest_fulfillment.get("tracking_number")
            tracking_company = latest_fulfillment.get("tracking_company")
            
            if not tracking_number:
                raise Exception(f"Aucun numéro de suivi trouvé dans le fulfillment pour la commande {order_id}")
            
            # Déterminer le code du transporteur à partir du nom de l'entreprise
            carrier = self._get_carrier_code(tracking_company) if tracking_company else None
            
            return {
                "tracking_number": tracking_number,
                "carrier": carrier,
                "tracking_company": tracking_company,
                "fulfillment_id": latest_fulfillment.get("id")
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des informations de suivi depuis Shopify pour la commande {order_id}: {str(e)}")
            raise Exception(f"Erreur lors de la récupération des informations de suivi: {str(e)}")
    
    async def _get_shipment_status(self, tracking_number: str, carrier: str) -> Dict:
        """Récupère le statut d'une expédition auprès du transporteur
        
        Args:
            tracking_number: Numéro de suivi
            carrier: Code du transporteur
            
        Returns:
            Dict: Statut détaillé de l'expédition
            
        Note:
            Dans une implémentation réelle, cette méthode appellerait l'API du transporteur
            ou un service de tracking tiers comme AfterShip ou ShipEngine.
            Pour cette démonstration, nous simulons une réponse.
        """
        # Simulation de statut d'expédition pour démonstration
        # Dans une implémentation réelle, cette méthode ferait une requête à une API de suivi
        
        # Générer un statut aléatoire pour la démonstration
        statuses = ["pending", "in_transit", "out_for_delivery", "delivered"]
        status_texts = {
            "pending": "En attente d'expédition",
            "in_transit": "En transit",
            "out_for_delivery": "En cours de livraison",
            "delivered": "Livré"
        }
        
        # Pour la démonstration, déterminer un statut basé sur le numéro de suivi
        # Dans une implémentation réelle, cela viendrait de l'API du transporteur
        status_index = hash(tracking_number) % len(statuses)
        status = statuses[status_index]
        
        # Générer des dates pour la démonstration
        now = datetime.now()
        last_update = now - timedelta(days=1, hours=6)
        estimated_delivery = now + timedelta(days=3)
        
        # Pour le statut "delivered", mettre à jour les dates
        if status == "delivered":
            last_update = now - timedelta(hours=2)
            estimated_delivery = last_update
        
        # Générer des événements fictifs pour la démonstration
        events = [
            {
                "timestamp": (now - timedelta(days=3)).isoformat(),
                "status": "pending",
                "location": "Centre de tri d'origine",
                "description": "Colis enregistré dans le système"
            }
        ]
        
        if status_index >= 1:  # in_transit ou supérieur
            events.append({
                "timestamp": (now - timedelta(days=2)).isoformat(),
                "status": "in_transit",
                "location": "Centre de distribution",
                "description": "Colis en transit"
            })
        
        if status_index >= 2:  # out_for_delivery ou supérieur
            events.append({
                "timestamp": (now - timedelta(days=1)).isoformat(),
                "status": "out_for_delivery",
                "location": "Centre de distribution local",
                "description": "Colis en cours de livraison"
            })
        
        if status_index >= 3:  # delivered
            events.append({
                "timestamp": last_update.isoformat(),
                "status": "delivered",
                "location": "Adresse de livraison",
                "description": "Colis livré"
            })
        
        return {
            "status": status,
            "status_text": status_texts.get(status, status),
            "location": events[-1].get("location"),
            "last_update": last_update.isoformat(),
            "estimated_delivery": estimated_delivery.isoformat(),
            "events": events
        }
    
    async def _update_shopify_fulfillment_status(self, order_id: int, status: str) -> bool:
        """Met à jour le statut de fulfillment dans Shopify
        
        Args:
            order_id: Identifiant de la commande
            status: Nouveau statut de fulfillment
            
        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        try:
            # Mettre à jour le statut dans Shopify
            update_result = await self.shopify_client.update_order_status(
                order_id,
                None,  # Ne pas modifier le statut financier
                status
            )
            
            self.logger.info(f"Statut de fulfillment mis à jour pour la commande {order_id}: {status}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du statut de fulfillment pour la commande {order_id}: {str(e)}")
            return False
    
    def _get_tracking_url(self, tracking_number: str, carrier: str) -> str:
        """Génère une URL de suivi pour un transporteur donné
        
        Args:
            tracking_number: Numéro de suivi
            carrier: Code du transporteur
            
        Returns:
            str: URL de suivi
        """
        carrier_lower = carrier.lower() if carrier else ""
        url_template = self.tracking_urls.get(carrier_lower, "")
        
        if url_template:
            return url_template.format(tracking_number)
        else:
            # URL générique de tracking si le transporteur n'est pas reconnu
            return f"https://www.trackingmore.com/track/number/{tracking_number}"
    
    def _get_carrier_code(self, tracking_company: str) -> str:
        """Convertit un nom de transporteur en code
        
        Args:
            tracking_company: Nom du transporteur
            
        Returns:
            str: Code du transporteur ou transporteur d'origine si non reconnu
        """
        if not tracking_company:
            return None
        
        # Conversion en minuscules pour la recherche
        company_lower = tracking_company.lower()
        
        # Recherche dans les noms de transporteurs
        for code, name in self.tracking_providers.items():
            if name.lower() in company_lower or code.lower() in company_lower:
                return code
        
        # Si le transporteur n'est pas reconnu, retourner le nom d'origine
        return tracking_company