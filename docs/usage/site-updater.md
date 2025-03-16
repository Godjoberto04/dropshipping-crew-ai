# Agent Site Updater - Guide d'utilisation

L'agent Site Updater est responsable de la mise à jour et de l'optimisation continue de votre boutique en ligne. Il est composé de plusieurs modules spécialisés qui travaillent ensemble pour améliorer différents aspects de votre site e-commerce.

## Modules disponibles

L'agent Site Updater comprend les modules suivants :

1. **Price Monitor** : Surveillance et ajustement automatique des prix
2. **A/B Testing** : Tests automatiques de variations pour optimiser les conversions
3. **Product Rotation** : Rotation intelligente des produits mis en avant
4. **SEO Optimization** : Optimisation continue du référencement naturel
5. **Performance Monitor** : Surveillance et optimisation des performances du site

## Performance Monitor

Le module Performance Monitor est responsable de la surveillance et de l'optimisation des performances de votre site e-commerce. Il analyse en continu les métriques clés de performance, identifie les problèmes et applique automatiquement des optimisations pour améliorer la vitesse et l'expérience utilisateur de votre boutique.

### Fonctionnalités clés

- **Analyse des Web Vitals** : Surveillance des métriques critiques comme LCP, CLS, FID et TTFB
- **Optimisation automatique des ressources** : Minification des fichiers JS/CSS et optimisation des images
- **Détection des problèmes de performance** : Identification des goulots d'étranglement et points d'amélioration
- **Suivi des tendances** : Analyse de l'évolution des performances dans le temps
- **Impact SEO** : Évaluation de l'impact des performances sur le référencement
- **API complète** : Accès programmatique à toutes les fonctionnalités

### Utilisation via l'API

Le module expose une API RESTful complète pour l'intégration avec d'autres systèmes. Voici les principaux endpoints disponibles :

#### Analyser les performances d'une URL

```bash
curl -X POST http://localhost:8005/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://votre-boutique.myshopify.com/products/exemple"}'
```

#### Optimiser les performances d'une URL

```bash
curl -X POST http://localhost:8005/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://votre-boutique.myshopify.com/products/exemple",
    "apply_automatically": true,
    "minify_js_css": true,
    "optimize_images": true,
    "target_image_format": "webp",
    "compress_resources": true
  }'
```

#### Configurer la surveillance périodique

```bash
curl -X POST http://localhost:8005/monitor \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://votre-boutique.myshopify.com/",
    "interval_hours": 24,
    "days": 7,
    "alert_on_regression": true,
    "regression_threshold": 10.0
  }'
```

#### Optimiser un lot d'images

```bash
curl -X POST http://localhost:8005/images/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "image_urls": [
      "https://votre-boutique.myshopify.com/cdn/images/produit1.jpg",
      "https://votre-boutique.myshopify.com/cdn/images/produit2.jpg"
    ],
    "target_format": "webp"
  }'
```

### Intégration avec les autres modules

Le module Performance Monitor est conçu pour fonctionner en synergie avec les autres modules de l'agent Site Updater :

- Avec **Price Monitor** : Optimisation des performances lors des mises à jour de prix
- Avec **A/B Testing** : Analyse des performances des différentes variantes de test
- Avec **Product Rotation** : Optimisation des performances lors des rotations de produits
- Avec **SEO Optimization** : Amélioration des aspects de performance impactant le référencement

### Métriques surveillées

Le module surveille les métriques de performance suivantes :

| Métrique | Description | Seuil recommandé |
|----------|-------------|------------------|
| **Largest Contentful Paint (LCP)** | Temps de chargement du plus grand élément visible | < 2.5 secondes |
| **First Input Delay (FID)** | Temps de réponse à la première interaction utilisateur | < 100 ms |
| **Cumulative Layout Shift (CLS)** | Stabilité visuelle pendant le chargement | < 0.1 (sans unité) |
| **Time To First Byte (TTFB)** | Temps de réponse initial du serveur | < 600 ms |
| **Page Load Time** | Temps de chargement complet de la page | < 3 secondes |
| **Server Response Time** | Temps de réponse du serveur | < 500 ms |

### Configuration

Le module peut être configuré via des variables d'environnement dans le fichier `.env` :

```env
# Configuration de base
API_URL=http://localhost:8000/api
PERFORMANCE_MONITOR_PORT=8005

# Informations d'authentification Shopify
SHOPIFY_API_KEY=votre_api_key
SHOPIFY_API_SECRET=votre_api_secret
SHOPIFY_STORE_URL=votre-boutique.myshopify.com
SHOPIFY_ACCESS_TOKEN=votre_access_token

# Configuration des seuils (optionnel, valeurs par défaut fournies)
PERFORMANCE_PAGE_LOAD_THRESHOLD=3.0
PERFORMANCE_LCP_THRESHOLD=2.5
PERFORMANCE_CLS_THRESHOLD=0.1
PERFORMANCE_FID_THRESHOLD=0.1
PERFORMANCE_TTFB_THRESHOLD=0.6
```

## Price Monitor

[Documentation du module Price Monitor]

## A/B Testing

[Documentation du module A/B Testing]

## Product Rotation

[Documentation du module Product Rotation]

## SEO Optimization

[Documentation du module SEO Optimization]

## Intégration globale

L'agent Site Updater coordonne tous ces modules pour une optimisation holistique de votre boutique. Les modules partagent des données et des insights pour maximiser l'efficacité globale.

### Tableau de bord unifié

Vous pouvez accéder à un tableau de bord unifié pour surveiller et contrôler tous les aspects de l'agent Site Updater à l'adresse `http://localhost/dashboard/site-updater`.

### API centralisée

Tous les modules sont accessibles via l'API centralisée du système, en plus de leurs APIs individuelles :

```bash
curl -X GET http://localhost:8000/api/site-updater/status
```

### Automatisation et planification

Vous pouvez configurer des tâches automatisées pour tous les modules via l'interface de planification :

```bash
curl -X POST http://localhost:8000/api/scheduler/create \
  -H "Content-Type: application/json" \
  -d '{
    "module": "site-updater",
    "task": "performance_scan",
    "schedule": "0 0 * * *",
    "params": {"url": "https://votre-boutique.myshopify.com/"}
  }'
```

## Résolution des problèmes courants

Pour plus d'informations sur la résolution des problèmes, consultez la [documentation de dépannage](../troubleshooting.md).
