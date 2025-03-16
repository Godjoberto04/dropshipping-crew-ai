# Module d'Optimisation SEO

Ce module fait partie de l'agent Site Updater et permet l'optimisation continue des aspects SEO des sites e-commerce.

## Fonctionnalités

- **Analyse SEO des pages** : Analyse complète des éléments SEO d'une page web (méta-données, contenu, liens, images, etc.)
- **Recommandations d'amélioration** : Génération de recommandations spécifiques pour améliorer le référencement
- **Optimisation automatique** : Application des optimisations recommandées sur les pages ciblées
- **Génération de données structurées** : Création de schémas JSON-LD pour améliorer la visibilité dans les résultats de recherche
- **Extraction automatique de mots-clés** : Identification des mots-clés pertinents pour chaque page
- **Rapports SEO** : Génération de rapports d'analyse globaux pour identifier les opportunités d'amélioration

## Structure du module

- `seo_manager.py` : Classe principale gérant l'analyse et l'optimisation SEO
- `seo_utils.py` : Utilitaires pour l'extraction de mots-clés et la génération de données structurées
- `__init__.py` : Initialisation du module

## Intégration

Ce module est conçu pour fonctionner avec les autres composants de l'agent Site Updater :

- Utilise les données du module de tests A/B pour améliorer les pages les plus performantes
- S'appuie sur le module de suivi des prix pour optimiser les descriptions de produits
- Fournit des données au module de rotation des produits pour optimiser les produits mis en avant

## Utilisation

```python
from site-updater.seo_optimization import SEOOptimizationManager

# Initialiser le gestionnaire
seo_manager = SEOOptimizationManager()

# Analyser une page spécifique
analysis = await seo_manager.analyze_page_seo(
    url="https://example-shop.com/products/product-1",
    target_keywords=["chaussures", "running", "confort"]
)

# Optimiser les paramètres SEO
results = await seo_manager.optimize_seo_settings(
    target_pages=["https://example-shop.com/products/product-1"],
    keywords=["chaussures", "running", "confort"],
    focus_areas=["meta", "headings", "content"]
)

# Scanner toute la boutique
scan_results = await seo_manager.scan_shop_pages(
    shop_url="https://example-shop.com",
    max_pages=50
)
```

## Développement futur

- Intégration de l'API Claude pour générer du contenu optimisé SEO
- Analyse concurrentielle automatisée
- Support multilingue pour l'optimisation SEO
- Surveillance des changements d'algorithmes des moteurs de recherche
