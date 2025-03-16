# Architecture d'API centralisée

Ce document décrit l'architecture de l'API centralisée qui sert de colonne vertébrale au système, permettant aux différents agents de communiquer et de collaborer.

## Vue d'ensemble

L'API centralisée est conçue comme un hub de communication qui:
- Fournit une interface unifiée pour tous les agents
- Coordonne les flux de travail entre agents
- Gère l'authentification et les autorisations
- Standardise les formats de données
- Facilite le monitoring et la traçabilité des opérations

## Structure de l'API

L'API est construite sur FastAPI, un framework Python moderne et performant. Ses principales caractéristiques sont:

### Points d'accès REST

L'API expose des endpoints REST organisés logiquement:

```
/api/
  /v1/                          # Version 1 de l'API
    /agents/                    # Points d'accès pour les agents
      /data-analyzer/           # API de l'agent Data Analyzer
        /analyze                # Analyse de marché et de produits
        /trends                 # Analyse de tendances
        /complementary          # Analyse de produits complémentaires
        /score                  # Scoring de produits
      
      /website-builder/         # API de l'agent Website Builder
        /store                  # Configuration de la boutique
        /theme                  # Gestion des thèmes
        /navigation             # Structure de navigation
        /collections            # Gestion des collections
      
      /content-generator/       # API de l'agent Content Generator
        /product-descriptions   # Génération de descriptions produits
        /metadata               # Génération de métadonnées SEO
        /blog                   # Génération d'articles de blog
      
      /order-manager/           # API de l'agent Order Manager
        /orders                 # Gestion des commandes
        /suppliers              # Intégration fournisseurs
        /shipping               # Suivi des expéditions
        /notifications          # Notifications clients
    
    /workflows/                 # Orchestration des workflows entre agents
      /initialize-product       # Workflow d'ajout de produit complet
      /update-product           # Workflow de mise à jour produit
      /process-order            # Workflow de traitement de commande
    
    /system/                    # Endpoints système
      /health                   # État de santé des services
      /metrics                  # Métriques de performance
      /logs                     # Accès aux logs centralisés
```

### Modèles de données

L'API utilise des modèles Pydantic pour:
- Valider les données entrantes et sortantes
- Documenter automatiquement les schémas
- Assurer la cohérence des données entre agents

Exemples de modèles:
- `Product`: Structure complète d'un produit
- `Order`: Structure d'une commande
- `AnalysisResult`: Résultat d'analyse de marché
- `ContentRequest`: Demande de génération de contenu

### Authentification et sécurité

L'API implémente plusieurs niveaux de sécurité:
- Authentification par API key pour les clients externes
- Authentification basée sur les rôles pour les différents agents
- Rate limiting pour prévenir les abus
- Validation des données d'entrée
- Sanitization des réponses

## Moteur de workflows

Un composant central de l'API est son moteur de workflows qui permet de définir et d'exécuter des séquences d'opérations impliquant plusieurs agents.

### Concepts clés

- **Workflow**: Séquence d'étapes définissant un processus métier
- **Task**: Unité de travail individuelle dans un workflow
- **Transition**: Règle définissant le passage d'une tâche à une autre
- **Trigger**: Événement déclenchant un workflow
- **State**: État d'une instance de workflow en cours d'exécution

### Exemple de workflow: Ajout de nouveau produit

```
1. Data Analyzer:
   - Analyser le potentiel du produit
   - Identifier les produits complémentaires
   - Générer un score et des recommandations

2. Content Generator:
   - Générer la description produit optimisée SEO
   - Créer les métadonnées
   - Préparer le matériel marketing

3. Website Builder:
   - Ajouter le produit au catalogue
   - Configurer les collections et catégories
   - Mettre en place les cross-sells

4. Order Manager:
   - Configurer les relations avec les fournisseurs
   - Définir les règles de stock et réapprovisionnement
```

### État actuel du moteur de workflows

- ✅ Définition des workflows en YAML
- ✅ Exécution séquentielle de tâches
- ✅ Gestion des erreurs de base
- 🔄 Transitions conditionnelles en développement
- 🔄 Parallélisation des tâches en développement
- 🔄 Interface visuelle pour les workflows en planification

## Système d'événements

L'API inclut un système d'événements basé sur Redis Pub/Sub pour faciliter la communication asynchrone entre les agents.

### Types d'événements

- **ProductEvents**: Événements liés aux produits (création, mise à jour, etc.)
- **OrderEvents**: Événements liés aux commandes
- **ContentEvents**: Événements liés à la génération de contenu
- **AnalysisEvents**: Événements liés à l'analyse de données
- **SystemEvents**: Événements système (maintenance, etc.)

### Exemple d'utilisation

```python
# Publication d'un événement
await event_bus.publish(
    "product.created",
    {
        "product_id": "abc123",
        "name": "Smartphone Case",
        "score": 87.5,
        "timestamp": "2025-03-16T12:34:56Z"
    }
)

# Souscription à un événement
@event_bus.subscribe("product.created")
async def handle_new_product(event_data):
    # Traitement de l'événement
    product_id = event_data["product_id"]
    # ...
```

## Gestionnaire de tâches

L'API intègre un gestionnaire de tâches pour l'exécution de processus asynchrones et planifiés:

- **Tâches asynchrones**: Opérations longues exécutées en arrière-plan
- **Tâches planifiées**: Opérations récurrentes (mises à jour, maintenance)
- **Tâches distribuées**: Répartition de la charge entre instances

Technologies utilisées:
- Redis comme broker de messages
- Celery comme framework de tâches asynchrones
- APScheduler pour la planification de tâches récurrentes

## Performance et mise à l'échelle

L'API est conçue pour être performante et évolutive:

- Réponses mises en cache via Redis
- Utilisation efficace des connexions avec des pools de connexions
- Architecture sans état facilitant la mise à l'échelle horizontale
- Utilisation d'async/await pour une gestion efficace des I/O

## Monitoring et observabilité

L'API expose des métriques et logs pour le monitoring:

- Métriques Prometheus sur `/system/metrics`
- Logs structurés au format JSON
- Traçage des requêtes avec IDs de corrélation
- Alertes sur seuils critiques de performance ou d'erreurs

## Documentation

L'API est auto-documentée grâce à OpenAPI (Swagger):

- Documentation interactive disponible sur `/api/docs`
- Exemples de requêtes et réponses
- Description des modèles de données
- Guide d'authentification

## Prochaines évolutions

L'API est en développement continu avec les améliorations prévues:

1. **Avancées du moteur de workflows**:
   - Interface visuelle pour la conception de workflows
   - Analyse et optimisation des workflows
   - Gestion des états et reprises après erreur

2. **Système d'événements amélioré**:
   - Filtrage avancé des événements
   - Persistance des événements pour replay
   - Observabilité des flux d'événements

3. **Améliorations de performance**:
   - Optimisation des requêtes fréquentes
   - Stratégies avancées de mise en cache
   - Compression des payloads

4. **Sécurité renforcée**:
   - Mise en œuvre d'OAuth 2.0
   - Chiffrement de bout en bout pour les données sensibles
   - Détection avancée d'intrusion
