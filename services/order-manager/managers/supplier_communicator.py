import logging
import json
import requests
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

class SupplierCommunicator:
    """Gestionnaire pour la communication avec les fournisseurs"""
    
    def __init__(self, config_manager):
        """Initialise le communicateur avec les fournisseurs
        
        Args:
            config_manager: Gestionnaire de configuration
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger("order-manager.supplier_communicator")
    
    async def get_suppliers(self) -> List[Dict]:
        """Récupère la liste des fournisseurs disponibles
        
        Returns:
            List[Dict]: Liste des fournisseurs disponibles
        """
        suppliers = self.config_manager.get_all_suppliers()
        supplier_list = []
        
        for supplier_id, supplier_info in suppliers.items():
            supplier_list.append({
                "id": supplier_id,
                "name": supplier_info.get("name", supplier_id),
                "status": await self._check_supplier_status(supplier_id, supplier_info)
            })
        
        return supplier_list
    
    async def place_order(self, supplier_id: str, order_data: Dict) -> Dict:
        """Place une commande auprès d'un fournisseur
        
        Args:
            supplier_id: Identifiant du fournisseur
            order_data: Données de la commande
            
        Returns:
            Dict: Résultat de la commande
            
        Raises:
            Exception: Si une erreur survient lors de la commande
        """
        try:
            supplier_info = self.config_manager.get_supplier_config(supplier_id)
            if not supplier_info:
                raise Exception(f"Fournisseur {supplier_id} non configuré")
            
            # Formatter les données de la commande selon le format attendu par le fournisseur
            formatted_order = await self._format_order_for_supplier(supplier_id, order_data)
            
            # Dans une implémentation réelle, envoyer une requête à l'API du fournisseur
            # Pour l'instant, simuler une réponse réussie
            self.logger.info(f"Commande placée auprès du fournisseur {supplier_id} pour la commande {order_data.get('id')}")
            
            # Simuler un délai et une réponse
            supplier_order_id = f"SUP-{supplier_id}-{order_data.get('id')}-{datetime.now().strftime('%Y%m%d%H%M')}"
            
            return {
                "success": True,
                "supplier_order_id": supplier_order_id,
                "status": "processing",
                "estimated_shipping": (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                                       .strftime("%Y-%m-%d")),
                "message": "Commande placée avec succès"
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la commande auprès du fournisseur {supplier_id}: {str(e)}")
            raise Exception(f"Erreur lors de la commande auprès du fournisseur: {str(e)}")
    
    async def get_order_status(self, supplier_id: str, supplier_order_id: str) -> Dict:
        """Récupère le statut d'une commande auprès d'un fournisseur
        
        Args:
            supplier_id: Identifiant du fournisseur
            supplier_order_id: Identifiant de la commande chez le fournisseur
            
        Returns:
            Dict: Statut de la commande
            
        Raises:
            Exception: Si une erreur survient lors de la récupération du statut
        """
        try:
            supplier_info = self.config_manager.get_supplier_config(supplier_id)
            if not supplier_info:
                raise Exception(f"Fournisseur {supplier_id} non configuré")
            
            # Dans une implémentation réelle, envoyer une requête à l'API du fournisseur
            # Pour l'instant, simuler une réponse
            self.logger.info(f"Récupération du statut de la commande {supplier_order_id} auprès du fournisseur {supplier_id}")
            
            # Simuler un délai et une réponse
            # Générer un statut aléatoire pour la démonstration
            statuses = ["pending", "processing", "shipped", "delivered"]
            status_texts = {
                "pending": "En attente de traitement",
                "processing": "En cours de traitement",
                "shipped": "Expédié",
                "delivered": "Livré"
            }
            
            # Pour la démonstration, déterminer un statut basé sur l'ID de commande
            status_index = hash(supplier_order_id) % len(statuses)
            status = statuses[status_index]
            
            tracking_info = None
            if status in ["shipped", "delivered"]:
                # Générer un numéro de suivi fictif
                tracking_number = f"TRK{supplier_order_id[-8:]}"
                carrier = "dhl" if "dhl" in supplier_id.lower() else ("usps" if "us" in supplier_id.lower() else "yanwen")
                
                tracking_info = {
                    "tracking_number": tracking_number,
                    "carrier": carrier,
                    "tracking_url": self._get_tracking_url(tracking_number, carrier)
                }
            
            return {
                "supplier_order_id": supplier_order_id,
                "status": status,
                "status_text": status_texts.get(status, status),
                "last_update": datetime.now().isoformat(),
                "tracking_info": tracking_info
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du statut auprès du fournisseur {supplier_id}: {str(e)}")
            raise Exception(f"Erreur lors de la récupération du statut: {str(e)}")
    
    async def cancel_order(self, supplier_id: str, supplier_order_id: str, reason: str = "Customer request") -> Dict:
        """Annule une commande auprès d'un fournisseur
        
        Args:
            supplier_id: Identifiant du fournisseur
            supplier_order_id: Identifiant de la commande chez le fournisseur
            reason: Raison de l'annulation
            
        Returns:
            Dict: Résultat de l'annulation
            
        Raises:
            Exception: Si une erreur survient lors de l'annulation
        """
        try:
            supplier_info = self.config_manager.get_supplier_config(supplier_id)
            if not supplier_info:
                raise Exception(f"Fournisseur {supplier_id} non configuré")
            
            # Dans une implémentation réelle, envoyer une requête à l'API du fournisseur
            # Pour l'instant, simuler une réponse
            self.logger.info(f"Annulation de la commande {supplier_order_id} auprès du fournisseur {supplier_id} (raison: {reason})")
            
            # Simuler un délai et une réponse
            # Vérifier d'abord le statut pour savoir si l'annulation est possible
            current_status = await self.get_order_status(supplier_id, supplier_order_id)
            
            if current_status.get("status") in ["shipped", "delivered"]:
                return {
                    "success": False,
                    "message": f"Impossible d'annuler la commande: elle est déjà {current_status.get('status_text')}"
                }
            
            return {
                "success": True,
                "supplier_order_id": supplier_order_id,
                "status": "cancelled",
                "message": "Commande annulée avec succès"
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'annulation auprès du fournisseur {supplier_id}: {str(e)}")
            raise Exception(f"Erreur lors de l'annulation: {str(e)}")
    
    async def get_product_info(self, supplier_id: str, product_id: str) -> Dict:
        """Récupère les informations sur un produit auprès d'un fournisseur
        
        Args:
            supplier_id: Identifiant du fournisseur
            product_id: Identifiant du produit chez le fournisseur
            
        Returns:
            Dict: Informations sur le produit
            
        Raises:
            Exception: Si une erreur survient lors de la récupération des informations
        """
        try:
            supplier_info = self.config_manager.get_supplier_config(supplier_id)
            if not supplier_info:
                raise Exception(f"Fournisseur {supplier_id} non configuré")
            
            # Dans une implémentation réelle, envoyer une requête à l'API du fournisseur
            # Pour l'instant, simuler une réponse
            self.logger.info(f"Récupération des informations du produit {product_id} auprès du fournisseur {supplier_id}")
            
            # Simuler un délai et une réponse
            return {
                "product_id": product_id,
                "name": f"Produit {product_id}",
                "price": 19.99,
                "stock": 100,
                "shipping_time": "7-15 jours",
                "shipping_cost": 2.99,
                "supplier_id": supplier_id
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des informations du produit {product_id} auprès du fournisseur {supplier_id}: {str(e)}")
            raise Exception(f"Erreur lors de la récupération des informations du produit: {str(e)}")
    
    async def _check_supplier_status(self, supplier_id: str, supplier_info: Dict) -> str:
        """Vérifie le statut d'un fournisseur
        
        Args:
            supplier_id: Identifiant du fournisseur
            supplier_info: Informations sur le fournisseur
            
        Returns:
            str: Statut du fournisseur ('active', 'inactive', 'error')
        """
        # Dans une implémentation réelle, on vérifierait la connexion à l'API du fournisseur
        # Pour l'instant, vérifier simplement si les informations de base sont présentes
        api_url = supplier_info.get("api_url")
        api_key = supplier_info.get("api_key")
        
        if not api_url or not api_key:
            self.logger.warning(f"Fournisseur {supplier_id} incomplet: URL API ou clé API manquante")
            return "inactive"
        
        # Simuler une vérification de l'API (dans une implémentation réelle, faire une requête de test)
        try:
            # Dans une implémentation réelle: requests.get(f"{api_url}/status", headers={"Authorization": f"Bearer {api_key}"}, timeout=5)
            return "active"
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification du statut du fournisseur {supplier_id}: {str(e)}")
            return "error"
    
    async def _format_order_for_supplier(self, supplier_id: str, order_data: Dict) -> Dict:
        """Formate les données de commande pour un fournisseur spécifique
        
        Args:
            supplier_id: Identifiant du fournisseur
            order_data: Données de la commande
            
        Returns:
            Dict: Données de commande formatées
        """
        # Formater différemment selon le fournisseur
        if supplier_id == "aliexpress":
            return self._format_for_aliexpress(order_data)
        elif supplier_id == "cjdropshipping":
            return self._format_for_cjdropshipping(order_data)
        else:
            # Format générique si le fournisseur n'est pas spécifiquement reconnu
            return self._format_generic(order_data)
    
    def _format_for_aliexpress(self, order_data: Dict) -> Dict:
        """Formate les données de commande pour AliExpress
        
        Args:
            order_data: Données de la commande
            
        Returns:
            Dict: Données de commande formatées pour AliExpress
        """
        # Exemple de format spécifique à AliExpress
        shipping_address = order_data.get("shipping_address", {})
        
        return {
            "reference": str(order_data.get("id")),
            "products": [
                {
                    "product_id": item.get("sku") or item.get("product_id"),
                    "quantity": item.get("quantity"),
                    "price": item.get("price"),
                    "properties": item.get("properties", [])
                } for item in order_data.get("line_items", [])
            ],
            "shipping": {
                "country": shipping_address.get("country_code"),
                "province": shipping_address.get("province"),
                "city": shipping_address.get("city"),
                "address1": shipping_address.get("address1"),
                "address2": shipping_address.get("address2"),
                "zipcode": shipping_address.get("zip"),
                "name": f"{shipping_address.get('first_name')} {shipping_address.get('last_name')}",
                "phone": shipping_address.get("phone")
            },
            "webhook_url": "http://example.com/webhooks/aliexpress/update"
        }
    
    def _format_for_cjdropshipping(self, order_data: Dict) -> Dict:
        """Formate les données de commande pour CJ Dropshipping
        
        Args:
            order_data: Données de la commande
            
        Returns:
            Dict: Données de commande formatées pour CJ Dropshipping
        """
        # Exemple de format spécifique à CJ Dropshipping
        shipping_address = order_data.get("shipping_address", {})
        
        return {
            "orderNumber": str(order_data.get("id")),
            "shippingMethod": "CJPacket",  # Valeur par défaut
            "fromCountryCode": "CN",  # Valeur par défaut
            "toCountryCode": shipping_address.get("country_code"),
            "products": [
                {
                    "vid": item.get("sku") or item.get("product_id"),
                    "quantity": item.get("quantity"),
                    "shippingName": f"{shipping_address.get('first_name')} {shipping_address.get('last_name')}"
                } for item in order_data.get("line_items", [])
            ],
            "address": {
                "name": f"{shipping_address.get('first_name')} {shipping_address.get('last_name')}",
                "phone": shipping_address.get("phone"),
                "email": order_data.get("email"),
                "address1": shipping_address.get("address1"),
                "address2": shipping_address.get("address2") or "",
                "city": shipping_address.get("city"),
                "province": shipping_address.get("province"),
                "country": shipping_address.get("country"),
                "zip": shipping_address.get("zip")
            }
        }
    
    def _format_generic(self, order_data: Dict) -> Dict:
        """Formate les données de commande de manière générique
        
        Args:
            order_data: Données de la commande
            
        Returns:
            Dict: Données de commande formatées génériquement
        """
        # Format générique pour les fournisseurs non spécifiquement reconnus
        shipping_address = order_data.get("shipping_address", {})
        
        return {
            "order_id": str(order_data.get("id")),
            "items": [
                {
                    "sku": item.get("sku") or item.get("product_id"),
                    "quantity": item.get("quantity"),
                    "price": item.get("price"),
                } for item in order_data.get("line_items", [])
            ],
            "customer": {
                "name": f"{shipping_address.get('first_name')} {shipping_address.get('last_name')}",
                "email": order_data.get("email"),
                "phone": shipping_address.get("phone")
            },
            "shipping_address": {
                "address1": shipping_address.get("address1"),
                "address2": shipping_address.get("address2"),
                "city": shipping_address.get("city"),
                "province": shipping_address.get("province"),
                "country": shipping_address.get("country"),
                "postal_code": shipping_address.get("zip")
            },
            "shipping_method": "standard",
            "payment_method": order_data.get("payment_gateway_names", ["credit_card"])[0]
        }
    
    def _get_tracking_url(self, tracking_number: str, carrier: str) -> str:
        """Génère une URL de suivi pour un transporteur donné
        
        Args:
            tracking_number: Numéro de suivi
            carrier: Code du transporteur
            
        Returns:
            str: URL de suivi
        """
        tracking_urls = {
            "dhl": "https://www.dhl.com/en/express/tracking.html?AWB={}",
            "fedex": "https://www.fedex.com/fedextrack/?trknbr={}",
            "ups": "https://www.ups.com/track?tracknum={}",
            "usps": "https://tools.usps.com/go/TrackConfirmAction?tLabels={}",
            "post": "https://www.laposte.fr/outils/suivre-vos-envois?code={}",
            "cainiao": "https://global.cainiao.com/detail.htm?mailNoList={}",
            "yanwen": "https://www.trackingmore.com/yanwen-tracking/en.html?number={}",
            "4px": "https://track.4px.com/#/result/0/{}"
        }
        
        carrier_lower = carrier.lower() if carrier else ""
        url_template = tracking_urls.get(carrier_lower, "")
        
        if url_template:
            return url_template.format(tracking_number)
        else:
            # URL générique de tracking si le transporteur n'est pas reconnu
            return f"https://www.trackingmore.com/track/number/{tracking_number}"
