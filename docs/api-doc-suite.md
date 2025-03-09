# Suite de la documentation API

## Exemple d'intégration (suite)

```python
# Récupérer les résultats de l'analyse
response = requests.get(f"{API_BASE_URL}/analysis/results/latest")
analysis_results = response.json()

# Afficher les produits recommandés
print("\nProduits recommandés:")
for product in analysis_results["top_products"]:
    print(f"- {product['name']} (Score: {product['recommendation_score']}/10)")
    print(f"  Prix fournisseur: {product['supplier_price']}€, Prix recommandé: {product['recommended_price']}€")
    print(f"  Marge: {product['potential_margin_percent']}%")
    print(f"  Tendance: {product['trend_direction']}, Concurrence: {product['competition_level']}")
    print(f"  Justification: {product['justification']}")
    print("")

# Sélectionner les meilleurs produits pour les ajouter à la boutique
# (Future implémentation - Website Builder)
selected_products = [p for p in analysis_results["top_products"] 
                    if p["recommendation_score"] >= 8.0]

print(f"Ajout de {len(selected_products)} produits à la boutique...")

# Génerer du contenu pour les produits sélectionnés
# (Future implémentation - Content Generator)
for product in selected_products:
    # Créer des données enrichies pour la génération de contenu
    product_data = {
        "title": product["name"],
        "features": product["justification"].split(", "),
        "product_type": "accessoire smartphone",  # À adapter selon le produit
        "benefits": ["Facilité d'utilisation", "Qualité premium"]  # À personnaliser
    }
    
    # Générer une description
    response = requests.post(
        f"{API_BASE_URL}/agents/content-generator/generate",
        json={
            "product_data": product_data,
            "content_type": "description",
            "length": "medium"
        }
    )
    
    # Dans une implémentation réelle, on stockerait ces informations
    # et on les utiliserait pour créer le produit dans Shopify
    # via l'agent Website Builder
```

## Schémas de données

### Product

Schéma représentant un produit analysé.

```json
{
  "name": "string",
  "supplier_price": "number",
  "recommended_price": "number",
  "potential_margin_percent": "number",
  "competition_level": "string (Low|Medium|High)",
  "trend_direction": "string (Up|Stable|Down)",
  "recommendation_score": "number (0-10)",
  "justification": "string"
}
```

### Analysis

Schéma représentant une analyse de marché complète.

```json
{
  "analysis_id": "string",
  "created_at": "string (ISO date)",
  "source_urls": ["string"],
  "top_products": ["Product"]
}
```

### Task

Schéma représentant une tâche en cours d'exécution.

```json
{
  "task_id": "string",
  "status": "string (queued|in_progress|completed|failed)",
  "progress": "number (0-100)",
  "message": "string",
  "started_at": "number (timestamp)",
  "estimated_completion": "number (timestamp)"
}
```

### Order

Schéma représentant une commande client.

```json
{
  "order_id": "string",
  "customer": {
    "name": "string",
    "email": "string",
    "shipping_address": {
      "street": "string",
      "city": "string",
      "postal_code": "string",
      "country": "string"
    }
  },
  "items": [
    {
      "product_id": "string",
      "quantity": "number",
      "price": "number"
    }
  ],
  "total_amount": "number",
  "shipping_method": "string"
}
```

## Bonnes pratiques pour l'utilisation de l'API

### Limitation des requêtes

Pour éviter les surcharges du système, respectez les limites suivantes :
- Maximum 10 requêtes par minute pour les endpoints GET
- Maximum 5 requêtes par minute pour les endpoints POST
- Maximum 3 requêtes d'analyse de marché par heure

### Gestion des erreurs

Toujours vérifier le code de statut HTTP des réponses :
- 2xx : Succès
- 4xx : Erreur client (vérifier les paramètres de la requête)
- 5xx : Erreur serveur (réessayer plus tard)

### Polling recommandé

Pour les tâches longue durée (analyse de marché, mise à jour des prix, etc.), utilisez le polling avec des intervalles exponentiels :
1. Commencez avec un intervalle de 5 secondes
2. Doublez l'intervalle à chaque requête jusqu'à un maximum de 60 secondes
3. Réduisez l'intervalle à 5 secondes une fois que la tâche atteint 90% de progression

## Prochaines fonctionnalités de l'API

Les fonctionnalités suivantes sont prévues pour les prochaines versions :

### Version 1.1 (semaine 4)
- Authentification par token JWT
- Gestion des permissions par rôle
- Filtrage avancé des résultats d'analyse
- Ajout de métriques et statistiques

### Version 1.2 (semaine 6)
- Webhooks pour les notifications d'événements
- API GraphQL en complément de l'API REST
- Support des opérations par lot
- Historique des analyses avec comparaison

### Version 1.3 (semaine 8)
- API complète pour tous les agents (Order Manager, Site Updater)
- Personnalisation des paramètres d'analyse
- Export de données aux formats CSV et JSON
- Intégration avec des outils d'analyse externes

## Sécurité et accès à l'API

### Environnements disponibles

- **Développement** : http://dev.dropship-ai.example.com:8000
- **Production** : http://163.172.160.102:8000

### Limites de responsabilité

- L'API est fournie "telle quelle", sans garantie d'aucune sorte
- Les analyses de marché sont fournies à titre informatif et ne constituent pas des conseils d'investissement
- L'utilisateur est responsable de la conformité aux conditions d'utilisation des sites analysés

### Règles d'utilisation

- N'utilisez pas l'API pour des activités illégales
- Respectez les robots.txt des sites analysés
- N'abusez pas des ressources système avec des requêtes excessives

## Support et contact

Pour toute question ou problème concernant l'API :
- Créez une issue sur le dépôt GitHub
- Consultez la documentation mise à jour régulièrement
- Utilisez l'endpoint `/status` pour vérifier la disponibilité des services

---

*Dernière mise à jour : 9 mars 2025*