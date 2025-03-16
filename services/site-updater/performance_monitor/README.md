# Module Performance Monitor

Ce module est responsable de la surveillance et de l'optimisation continues des performances des sites e-commerce générés par le système. Il fait partie de l'agent Site Updater et constitue le dernier composant à être implémenté pour compléter cet agent.

## Fonctionnalités

### Surveillance des performances

- **Collecte des métriques Web Vitals** : Analyse des métriques critiques (LCP, CLS, FID, TTFB, etc.)
- **Analyse des ressources** : Détection des problèmes avec les fichiers JS, CSS, images et polices
- **Monitoring périodique** : Surveillance régulière des performances avec détection automatique des régressions
- **Analyse des tendances** : Suivi de l'évolution des performances au fil du temps

### Optimisation automatique

- **Détection des problèmes** : Identification automatique des goulots d'étranglement de performance
- **Suggestions d'optimisation** : Génération de recommandations adaptées aux problèmes détectés
- **Optimisation automatique** : Application automatique des optimisations pour les problèmes courants
- **Reporting détaillé** : Génération de rapports complets avec score de performance et suivi des améliorations

### Outils d'optimisation

- **Optimisation d'images** : Conversion et compression des images pour des performances optimales
- **Minification des ressources** : Optimisation automatique des fichiers JS et CSS
- **Analyse SEO** : Évaluation de l'impact des performances sur le référencement
- **Surveillance multi-pages** : Analyse des performances à travers différentes sections du site

## Architecture

Le module Performance Monitor est composé de plusieurs composants :

- **PerformanceManager** : Classe principale qui orchestre toutes les fonctionnalités
- **ImageOptimizer** : Optimisation des images (conversion, compression, lazy loading)
- **ResourceMinifier** : Minification des fichiers JS et CSS
- **PerformanceMetricsAnalyzer** : Analyse des tendances et détection des régressions
- **SEOPerformanceAnalyzer** : Évaluation de l'impact SEO des performances

## Métriques surveillées

Le module surveille les métriques de performance suivantes :

| Métrique | Description | Seuil recommandé |
|----------|-------------|------------------|
| **Largest Contentful Paint (LCP)** | Temps de chargement du plus grand élément visible | < 2.5 secondes |
| **First Input Delay (FID)** | Temps de réponse à la première interaction utilisateur | < 100 ms |
| **Cumulative Layout Shift (CLS)** | Stabilité visuelle pendant le chargement | < 0.1 (sans unité) |
| **Time To First Byte (TTFB)** | Temps de réponse initial du serveur | < 600 ms |
| **Page Load Time** | Temps de chargement complet de la page | < 3 secondes |
| **Server Response Time** | Temps de réponse du serveur | < 500 ms |

## Utilisation

### Initialisation

```python
from performance_manager import PerformanceManager

# Initialisation du gestionnaire de performance
performance_manager = PerformanceManager(
    api_url="https://api.example.com",
    shopify_api_key="your_shopify_key",
    shopify_api_secret="your_shopify_secret",
    shopify_store_url="your-store.myshopify.com"
)
```

### Analyse de performance sur demande

```python
# Générer un rapport de performance pour une URL
report = await performance_manager.generate_performance_report("https://your-store.myshopify.com/products/example")

# Accéder aux informations du rapport
print(f"Score global: {report['summary']['overall_score']}")
print(f"Problèmes identifiés: {report['summary']['issue_count']}")
print(f"Optimisations appliquées: {report['summary']['optimizations_applied']}")
```

### Surveillance continue

```python
# Programmer une surveillance régulière (toutes les 24 heures)
import asyncio

# Dans une fonction asynchrone
asyncio.create_task(
    performance_manager.schedule_performance_monitoring("https://your-store.myshopify.com", interval_hours=24)
)
```

### Analyses ponctuelles

```python
# Collecter uniquement les données de performance
performance_data = await performance_manager.collect_performance_data("https://your-store.myshopify.com")

# Analyser uniquement les ressources
resource_data = await performance_manager.analyze_resources("https://your-store.myshopify.com")

# Suivre l'évolution des performances
trends = await performance_manager.monitor_performance_over_time(
    "https://your-store.myshopify.com",
    days=7,
    interval_hours=6
)
```

## Intégration avec les autres modules

Le module Performance Monitor est conçu pour fonctionner en synergie avec les autres modules de l'agent Site Updater :

- **Price Monitor** : Coordination pour l'optimisation des performances lors des mises à jour de prix
- **A/B Testing** : Analyse des performances des différentes variantes de test
- **Product Rotation** : Optimisation des performances lors de la rotation des produits mis en avant
- **SEO Optimization** : Amélioration des aspects de performance impactant le référencement

Il s'intègre également avec les autres agents du système :

- **Content Generator** : Suggestions pour améliorer le contenu en fonction des performances
- **Website Builder** : Application des optimisations à la structure du site
- **Data Analyzer** : Corrélation entre les performances et les métriques de conversion

## Tests

Le module comprend une suite de tests unitaires complète pour garantir la qualité et la fiabilité du code. Pour exécuter les tests :

```bash
cd services/site-updater/performance_monitor
python -m unittest test_performance_manager.py
```

## Roadmap

Les améliorations planifiées pour les versions futures comprennent :

1. **Optimisation avancée des images** : Support pour WebP et AVIF avec détection automatique du format optimal
2. **Analyse de code mort** : Détection et suppression du JavaScript et CSS inutilisés
3. **Optimisation de la mise en cache** : Configuration automatique des en-têtes de cache
4. **Analyse prédictive** : Prévision des problèmes de performance avant qu'ils n'impactent les utilisateurs
5. **Rapport de performance comparatif** : Benchmarking par rapport aux concurrents

## Exigences

- Python 3.9+
- aiohttp
- asyncio
- Accès à l'API Shopify
- Accès à l'API centrale du système
