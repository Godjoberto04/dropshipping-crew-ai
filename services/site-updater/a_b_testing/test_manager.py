#!/usr/bin/env python3
"""
Module pour la gestion des tests A/B sur le site e-commerce.
"""

import asyncio
import json
import time
import uuid
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta

from config import settings, get_logger

logger = get_logger("ab_test_manager")

class ABTestManager:
    """
    Classe pour créer et gérer des tests A/B sur le site e-commerce.
    Permet d'optimiser la présentation, les prix, et d'autres éléments
    en testant différentes variantes auprès des utilisateurs.
    """
    
    def __init__(self):
        """Initialise le gestionnaire de tests A/B."""
        self.active_tests = {}  # Stocke les tests actifs
        logger.info("Gestionnaire de tests A/B initialisé")
    
    async def _get_test_data(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les données d'un test existant.
        
        Args:
            test_id: Identifiant du test
            
        Returns:
            Données du test ou None si non trouvé
        """
        # Dans une implémentation réelle, ces données seraient stockées dans une base de données
        return self.active_tests.get(test_id)
    
    async def _save_test_data(self, test_data: Dict[str, Any]) -> bool:
        """
        Sauvegarde les données d'un test.
        
        Args:
            test_data: Données du test à sauvegarder
            
        Returns:
            True si réussi, False sinon
        """
        # Dans une implémentation réelle, sauvegarde dans une base de données
        try:
            test_id = test_data.get("test_id")
            if not test_id:
                return False
                
            self.active_tests[test_id] = test_data
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données de test: {str(e)}")
            return False
    
    async def _update_metrics(self, test_id: str, variant_id: str, metrics: Dict[str, Any]) -> bool:
        """
        Met à jour les métriques pour une variante d'un test.
        
        Args:
            test_id: Identifiant du test
            variant_id: Identifiant de la variante
            metrics: Métriques à mettre à jour
            
        Returns:
            True si réussi, False sinon
        """
        test_data = await self._get_test_data(test_id)
        if not test_data:
            logger.warning(f"Tentative de mise à jour des métriques pour un test inexistant: {test_id}")
            return False
        
        # Rechercher la variante
        found = False
        for variant in test_data.get("variants", []):
            if variant.get("id") == variant_id:
                # Mettre à jour les métriques de la variante
                variant_metrics = variant.get("metrics", {})
                for key, value in metrics.items():
                    # Incrémenter les compteurs
                    if key in ["views", "clicks", "conversions", "cart_adds"]:
                        variant_metrics[key] = variant_metrics.get(key, 0) + value
                    # Remplacer les valeurs normales
                    else:
                        variant_metrics[key] = value
                
                # Calculer les métriques dérivées
                if "views" in variant_metrics and variant_metrics["views"] > 0:
                    if "clicks" in variant_metrics:
                        variant_metrics["click_rate"] = variant_metrics["clicks"] / variant_metrics["views"] * 100
                    
                    if "conversions" in variant_metrics:
                        variant_metrics["conversion_rate"] = variant_metrics["conversions"] / variant_metrics["views"] * 100
                
                variant["metrics"] = variant_metrics
                found = True
                break
        
        if not found:
            logger.warning(f"Variante {variant_id} non trouvée dans le test {test_id}")
            return False
        
        # Sauvegarder les modifications
        return await self._save_test_data(test_data)
    
    async def create_test(self, test_name: str, test_type: str, variants: List[Dict[str, Any]], 
                         duration: int = None, target_metric: str = "conversion_rate") -> Dict[str, Any]:
        """
        Crée un nouveau test A/B.
        
        Args:
            test_name: Nom du test
            test_type: Type de test (layout, price, content, etc.)
            variants: Liste des variantes à tester
            duration: Durée du test en secondes
            target_metric: Métrique principale à optimiser
            
        Returns:
            Informations sur le test créé
        """
        if not variants or len(variants) < 2:
            raise ValueError("Au moins deux variantes sont requises pour un test A/B")
        
        # Durée par défaut
        if duration is None:
            duration = settings.A_B_TEST_MIN_DURATION
        
        # S'assurer que la durée est suffisante
        if duration < settings.A_B_TEST_MIN_DURATION:
            logger.warning(f"Durée de test trop courte, ajustée à {settings.A_B_TEST_MIN_DURATION} secondes")
            duration = settings.A_B_TEST_MIN_DURATION
        
        # Créer un ID unique pour le test
        test_id = str(uuid.uuid4())
        start_time = time.time()
        end_time = start_time + duration
        
        # Préparer les variantes avec des IDs
        prepared_variants = []
        for i, variant in enumerate(variants):
            variant_id = variant.get("id", f"variant_{i+1}")
            prepared_variants.append({
                "id": variant_id,
                "name": variant.get("name", f"Variante {chr(65+i)}"),  # A, B, C, etc.
                "content": variant.get("content", {}),
                "traffic_allocation": 1.0 / len(variants),  # Répartition égale du trafic
                "metrics": {
                    "views": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "cart_adds": 0
                }
            })
        
        # Créer l'objet test
        test_data = {
            "test_id": test_id,
            "name": test_name,
            "type": test_type,
            "status": "active",
            "start_time": start_time,
            "end_time": end_time,
            "target_metric": target_metric,
            "variants": prepared_variants,
            "winner": None,
            "confidence": None,
            "created_at": time.time()
        }
        
        # Sauvegarder le test
        success = await self._save_test_data(test_data)
        if not success:
            raise RuntimeError("Échec lors de la création du test A/B")
        
        logger.info(f"Test A/B '{test_name}' créé avec succès (ID: {test_id})")
        
        # Configurer le test dans Shopify (simulation)
        await asyncio.sleep(0.5)  # Simulation
        
        return {
            "test_id": test_id,
            "name": test_name,
            "status": "active",
            "start_time": start_time,
            "end_time": end_time,
            "variants": [{
                "id": v["id"],
                "name": v["name"],
                "traffic_allocation": v["traffic_allocation"]
            } for v in prepared_variants]
        }
    
    async def monitor_test(self, test_id: str) -> Dict[str, Any]:
        """
        Surveille un test A/B existant, analyse les résultats et détermine s'il y a un gagnant.
        
        Args:
            test_id: Identifiant du test
            
        Returns:
            Informations sur l'état du test
        """
        test_data = await self._get_test_data(test_id)
        if not test_data:
            raise ValueError(f"Test non trouvé: {test_id}")
        
        # Vérifier si le test est toujours actif
        current_time = time.time()
        end_time = test_data.get("end_time", 0)
        status = test_data.get("status", "unknown")
        
        # Mettre à jour le statut si nécessaire
        if status == "active" and current_time > end_time:
            test_data["status"] = "completed"
            status = "completed"
            await self._save_test_data(test_data)
        
        # Récupérer les métriques actuelles (simulation)
        # Dans une implémentation réelle, ces données proviendraient de l'API Shopify/Google Analytics
        updated_metrics = await self._simulate_test_metrics(test_data)
        
        # Calculer les statistiques
        target_metric = test_data.get("target_metric", "conversion_rate")
        variants = test_data.get("variants", [])
        
        # Trouver la meilleure variante
        best_variant = None
        best_value = -1
        
        for variant in variants:
            metrics = variant.get("metrics", {})
            value = metrics.get(target_metric, 0)
            
            if value > best_value:
                best_value = value
                best_variant = variant
        
        # Calculer la confiance statistique (simulation simplifiée)
        # Dans une implémentation réelle, il faudrait utiliser des tests statistiques appropriés
        confidence = await self._calculate_confidence(variants, target_metric)
        
        # Déterminer s'il y a un gagnant clair
        winner = None
        if confidence >= 0.95 and best_variant:
            winner = best_variant.get("id")
            
            # Mettre à jour le test avec le gagnant si le test est terminé
            if status == "completed" and test_data.get("winner") is None:
                test_data["winner"] = winner
                test_data["confidence"] = confidence
                await self._save_test_data(test_data)
        
        # Préparer le résultat
        result = {
            "test_id": test_id,
            "name": test_data.get("name", ""),
            "status": status,
            "progress": min(100, int((current_time - test_data.get("start_time", 0)) / 
                              (end_time - test_data.get("start_time", 1)) * 100)),
            "time_remaining": max(0, end_time - current_time),
            "target_metric": target_metric,
            "variants": [
                {
                    "id": v.get("id"),
                    "name": v.get("name"),
                    "metrics": v.get("metrics", {})
                }
                for v in variants
            ],
            "best_variant": best_variant.get("id") if best_variant else None,
            "confidence": confidence,
            "winner": winner,
            "timestamp": current_time
        }
        
        return result
    
    async def _simulate_test_metrics(self, test_data: Dict[str, Any]) -> bool:
        """
        Simule l'acquisition de métriques pour un test.
        Dans une implémentation réelle, ces données proviendraient de Shopify/Google Analytics.
        
        Args:
            test_data: Données du test
            
        Returns:
            True si les métriques ont été mises à jour, False sinon
        """
        import random
        
        test_id = test_data.get("test_id")
        variants = test_data.get("variants", [])
        
        # Pour chaque variante, simuler des métriques
        for variant in variants:
            variant_id = variant.get("id")
            
            # Simuler des incréments de métriques
            metrics_update = {
                "views": random.randint(10, 50),
                "clicks": random.randint(1, 15),
                "conversions": random.randint(0, 3),
                "cart_adds": random.randint(1, 10),
                "revenue": random.uniform(50, 200)
            }
            
            # Ajouter une légère différence entre les variantes pour simulation
            if variant_id == variants[0].get("id"):
                # Variante A (légèrement meilleure)
                metrics_update["clicks"] += random.randint(1, 5)
                metrics_update["conversions"] += random.randint(0, 2)
            
            # Mettre à jour les métriques
            await self._update_metrics(test_id, variant_id, metrics_update)
        
        return True
    
    async def _calculate_confidence(self, variants: List[Dict[str, Any]], metric: str) -> float:
        """
        Calcule la confiance statistique pour déterminer s'il y a un gagnant.
        Simulation simplifiée - dans la réalité, utiliserait des tests statistiques appropriés.
        
        Args:
            variants: Liste des variantes avec leurs métriques
            metric: Métrique cible à comparer
            
        Returns:
            Niveau de confiance (0-1)
        """
        if len(variants) < 2:
            return 0.0
        
        # Trouver les deux meilleures variantes
        sorted_variants = sorted(variants, 
                                 key=lambda v: v.get("metrics", {}).get(metric, 0),
                                 reverse=True)
        
        best = sorted_variants[0]
        second_best = sorted_variants[1]
        
        best_value = best.get("metrics", {}).get(metric, 0)
        second_value = second_best.get("metrics", {}).get(metric, 0)
        
        # Pas de différence
        if best_value == 0 or second_value == 0:
            return 0.0
        
        # Calculer le pourcentage de différence
        diff_percent = (best_value - second_value) / second_value
        
        # Simuler la confiance en fonction de la différence et du volume
        views_best = best.get("metrics", {}).get("views", 0)
        
        # Plus de vues = plus de confiance
        volume_factor = min(1.0, views_best / 1000)  # Max à 1000 vues
        
        # Plus de différence = plus de confiance
        diff_factor = min(1.0, diff_percent * 10)  # 10% diff = pleine confiance
        
        # Combinaison des facteurs
        confidence = min(0.99, volume_factor * 0.5 + diff_factor * 0.5)
        
        return confidence
    
    async def stop_test(self, test_id: str, declare_winner: bool = True) -> Dict[str, Any]:
        """
        Arrête un test A/B en cours et déclare éventuellement un gagnant.
        
        Args:
            test_id: Identifiant du test
            declare_winner: Si True, déclare un gagnant si possible
            
        Returns:
            Résultat de l'arrêt du test
        """
        test_data = await self._get_test_data(test_id)
        if not test_data:
            raise ValueError(f"Test non trouvé: {test_id}")
        
        # Vérifier si le test est déjà terminé
        status = test_data.get("status", "unknown")
        if status != "active":
            return {
                "test_id": test_id,
                "status": status,
                "message": "Le test n'est pas actif et ne peut pas être arrêté"
            }
        
        # Arrêter le test
        test_data["status"] = "stopped"
        test_data["end_time"] = time.time()
        
        # Déterminer un gagnant si demandé
        winner = None
        confidence = 0.0
        
        if declare_winner:
            # Obtenir les dernières métriques
            await self._simulate_test_metrics(test_data)
            
            # Trouver la meilleure variante
            target_metric = test_data.get("target_metric", "conversion_rate")
            variants = test_data.get("variants", [])
            
            best_variant = None
            best_value = -1
            
            for variant in variants:
                metrics = variant.get("metrics", {})
                value = metrics.get(target_metric, 0)
                
                if value > best_value:
                    best_value = value
                    best_variant = variant
            
            if best_variant:
                winner = best_variant.get("id")
                # Calculer la confiance (simplifié car test arrêté prématurément)
                confidence = await self._calculate_confidence(variants, target_metric)
                
                # Enregistrer le gagnant
                test_data["winner"] = winner
                test_data["confidence"] = confidence
        
        # Sauvegarder les changements
        await self._save_test_data(test_data)
        
        # Désactiver le test dans Shopify (simulation)
        await asyncio.sleep(0.3)  # Simulation
        
        return {
            "test_id": test_id,
            "status": "stopped",
            "winner": winner,
            "confidence": confidence,
            "message": "Le test a été arrêté avec succès"
        }
    
    async def apply_test_winner(self, test_id: str, variant_id: str = None) -> Dict[str, Any]:
        """
        Applique la variante gagnante (ou spécifiée) comme configuration permanente.
        
        Args:
            test_id: Identifiant du test
            variant_id: Identifiant de la variante à appliquer (si None, utilise le gagnant déclaré)
            
        Returns:
            Résultat de l'application
        """
        test_data = await self._get_test_data(test_id)
        if not test_data:
            raise ValueError(f"Test non trouvé: {test_id}")
        
        # Déterminer la variante à appliquer
        winner_id = variant_id or test_data.get("winner")
        if not winner_id:
            raise ValueError(f"Aucun gagnant défini pour le test {test_id} et aucune variante spécifiée")
        
        # Trouver la variante gagnante
        winner_variant = None
        for variant in test_data.get("variants", []):
            if variant.get("id") == winner_id:
                winner_variant = variant
                break
        
        if not winner_variant:
            raise ValueError(f"Variante {winner_id} non trouvée dans le test {test_id}")
        
        # Appliquer la variante gagnante (simulation)
        # Dans une implémentation réelle, mettrait à jour la configuration Shopify
        await asyncio.sleep(0.5)  # Simulation
        
        # Marquer le test comme appliqué
        test_data["status"] = "applied"
        test_data["applied_variant"] = winner_id
        test_data["applied_at"] = time.time()
        
        await self._save_test_data(test_data)
        
        return {
            "test_id": test_id,
            "status": "applied",
            "applied_variant": winner_id,
            "message": f"La variante {winner_id} a été appliquée avec succès"
        }
