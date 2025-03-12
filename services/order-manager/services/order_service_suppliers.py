#!/usr/bin/env python3
"""
Fonctionnalités de gestion des fournisseurs pour l'agent Order Manager
Fait partie du projet Dropshipping Crew AI

Ce module contient les méthodes de OrderService liées aux interactions avec les fournisseurs.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger

from models import Order, OrderStatus, SupplierOrder, SupplierType

async def _group_products_by_supplier(self, order: Order) -> Dict[str, List[Dict[str, Any]]]:
    """
    Regroupe les produits de la commande par fournisseur.
    
    Args:
        order: Commande à traiter
        
    Returns:
        Dictionnaire avec le type de fournisseur comme clé et la liste des produits comme valeur
    """
    supplier_groups = {}
    
    for item in order.line_items:
        # Récupération des métadonnées du produit pour identifier le fournisseur
        product_id = item.get("product_id")
        variant_id = item.get("variant_id")
        
        if not product_id or not variant_id:
            logger.warning(f"Produit sans identifiant trouvé dans la commande {order.id}")
            continue
        
        # Récupération des métadonnées du produit depuis Shopify
        product_data = await self.shopify_client.get_product_metafields(product_id, variant_id)
        
        # Détermination du fournisseur
        supplier_type = self._determine_supplier_type(product_data)
        
        if not supplier_type:
            logger.warning(f"Impossible de déterminer le fournisseur pour le produit {product_id} de la commande {order.id}")
            continue
        
        # Ajout du produit au groupe du fournisseur
        if supplier_type not in supplier_groups:
            supplier_groups[supplier_type] = []
        
        supplier_groups[supplier_type].append({
            **item,
            "supplier_data": self._extract_supplier_data(product_data, supplier_type)
        })
    
    return supplier_groups

def _determine_supplier_type(self, product_data: Dict[str, Any]) -> Optional[str]:
    """
    Détermine le type de fournisseur à partir des métadonnées du produit.
    
    Args:
        product_data: Métadonnées du produit
        
    Returns:
        Type de fournisseur ou None si indéterminé
    """
    metafields = product_data.get("metafields", {})
    
    # Vérification des différents fournisseurs possibles
    if metafields.get("supplier_aliexpress_id"):
        return SupplierType.ALIEXPRESS
    elif metafields.get("supplier_cj_dropshipping_id"):
        return SupplierType.CJ_DROPSHIPPING
    
    # Par défaut, on utilise AliExpress si aucun fournisseur n'est spécifié explicitement
    # mais que d'autres métadonnées d'AliExpress sont présentes
    if (
        metafields.get("aliexpress_product_id") or 
        metafields.get("aliexpress_variant_id")
    ):
        return SupplierType.ALIEXPRESS
    
    return None

def _extract_supplier_data(self, product_data: Dict[str, Any], supplier_type: str) -> Dict[str, Any]:
    """
    Extrait les données spécifiques au fournisseur à partir des métadonnées du produit.
    
    Args:
        product_data: Métadonnées du produit
        supplier_type: Type de fournisseur
        
    Returns:
        Données spécifiques au fournisseur
    """
    metafields = product_data.get("metafields", {})
    supplier_data = {}
    
    if supplier_type == SupplierType.ALIEXPRESS:
        supplier_data = {
            "product_id": metafields.get("aliexpress_product_id"),
            "variant_id": metafields.get("aliexpress_variant_id"),
            "supplier_id": metafields.get("supplier_aliexpress_id"),
            "shipping_method": metafields.get("aliexpress_shipping_method", "standard"),
            "properties": metafields.get("aliexpress_properties", {})
        }
    elif supplier_type == SupplierType.CJ_DROPSHIPPING:
        supplier_data = {
            "product_id": metafields.get("cj_dropshipping_product_id"),
            "variant_id": metafields.get("cj_dropshipping_variant_id"),
            "supplier_id": metafields.get("supplier_cj_dropshipping_id"),
            "shipping_method": metafields.get("cj_dropshipping_shipping_method", "standard"),
            "warehouse": metafields.get("cj_dropshipping_warehouse", "CN")
        }
    
    return supplier_data

async def _create_supplier_order(self, original_order: Order, supplier_type: str, line_items: List[Dict[str, Any]]) -> SupplierOrder:
    """
    Crée une commande fournisseur à partir de la commande originale et des produits.
    
    Args:
        original_order: Commande originale
        supplier_type: Type de fournisseur
        line_items: Liste des produits pour ce fournisseur
        
    Returns:
        Commande fournisseur créée
    """
    # Génération d'un identifiant unique pour la commande fournisseur
    supplier_order_id = str(uuid.uuid4())
    
    # Création de la commande fournisseur
    supplier_order = SupplierOrder(
        id=supplier_order_id,
        original_order_id=original_order.id,
        supplier_type=supplier_type,
        supplier_order_id=None,  # Sera attribué par le fournisseur après l'envoi
        status="pending",
        line_items=line_items,
        shipping_address=original_order.shipping_address,
        tracking_info=None,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        errors=[]
    )
    
    return supplier_order

async def _send_order_to_supplier(self, supplier_order: SupplierOrder) -> bool:
    """
    Envoie une commande au fournisseur.
    
    Args:
        supplier_order: Commande fournisseur à envoyer
        
    Returns:
        Succès de l'envoi
    """
    try:
        # Envoi de la commande au fournisseur via le communicateur
        result = await self.supplier_communicator.place_order(supplier_order)
        
        if not result.success:
            logger.error(f"Erreur lors de l'envoi de la commande {supplier_order.id} au fournisseur {supplier_order.supplier_type}: {result.error_message}")
            
            # Mise à jour du statut et enregistrement de l'erreur
            supplier_order.status = "error"
            supplier_order.errors.append({
                "timestamp": datetime.now().isoformat(),
                "message": result.error_message
            })
            await self.repository.update_supplier_order(supplier_order)
            return False
        
        # Mise à jour avec l'identifiant fournisseur
        supplier_order.supplier_order_id = result.supplier_order_id
        supplier_order.status = "processing"
        await self.repository.update_supplier_order(supplier_order)
        
        logger.info(f"Commande {supplier_order.id} envoyée avec succès au fournisseur {supplier_order.supplier_type} (ID: {supplier_order.supplier_order_id})")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de la commande {supplier_order.id} au fournisseur: {str(e)}")
        
        # Mise à jour du statut et enregistrement de l'erreur
        supplier_order.status = "error"
        supplier_order.errors.append({
            "timestamp": datetime.now().isoformat(),
            "message": str(e)
        })
        await self.repository.update_supplier_order(supplier_order)
        return False

async def _check_supplier_order_updates(self):
    """
    Vérifie les mises à jour des commandes fournisseurs.
    """
    # Récupération des commandes en cours de traitement
    processing_orders = await self.repository.get_supplier_orders_by_status("processing")
    
    if not processing_orders:
        logger.info("Aucune commande fournisseur en cours de traitement")
        return
    
    logger.info(f"{len(processing_orders)} commandes fournisseurs en cours de traitement")
    
    # Vérification de chaque commande
    for supplier_order in processing_orders:
        try:
            # Mise à jour du statut de la commande
            updated = await self._update_supplier_order_status(supplier_order)
            
            if updated:
                logger.info(f"Statut de la commande fournisseur {supplier_order.id} mis à jour avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut de la commande fournisseur {supplier_order.id}: {str(e)}")

async def _update_supplier_order_status(self, supplier_order: SupplierOrder) -> bool:
    """
    Met à jour le statut d'une commande fournisseur.
    
    Args:
        supplier_order: Commande fournisseur à mettre à jour
        
    Returns:
        Vrai si le statut a été mis à jour, faux sinon
    """
    if not supplier_order.supplier_order_id:
        logger.warning(f"Commande fournisseur {supplier_order.id} sans identifiant fournisseur")
        return False
    
    # Récupération du statut depuis le fournisseur
    status_result = await self.supplier_communicator.check_order_status(
        supplier_order.supplier_type,
        supplier_order.supplier_order_id
    )
    
    if not status_result.success:
        logger.error(f"Erreur lors de la vérification du statut de la commande {supplier_order.id}: {status_result.error_message}")
        return False
    
    # Vérification si le statut a changé
    if status_result.status == supplier_order.status:
        return False
    
    # Mise à jour du statut
    old_status = supplier_order.status
    supplier_order.status = status_result.status
    supplier_order.updated_at = datetime.now().isoformat()
    
    # Si la commande est expédiée, enregistrement des informations de suivi
    if status_result.status == "shipped" and status_result.tracking_info:
        supplier_order.tracking_info = status_result.tracking_info
    
    # Enregistrement de la mise à jour
    success = await self.repository.update_supplier_order(supplier_order)
    
    if not success:
        logger.error(f"Erreur lors de l'enregistrement de la mise à jour de la commande fournisseur {supplier_order.id}")
        return False
    
    # Mise à jour de la commande principale si toutes les commandes fournisseurs sont expédiées ou livrées
    if status_result.status in ["shipped", "delivered"]:
        await self._update_original_order_status(supplier_order.original_order_id)
    
    logger.info(f"Statut de la commande fournisseur {supplier_order.id} mis à jour de {old_status} à {supplier_order.status}")
    return True
