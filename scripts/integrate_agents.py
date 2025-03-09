#!/usr/bin/env python3
"""
Script d'intégration entre l'agent Data Analyzer et l'agent Website Builder.
Ce script récupère les résultats d'analyse de produits et ajoute automatiquement
les produits recommandés à la boutique Shopify.

Usage:
    python3 integrate_agents.py --threshold 7.5 --limit 5
"""

import argparse
import json
import sys
import time
import requests
from datetime import datetime

# Configuration par défaut
DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_THRESHOLD = 7.5  # Score minimum pour ajouter un produit
DEFAULT_LIMIT = 10  # Nombre maximum de produits à ajouter

def parse_arguments():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(description="Intégration entre Data Analyzer et Website Builder")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="URL de l'API (par défaut: http://localhost:8000)")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD, help="Score minimum pour ajouter un produit (par défaut: 7.5)")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Nombre maximum de produits à ajouter (par défaut: 10)")
    return parser.parse_args()

def get_latest_analysis(api_url):
    """Récupère les derniers résultats d'analyse"""
    try:
        response = requests.get(f"{api_url}/analysis/results/latest")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des résultats d'analyse: {e}")
        sys.exit(1)

def filter_recommended_products(analysis_results, threshold, limit):
    """Filtre les produits recommandés selon le score et la limite"""
    if "top_products" not in analysis_results:
        print("Aucun produit trouvé dans les résultats d'analyse")
        return []
    
    # Filtrer les produits avec un score supérieur au seuil
    recommended_products = [
        product for product in analysis_results.get("top_products", [])
        if product.get("recommendation_score", 0) >= threshold
    ]
    
    # Trier par score de recommandation (du plus élevé au plus bas)
    recommended_products.sort(key=lambda p: p.get("recommendation_score", 0), reverse=True)
    
    # Limiter le nombre de produits
    return recommended_products[:limit]

def transform_to_shopify_product(product):
    """Transforme un produit analysé en format Shopify"""
    shopify_product = {
        "title": product["name"],
        "description": product.get("justification", ""),
        "vendor": "Dropshipping Autonome",
        "product_type": "Accessoire",  # À adapter en fonction du segment de marché
        "tags": ["automatisé", "recommandé", f"score_{int(product.get('recommendation_score', 0))}"],
        "variants": [
            {
                "price": str(product["recommended_price"]),
                "compare_at_price": str(round(product["recommended_price"] * 1.2, 2)),  # +20%
                "inventory_quantity": 100
            }
        ],
        "images": []
    }
    
    # Ajouter l'image si disponible
    if product.get("image_url"):
        shopify_product["images"].append({
            "src": product["image_url"],
            "alt": product["name"]
        })
    
    return shopify_product

def add_product_to_shopify(api_url, product_data):
    """Ajoute un produit via l'agent Website Builder"""
    try:
        response = requests.post(
            f"{api_url}/agents/website-builder/action",
            json={
                "action": "add_product",
                "product_data": product_data
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'ajout du produit: {e}")
        return None

def wait_for_task_completion(api_url, task_id, max_attempts=12, wait_time=5):
    """Attend la fin d'une tâche"""
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{api_url}/tasks/{task_id}")
            response.raise_for_status()
            task_status = response.json()
            
            status = task_status.get("status")
            if status in ["completed", "failed"]:
                return status
            
            print(f"Tâche en cours... {task_status.get('progress', 0)}% complété. Attente de {wait_time} secondes.")
            time.sleep(wait_time)
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la vérification du statut de la tâche: {e}")
            time.sleep(wait_time)
    
    return "timeout"

def main():
    args = parse_arguments()
    
    print(f"===== Intégration Data Analyzer → Website Builder =====")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {args.api_url}")
    print(f"Seuil de score: {args.threshold}")
    print(f"Limite de produits: {args.limit}")
    print("\n")
    
    # Récupérer les résultats d'analyse
    print("1. Récupération des résultats d'analyse...")
    analysis_results = get_latest_analysis(args.api_url)
    print(f"   - Analyse récupérée: {analysis_results.get('analysis_metadata', {}).get('timestamp', 'N/A')}")
    
    # Filtrer les produits recommandés
    print("\n2. Filtrage des produits recommandés...")
    recommended_products = filter_recommended_products(analysis_results, args.threshold, args.limit)
    print(f"   - {len(recommended_products)} produits filtrés avec un score >= {args.threshold}")
    
    if not recommended_products:
        print("Aucun produit recommandé à ajouter. Fin du processus.")
        return
    
    # Transformer et ajouter les produits
    print("\n3. Ajout des produits à la boutique Shopify...")
    successful_additions = 0
    
    for i, product in enumerate(recommended_products, 1):
        print(f"\n   - Produit {i}/{len(recommended_products)}: {product['name']} (Score: {product.get('recommendation_score', 'N/A')})")
        
        # Transformer le produit
        shopify_product = transform_to_shopify_product(product)
        
        # Ajouter le produit
        result = add_product_to_shopify(args.api_url, shopify_product)
        
        if result and "task_id" in result:
            task_id = result["task_id"]
            print(f"     Tâche créée avec l'ID: {task_id}")
            
            # Attendre la fin de la tâche
            status = wait_for_task_completion(args.api_url, task_id)
            
            if status == "completed":
                print(f"     ✅ Produit ajouté avec succès")
                successful_additions += 1
            elif status == "failed":
                print(f"     ❌ Échec de l'ajout du produit")
            else:  # timeout
                print(f"     ⏱️ Délai d'attente dépassé pour l'ajout du produit")
        else:
            print(f"     ❌ Échec de la création de la tâche")
    
    # Résumé
    print(f"\n===== Résumé =====")
    print(f"Produits récupérés: {len(analysis_results.get('top_products', []))}")
    print(f"Produits filtrés: {len(recommended_products)}")
    print(f"Produits ajoutés avec succès: {successful_additions}")
    print(f"Date de fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
