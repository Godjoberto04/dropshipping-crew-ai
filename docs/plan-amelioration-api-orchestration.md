# Plan d'amélioration de l'API pour l'orchestration des agents

## Analyse de la situation actuelle

Le système actuel utilise une API centralisée qui permet déjà une communication efficace entre les différents agents du projet dropshipping-crew-ai. L'architecture présente les caractéristiques suivantes:

- **API REST centralisée** qui sert de point d'échange entre les agents
- **Système de tâches** permettant de distribuer le travail à chaque agent
- **Base de données PostgreSQL** pour le stockage persistant des données
- **Cache Redis** pour la gestion des états et des données temporaires
- **Agents indépendants** qui vérifient périodiquement les tâches à exécuter

Cette architecture a permis de développer efficacement les premiers agents (Data Analyzer et Website Builder) mais pourrait être optimisée pour faciliter la coordination lors de l'ajout des agents suivants (Content Generator, Order Manager et Site Updater).

## Objectifs des améliorations

Plutôt que d'ajouter un agent manager supplémentaire (qui ajouterait de la complexité inutile), nous proposons d'étendre les fonctionnalités de l'API existante pour créer un système d'orchestration plus robuste avec les objectifs suivants:

1. **Faciliter les workflows multi-agents** pour les opérations nécessitant plusieurs étapes
2. **Améliorer la traçabilité** des opérations à travers le système
3. **Permettre des déclenchements automatiques** basés sur des événements
4. **Optimiser la résilience** du système en cas d'échec d'un agent
5. **Simplifier l'ajout de nouveaux agents** au système

## Améliorations proposées

### 1. Moteur de workflows

#### Description
Implémentation d'un moteur de workflows dans l'API permettant de définir et d'exécuter des séquences d'opérations impliquant plusieurs agents.

#### Composants
- **Définition de workflows**: Schéma JSON pour définir des séquences d'actions impliquant plusieurs agents
- **État de workflow**: Stockage et suivi de l'état d'avancement des workflows
- **Gestion des transitions**: Logique pour passer d'une étape à l'autre
- **Gestion des erreurs**: Mécanismes de reprise et de compensation en cas d'échec

#### Exemple de workflow
```json
{
  "workflow_id": "new_product_pipeline",
  "name": "Pipeline d'ajout de nouveau produit",
  "steps": [
    {
      "step_id": "market_analysis",
      "agent": "data-analyzer",
      "action": "analyze_product",
      "params": {
        "product_url": "${input.product_url}",
        "market_segment": "${input.market_segment}"
      }
    },
    {
      "step_id": "content_generation",
      "agent": "content-generator",
      "action": "generate_product_description",
      "params": {
        "product_data": "${steps.market_analysis.result.product_data}",
        "tone": "persuasive",
        "language": "fr"
      },
      "requires": ["market_analysis"]
    },
    {
      "step_id": "product_creation",
      "agent": "website-builder",
      "action": "add_product",
      "params": {
        "product_data": "${steps.market_analysis.result.product_data}",
        "product_description": "${steps.content_generation.result.description}",
        "seo_metadata": "${steps.content_generation.result.seo_metadata}"
      },
      "requires": ["market_analysis", "content_generation"]
    }
  ]
}
```

### 2. Système d'événements et de déclencheurs

#### Description
Un système permettant aux agents de publier des événements et à d'autres agents de s'y abonner ou de déclencher des actions automatiquement.

#### Composants
- **Publication d'événements**: API pour publier des événements depuis les agents
- **Abonnements**: Mécanisme permettant aux agents de s'abonner à des événements
- **Déclencheurs conditionnels**: Règles pour exécuter des actions basées sur des événements
- **File d'événements**: Système de file d'attente pour traiter les événements de manière asynchrone

#### Exemples d'événements
- `product.analyzed`: Déclenché après l'analyse d'un produit par Data Analyzer
- `product.created`: Déclenché après l'ajout d'un produit par Website Builder
- `order.received`: Déclenché à la réception d'une nouvelle commande
- `content.generated`: Déclenché après la génération de contenu

### 3. Tableau de bord d'orchestration avancé

#### Description
Extension du tableau de bord actuel pour intégrer des fonctionnalités de monitoring et de contrôle des workflows et événements.

#### Composants
- **Visualisation des workflows**: Interface pour visualiser et suivre les workflows en cours
- **Monitoring des événements**: Affichage des événements récents et de leur traitement
- **Contrôles manuels**: Possibilité d'intervenir manuellement dans les workflows
- **Alertes et notifications**: Système d'alerte en cas d'erreur ou de blocage

### 4. API d'orchestration étendue

#### Description
Nouveaux endpoints API pour gérer les workflows, événements et la coordination entre agents.

#### Nouveaux endpoints
- `/workflows`: Gestion des définitions de workflows
- `/workflows/{id}/instances`: Gestion des instances de workflows
- `/events`: Publication et abonnement aux événements
- `/triggers`: Gestion des déclencheurs automatiques
- `/agents/{id}/capabilities`: Documentation des capacités de chaque agent

## Plan d'implémentation

### Phase 1: Fondations (2 semaines)
- Conception détaillée du système de workflows
- Schéma de base de données pour les workflows et événements
- Implémentation des endpoints API de base

### Phase 2: Workflows basiques (2 semaines)
- Implémentation du moteur d'exécution de workflows
- Intégration avec les agents existants (Data Analyzer, Website Builder)
- Création des premiers workflows pour la gestion des produits

### Phase 3: Système d'événements (1 semaine)
- Implémentation du système de publication/abonnement
- Intégration des événements dans les agents existants
- Mise en place des premiers déclencheurs automatiques

### Phase 4: Interface d'administration (1 semaine)
- Extension du tableau de bord pour visualiser les workflows
- Ajout des contrôles manuels et du monitoring
- Documentation et guides d'utilisation

## Intégration avec les phases existantes du projet

Cette amélioration de l'API s'intègre naturellement dans le calendrier de développement actuel:

- **Semaines 3-4**: Développement des fondations et workflows basiques pendant le développement du Content Generator
- **Semaines 5-6**: Implémentation du système d'événements et des premiers workflows complexes pendant le développement de l'Order Manager
- **Semaines 7-8**: Finalisation de l'interface d'administration pendant le développement du Site Updater

## Avantages pour le projet

1. **Accélération du développement**: Réduction du temps nécessaire pour implémenter les interactions entre agents
2. **Meilleure qualité**: Traçabilité complète des opérations et gestion standardisée des erreurs
3. **Facilité d'extension**: Ajout simplifié de nouveaux agents et fonctionnalités
4. **Autonomie accrue**: Automatisation de scénarios complexes sans intervention humaine
5. **Monitoring amélioré**: Visibilité complète sur l'état du système à tout moment

## Conclusion

En améliorant l'API existante pour y ajouter des capacités d'orchestration avancées, nous pouvons obtenir tous les avantages qu'aurait pu apporter un "agent manager" sans introduire de complexité supplémentaire ni de point unique de défaillance. Cette approche s'aligne parfaitement avec l'architecture modulaire du projet et permettra d'accélérer le développement des prochains agents tout en maintenant une base de code propre et maintenable.

---

*Document créé le 10 mars 2025*