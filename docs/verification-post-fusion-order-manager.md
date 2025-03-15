# Guide de vérification post-fusion de l'agent Order Manager

Ce document détaille les vérifications à effectuer après la fusion de la branche `order-manager-complete` dans la branche principale (`main`) pour s'assurer que l'intégration s'est déroulée correctement et que toutes les fonctionnalités sont opérationnelles.

## Objectifs de la vérification

Les vérifications post-fusion ont pour objectifs de :

1. Confirmer que tous les composants du système démarrent correctement
2. Valider que l'agent Order Manager fonctionne comme prévu
3. Vérifier l'intégration avec les autres agents
4. S'assurer qu'aucune régression n'a été introduite

## Liste de contrôle technique

### 1. Vérification du déploiement

- [ ] Tous les conteneurs Docker démarrent correctement
  ```bash
  docker-compose ps
  # Vérifier que le statut de tous les services est "Up"
  ```

- [ ] Les logs ne contiennent pas d'erreurs
  ```bash
  docker-compose logs | grep -i error
  # Vérifier qu'aucune erreur critique n'est présente
  ```

- [ ] L'agent Order Manager répond aux requêtes de santé
  ```bash
  curl -X GET "http://localhost:8000/agents/order-manager/health" | jq
  # Devrait retourner {"status": "ok", "version": "x.y.z"}
  ```

### 2. Vérification fonctionnelle de l'agent Order Manager

- [ ] L'API d'Order Manager répond correctement
  ```bash
  curl -X GET "http://localhost:8000/agents/order-manager/orders?limit=5" | jq
  # Devrait retourner une liste de commandes ou un tableau vide
  ```

- [ ] Création d'une commande de test
  ```bash
  curl -X POST "http://localhost:8000/agents/order-manager/orders" \
    -H "Content-Type: application/json" \
    -d '{
      "test_order": true,
      "customer": {
        "name": "Test Customer",
        "email": "test@example.com"
      },
      "shipping_address": {
        "address1": "123 Test Street",
        "city": "Test City",
        "zip": "12345",
        "country": "Test Country"
      },
      "line_items": [
        {
          "product_id": "test-product-1",
          "quantity": 1,
          "price": 9.99
        }
      ]
    }' | jq
  # Devrait retourner l'ID de la commande créée
  ```

- [ ] Récupération de la commande de test
  ```bash
  curl -X GET "http://localhost:8000/agents/order-manager/orders/{id_commande}" | jq
  # Remplacer {id_commande} par l'ID retourné précédemment
  # Devrait retourner les détails de la commande
  ```

- [ ] Recherche de produits chez les fournisseurs
  ```bash
  curl -X POST "http://localhost:8000/agents/order-manager/suppliers/search" \
    -H "Content-Type: application/json" \
    -d '{
      "supplier": "aliexpress",
      "query": "smartphone accessories",
      "limit": 2
    }' | jq
  # Devrait retourner une liste de produits AliExpress
  ```

### 3. Vérification de l'intégration avec les autres agents

- [ ] Communication avec l'agent Data Analyzer
  ```bash
  # Créer une commande de test puis vérifier que les informations sont disponibles pour Data Analyzer
  curl -X GET "http://localhost:8000/agents/data-analyzer/products/recent-sales" | jq
  # Devrait inclure des données provenant de l'agent Order Manager
  ```

- [ ] Communication avec l'agent Website Builder
  ```bash
  # Vérifier que Website Builder peut récupérer les informations de suivi
  curl -X GET "http://localhost:8000/agents/website-builder/shipping-info?order_id={id_commande}" | jq
  # Devrait retourner les informations de suivi de la commande
  ```

- [ ] Communication avec l'agent Content Generator
  ```bash
  # Vérifier que Content Generator peut accéder aux avis sur les produits
  curl -X GET "http://localhost:8000/agents/content-generator/product-reviews?product_id=test-product-1" | jq
  # Devrait inclure des données provenant de l'agent Order Manager
  ```

### 4. Vérification des workflows

- [ ] Workflow de traitement de commande
  ```bash
  # Déclencher le workflow de traitement de commande
  curl -X POST "http://localhost:8000/api/workflows/order-processing" \
    -H "Content-Type: application/json" \
    -d '{
      "order_id": "{id_commande}"
    }' | jq
  # Devrait retourner l'ID du workflow déclenché
  
  # Vérifier l'état du workflow après quelques secondes
  curl -X GET "http://localhost:8000/api/workflows/{workflow_id}" | jq
  # Devrait montrer les étapes complétées
  ```

- [ ] Workflow d'alerte de stock
  ```bash
  # Déclencher une alerte de stock
  curl -X POST "http://localhost:8000/agents/order-manager/products/stock-alert" \
    -H "Content-Type: application/json" \
    -d '{
      "product_id": "test-product-1",
      "current_stock": 2,
      "threshold": 5
    }' | jq
  
  # Vérifier que l'alerte a été traitée par Data Analyzer
  curl -X GET "http://localhost:8000/agents/data-analyzer/alerts" | jq
  # Devrait inclure l'alerte de stock
  ```

### 5. Tests de charge

- [ ] Test de réponse sous charge légère
  ```bash
  # Utiliser un outil comme Apache Bench pour envoyer 50 requêtes sur 10 secondes
  ab -n 50 -c 5 http://localhost:8000/agents/order-manager/health
  # Vérifier le temps de réponse moyen et les erreurs
  ```

- [ ] Test de création simultanée de commandes
  ```bash
  # Script pour créer 10 commandes simultanément
  for i in {1..10}; do
    curl -X POST "http://localhost:8000/agents/order-manager/orders" \
      -H "Content-Type: application/json" \
      -d '{
        "test_order": true,
        "customer": {
          "name": "Test Customer '"$i"'",
          "email": "test'"$i"'@example.com"
        },
        "shipping_address": {
          "address1": "123 Test Street",
          "city": "Test City",
          "zip": "12345",
          "country": "Test Country"
        },
        "line_items": [
          {
            "product_id": "test-product-'"$i"'",
            "quantity": 1,
            "price": 9.99
          }
        ]
      }' &
  done
  wait
  
  # Vérifier que toutes les commandes ont été créées
  curl -X GET "http://localhost:8000/agents/order-manager/orders?limit=20" | jq
  # Devrait retourner au moins 10 commandes
  ```

### 6. Vérification de la base de données

- [ ] Vérifier les migrations
  ```bash
  # Se connecter à la base de données
  docker-compose exec postgres psql -U postgres -d dropshipping
  
  # Lister les tables liées à Order Manager
  \dt orders*
  \dt supplier*
  \dt shipments*
  
  # Vérifier la structure d'une table clé
  \d orders
  ```

- [ ] Vérifier l'intégrité des données
  ```bash
  # Exemple de requête pour vérifier la cohérence
  SELECT COUNT(*) FROM orders;
  SELECT COUNT(*) FROM supplier_orders;
  SELECT COUNT(*) FROM shipments;
  
  # Vérifier la relation entre les tables
  SELECT o.id, COUNT(so.id) 
  FROM orders o 
  LEFT JOIN supplier_orders so ON o.id = so.order_id 
  GROUP BY o.id;
  ```

### 7. Vérification de l'intégration Shopify

- [ ] Test du webhook Shopify
  ```bash
  # Simuler un webhook Shopify
  curl -X POST "http://localhost:8000/agents/order-manager/webhooks/shopify" \
    -H "Content-Type: application/json" \
    -H "X-Shopify-Hmac-Sha256: {signature_simulée}" \
    -d '{
      "id": 450789469,
      "email": "john@example.com",
      "closed_at": null,
      "created_at": "2025-03-15T05:33:43-04:00",
      "updated_at": "2025-03-15T05:33:43-04:00",
      "number": 1,
      "note": null,
      "token": "123456abcd",
      "gateway": "bogus",
      "test": true,
      "total_price": "403.00",
      "subtotal_price": "388.00",
      "total_tax": "15.00",
      "currency": "USD",
      "financial_status": "paid",
      "confirmed": true,
      "total_discounts": "5.00",
      "total_line_items_price": "393.00",
      "line_items": [
        {
          "id": 466157049,
          "quantity": 1,
          "price": "199.00",
          "title": "Test Product"
        }
      ],
      "shipping_address": {
        "address1": "123 Shipping Street",
        "city": "Shippingville",
        "zip": "K2P0B0",
        "country": "Canada"
      }
    }'
  ```

- [ ] Vérifier la création de commande via Shopify
  ```bash
  # Vérifier que la commande Shopify a été créée
  curl -X GET "http://localhost:8000/agents/order-manager/orders?source=shopify&external_id=450789469" | jq
  # Devrait retourner la commande créée via webhook
  ```

### 8. Vérification de l'intégration AliExpress

- [ ] Test de recherche de produits
  ```bash
  curl -X POST "http://localhost:8000/agents/order-manager/suppliers/aliexpress/search" \
    -H "Content-Type: application/json" \
    -d '{
      "query": "wireless earbuds",
      "limit": 5
    }' | jq
  # Devrait retourner des produits AliExpress
  ```

- [ ] Test de récupération des détails de produit
  ```bash
  # Utiliser un ID produit retourné par la recherche précédente
  curl -X GET "http://localhost:8000/agents/order-manager/suppliers/aliexpress/products/{product_id}" | jq
  # Devrait retourner les détails complets du produit
  ```

- [ ] Test de calcul d'expédition
  ```bash
  curl -X POST "http://localhost:8000/agents/order-manager/suppliers/aliexpress/shipping" \
    -H "Content-Type: application/json" \
    -d '{
      "product_id": "{product_id}",
      "quantity": 1,
      "country": "US",
      "zipcode": "90210"
    }' | jq
  # Devrait retourner les options d'expédition disponibles
  ```

## 9. Vérification des événements et notifications

- [ ] Test du système d'événements
  ```bash
  # Déclencher un événement (exemple: mise à jour de stock)
  curl -X POST "http://localhost:8000/api/events" \
    -H "Content-Type: application/json" \
    -d '{
      "type": "product.stock_updated",
      "data": {
        "product_id": "test-product-1",
        "new_stock": 50,
        "previous_stock": 10
      }
    }' | jq
  
  # Vérifier que l'événement a été traité
  curl -X GET "http://localhost:8000/api/events?type=product.stock_updated&limit=1" | jq
  # Devrait retourner l'événement créé
  ```

- [ ] Test des notifications
  ```bash
  # Vérifier la configuration des notifications
  curl -X GET "http://localhost:8000/agents/order-manager/notification-templates" | jq
  # Devrait retourner les templates de notification disponibles
  
  # Envoyer une notification de test
  curl -X POST "http://localhost:8000/agents/order-manager/notifications/test" \
    -H "Content-Type: application/json" \
    -d '{
      "email": "test@example.com",
      "template": "order_confirmation",
      "data": {
        "order_id": "{id_commande}",
        "customer_name": "Test Customer"
      }
    }' | jq
  # Devrait confirmer l'envoi de la notification
  ```

## 10. Vérification des informations de monitoring

- [ ] Métriques de l'agent Order Manager
  ```bash
  curl -X GET "http://localhost:8000/agents/order-manager/metrics" | jq
  # Devrait retourner les métriques de performance
  ```

- [ ] Statut des jobs en cours
  ```bash
  curl -X GET "http://localhost:8000/agents/order-manager/jobs" | jq
  # Devrait retourner les jobs en cours d'exécution
  ```

## Gestion des problèmes courants

### Problème: L'agent Order Manager ne démarre pas

Vérifications:
1. Examiner les logs Docker spécifiques
   ```bash
   docker-compose logs order-manager
   ```
2. Vérifier les variables d'environnement
   ```bash
   docker-compose config | grep -A 20 order-manager
   ```
3. Vérifier les connexions aux dépendances (PostgreSQL, Redis)
   ```bash
   docker-compose exec order-manager python -c "import psycopg2; conn=psycopg2.connect('dbname=dropshipping user=postgres host=postgres'); print('PostgreSQL: OK')"
   docker-compose exec order-manager python -c "import redis; r=redis.Redis(host='redis'); r.ping() and print('Redis: OK')"
   ```

### Problème: Échec des appels API AliExpress

Vérifications:
1. Vérifier les identifiants AliExpress dans les variables d'environnement
2. Examiner les logs spécifiques aux appels API externes
   ```bash
   docker-compose logs | grep -i aliexpress
   ```
3. Vérifier si le proxy est correctement configuré (si utilisé)
   ```bash
   docker-compose exec order-manager curl -v https://api.aliexpress.com/healthcheck
   ```

### Problème: Échec des webhooks Shopify

Vérifications:
1. Vérifier que l'URL de webhook est accessible depuis l'extérieur
2. Examiner les logs pour les erreurs de validation de signature
3. Vérifier les permissions de l'application Shopify

## Validation finale

Pour considérer la fusion comme réussie, tous les éléments suivants doivent être validés:

- [ ] Toutes les vérifications techniques ont réussi
- [ ] Aucune erreur critique dans les logs après 24h de fonctionnement
- [ ] Les métriques de performance restent stables (temps de réponse < 500ms)
- [ ] Le traitement des commandes de test se déroule de bout en bout sans erreur
- [ ] L'intégration avec tous les autres agents fonctionne correctement
- [ ] Le dashboard affiche correctement les données de l'agent Order Manager

## Procédure de rollback

Si des problèmes critiques sont détectés et ne peuvent pas être résolus rapidement:

1. Arrêter les services
   ```bash
   docker-compose down
   ```

2. Réversion de la fusion git
   ```bash
   git revert -m 1 <commit-de-fusion>
   git push origin main
   ```

3. Redémarrer les services
   ```bash
   docker-compose up -d
   ```

4. Vérifier que le système est revenu à un état stable
   ```bash
   docker-compose ps
   curl -X GET "http://localhost:8000/api/health" | jq
   ```

## Journal des vérifications

| Date       | Version | Responsable | Résultat | Commentaires |
|------------|---------|-------------|----------|--------------|
| YYYY-MM-DD | x.y.z   | Nom         | ✅/❌     | Notes        |

## Conclusion

Cette vérification post-fusion est une étape cruciale pour assurer que l'intégration de l'agent Order Manager dans la branche principale se déroule sans perturbation pour le système existant. En suivant ce guide systématiquement, vous pourrez identifier et corriger rapidement tout problème potentiel.

N'oubliez pas de documenter votre processus de vérification dans le journal des vérifications pour référence future et traçabilité.

---

*Document créé le 15 mars 2025*
