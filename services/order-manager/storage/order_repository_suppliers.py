#!/usr/bin/env python3
"""
Méthodes de repository pour la gestion des commandes fournisseurs
Fait partie du projet Dropshipping Crew AI

Ce module contient les méthodes du repository OrderRepository pour la gestion
des commandes fournisseurs.
"""

import sqlite3
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from models import SupplierOrder, SupplierType

async def add_supplier_order(self, supplier_order: SupplierOrder) -> bool:
    """
    Ajoute une commande fournisseur à la base de données.
    
    Args:
        supplier_order: Commande fournisseur à ajouter
        
    Returns:
        Succès de l'opération
    """
    await self._ensure_initialized()
    
    # Conversion en dict pour stockage
    supplier_order_dict = self.converter._supplier_order_to_dict(supplier_order)
    
    # Exécution dans un thread séparé
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(None, self._insert_supplier_order, supplier_order_dict)
    
    return success

def _insert_supplier_order(self, supplier_order_dict: Dict[str, Any]) -> bool:
    """Insère une commande fournisseur dans la base de données (fonction synchrone)."""
    try:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Conversion des champs complexes en JSON
        supplier_order_dict["line_items"] = json.dumps(supplier_order_dict["line_items"])
        if supplier_order_dict.get("tracking_info"):
            supplier_order_dict["tracking_info"] = json.dumps(supplier_order_dict["tracking_info"])
        if supplier_order_dict.get("errors"):
            supplier_order_dict["errors"] = json.dumps(supplier_order_dict["errors"])
        
        # Préparation de la requête
        columns = ", ".join(supplier_order_dict.keys())
        placeholders = ", ".join(["?" for _ in supplier_order_dict])
        values = list(supplier_order_dict.values())
        
        cursor.execute(f"INSERT INTO supplier_orders ({columns}) VALUES ({placeholders})", values)
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'insertion de la commande fournisseur: {str(e)}")
        return False

async def update_supplier_order(self, supplier_order: SupplierOrder) -> bool:
    """
    Met à jour une commande fournisseur existante.
    
    Args:
        supplier_order: Commande fournisseur à mettre à jour
        
    Returns:
        Succès de l'opération
    """
    await self._ensure_initialized()
    
    # Vérification que la commande fournisseur existe
    existing = await self.get_supplier_order(supplier_order.id)
    if not existing:
        logger.error(f"Tentative de mise à jour d'une commande fournisseur inexistante: {supplier_order.id}")
        return False
    
    # Conversion en dict pour stockage
    supplier_order_dict = self.converter._supplier_order_to_dict(supplier_order)
    
    # Mise à jour de la date de dernière modification
    supplier_order_dict["updated_at"] = datetime.now().isoformat()
    
    # Exécution dans un thread séparé
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(None, self._update_supplier_order, supplier_order_dict)
    
    return success

def _update_supplier_order(self, supplier_order_dict: Dict[str, Any]) -> bool:
    """Met à jour une commande fournisseur dans la base de données (fonction synchrone)."""
    try:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Conversion des champs complexes en JSON
        supplier_order_dict["line_items"] = json.dumps(supplier_order_dict["line_items"])
        if supplier_order_dict.get("tracking_info"):
            supplier_order_dict["tracking_info"] = json.dumps(supplier_order_dict["tracking_info"])
        if supplier_order_dict.get("errors"):
            supplier_order_dict["errors"] = json.dumps(supplier_order_dict["errors"])
        
        # Préparation de la requête
        supplier_order_id = supplier_order_dict.pop("id")
        set_clause = ", ".join([f"{key} = ?" for key in supplier_order_dict.keys()])
        values = list(supplier_order_dict.values()) + [supplier_order_id]
        
        cursor.execute(f"UPDATE supplier_orders SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la commande fournisseur: {str(e)}")
        return False

async def get_supplier_order(self, supplier_order_id: str) -> Optional[SupplierOrder]:
    """
    Récupère une commande fournisseur par son identifiant.
    
    Args:
        supplier_order_id: Identifiant de la commande fournisseur
        
    Returns:
        Commande fournisseur ou None si non trouvée
    """
    await self._ensure_initialized()
    
    # Exécution dans un thread séparé
    loop = asyncio.get_event_loop()
    supplier_order_dict = await loop.run_in_executor(None, self._get_supplier_order, supplier_order_id)
    
    if not supplier_order_dict:
        return None
    
    # Conversion du dict en objet SupplierOrder
    return self.converter._dict_to_supplier_order(supplier_order_dict)

def _get_supplier_order(self, supplier_order_id: str) -> Optional[Dict[str, Any]]:
    """Récupère une commande fournisseur par son identifiant (fonction synchrone)."""
    try:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM supplier_orders WHERE id = ?", (supplier_order_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Conversion en dictionnaire
        supplier_order_dict = dict(row)
        
        # Conversion des champs JSON
        supplier_order_dict["line_items"] = json.loads(supplier_order_dict["line_items"])
        if supplier_order_dict.get("tracking_info"):
            supplier_order_dict["tracking_info"] = json.loads(supplier_order_dict["tracking_info"])
        if supplier_order_dict.get("errors"):
            supplier_order_dict["errors"] = json.loads(supplier_order_dict["errors"])
        
        return supplier_order_dict
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la commande fournisseur {supplier_order_id}: {str(e)}")
        return None

async def get_supplier_orders_for_order(self, order_id: str) -> List[SupplierOrder]:
    """
    Récupère toutes les commandes fournisseurs d'une commande.
    
    Args:
        order_id: Identifiant de la commande principale
        
    Returns:
        Liste des commandes fournisseurs de la commande
    """
    await self._ensure_initialized()
    
    # Exécution dans un thread séparé
    loop = asyncio.get_event_loop()
    supplier_orders_dict = await loop.run_in_executor(None, self._get_supplier_orders_for_order, order_id)
    
    # Conversion des dicts en objets SupplierOrder
    return [self.converter._dict_to_supplier_order(supplier_order_dict) for supplier_order_dict in supplier_orders_dict]

def _get_supplier_orders_for_order(self, order_id: str) -> List[Dict[str, Any]]:
    """Récupère toutes les commandes fournisseurs d'une commande (fonction synchrone)."""
    try:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM supplier_orders WHERE original_order_id = ?", (order_id,))
        rows = cursor.fetchall()
        conn.close()
        
        # Conversion en liste de dictionnaires
        supplier_orders_dict = []
        for row in rows:
            supplier_order_dict = dict(row)
            
            # Conversion des champs JSON
            supplier_order_dict["line_items"] = json.loads(supplier_order_dict["line_items"])
            if supplier_order_dict.get("tracking_info"):
                supplier_order_dict["tracking_info"] = json.loads(supplier_order_dict["tracking_info"])
            if supplier_order_dict.get("errors"):
                supplier_order_dict["errors"] = json.loads(supplier_order_dict["errors"])
            
            supplier_orders_dict.append(supplier_order_dict)
        
        return supplier_orders_dict
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des commandes fournisseurs pour la commande {order_id}: {str(e)}")
        return []

async def get_supplier_order_by_supplier_id(self, supplier_type: str, supplier_order_id: str) -> Optional[SupplierOrder]:
    """
    Récupère une commande fournisseur par son identifiant chez le fournisseur.
    
    Args:
        supplier_type: Type de fournisseur
        supplier_order_id: Identifiant de la commande chez le fournisseur
        
    Returns:
        Commande fournisseur ou None si non trouvée
    """
    await self._ensure_initialized()
    
    # Exécution dans un thread séparé
    loop = asyncio.get_event_loop()
    supplier_order_dict = await loop.run_in_executor(
        None, self._get_supplier_order_by_supplier_id, supplier_type, supplier_order_id)
    
    if not supplier_order_dict:
        return None
    
    # Conversion du dict en objet SupplierOrder
    return self.converter._dict_to_supplier_order(supplier_order_dict)

def _get_supplier_order_by_supplier_id(self, supplier_type: str, supplier_order_id: str) -> Optional[Dict[str, Any]]:
    """Récupère une commande fournisseur par son identifiant chez le fournisseur (fonction synchrone)."""
    try:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM supplier_orders WHERE supplier_type = ? AND supplier_order_id = ?", 
            (supplier_type, supplier_order_id)
        )
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Conversion en dictionnaire
        supplier_order_dict = dict(row)
        
        # Conversion des champs JSON
        supplier_order_dict["line_items"] = json.loads(supplier_order_dict["line_items"])
        if supplier_order_dict.get("tracking_info"):
            supplier_order_dict["tracking_info"] = json.loads(supplier_order_dict["tracking_info"])
        if supplier_order_dict.get("errors"):
            supplier_order_dict["errors"] = json.loads(supplier_order_dict["errors"])
        
        return supplier_order_dict
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la commande fournisseur {supplier_order_id} du fournisseur {supplier_type}: {str(e)}")
        return None

async def get_pending_supplier_orders(self) -> List[SupplierOrder]:
    """
    Récupère toutes les commandes fournisseurs en attente.
    
    Returns:
        Liste des commandes fournisseurs en attente
    """
    await self._ensure_initialized()
    
    # Exécution dans un thread séparé
    loop = asyncio.get_event_loop()
    supplier_orders_dict = await loop.run_in_executor(None, self._get_pending_supplier_orders)
    
    # Conversion des dicts en objets SupplierOrder
    return [self.converter._dict_to_supplier_order(supplier_order_dict) for supplier_order_dict in supplier_orders_dict]

def _get_pending_supplier_orders(self) -> List[Dict[str, Any]]:
    """Récupère toutes les commandes fournisseurs en attente (fonction synchrone)."""
    try:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM supplier_orders WHERE status = 'pending'")
        rows = cursor.fetchall()
        conn.close()
        
        # Conversion en liste de dictionnaires
        supplier_orders_dict = []
        for row in rows:
            supplier_order_dict = dict(row)
            
            # Conversion des champs JSON
            supplier_order_dict["line_items"] = json.loads(supplier_order_dict["line_items"])
            if supplier_order_dict.get("tracking_info"):
                supplier_order_dict["tracking_info"] = json.loads(supplier_order_dict["tracking_info"])
            if supplier_order_dict.get("errors"):
                supplier_order_dict["errors"] = json.loads(supplier_order_dict["errors"])
            
            supplier_orders_dict.append(supplier_order_dict)
        
        return supplier_orders_dict
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des commandes fournisseurs en attente: {str(e)}")
        return []

async def get_supplier_orders_by_status(self, status: str) -> List[SupplierOrder]:
    """
    Récupère toutes les commandes fournisseurs par statut.
    
    Args:
        status: Statut des commandes à récupérer
        
    Returns:
        Liste des commandes fournisseurs ayant le statut spécifié
    """
    await self._ensure_initialized()
    
    # Exécution dans un thread séparé
    loop = asyncio.get_event_loop()
    supplier_orders_dict = await loop.run_in_executor(None, self._get_supplier_orders_by_status, status)
    
    # Conversion des dicts en objets SupplierOrder
    return [self.converter._dict_to_supplier_order(supplier_order_dict) for supplier_order_dict in supplier_orders_dict]

def _get_supplier_orders_by_status(self, status: str) -> List[Dict[str, Any]]:
    """Récupère toutes les commandes fournisseurs par statut (fonction synchrone)."""
    try:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM supplier_orders WHERE status = ?", (status,))
        rows = cursor.fetchall()
        conn.close()
        
        # Conversion en liste de dictionnaires
        supplier_orders_dict = []
        for row in rows:
            supplier_order_dict = dict(row)
            
            # Conversion des champs JSON
            supplier_order_dict["line_items"] = json.loads(supplier_order_dict["line_items"])
            if supplier_order_dict.get("tracking_info"):
                supplier_order_dict["tracking_info"] = json.loads(supplier_order_dict["tracking_info"])
            if supplier_order_dict.get("errors"):
                supplier_order_dict["errors"] = json.loads(supplier_order_dict["errors"])
            
            supplier_orders_dict.append(supplier_order_dict)
        
        return supplier_orders_dict
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des commandes fournisseurs avec le statut {status}: {str(e)}")
        return []
