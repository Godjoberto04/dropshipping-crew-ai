# Agent Website Builder

L'agent Website Builder est responsable de la création et de la gestion de sites e-commerce optimisés pour le dropshipping. Il interagit avec l'API Shopify pour configurer et personnaliser la boutique selon les besoins spécifiques du projet.

## Fonctionnalités principales

- Configuration complète d'une boutique Shopify
- Personnalisation de thèmes et de designs
- Gestion de la navigation du site
- Ajout et gestion de produits
- Optimisation SEO automatisée pour toutes les pages

## Architecture

L'agent Website Builder est structuré autour des composants suivants :

- **main.py** : Point d'entrée principal et gestionnaire de tâches
- **tools/** : Modules spécialisés pour différentes fonctionnalités
  - **api_client.py** : Client pour l'API centrale du projet
  - **shopify_api.py** : Intégration avec l'API Shopify
  - **theme_manager.py** : Gestionnaire de thèmes et personnalisation visuelle
  - **store_setup.py** : Configuration initiale de la boutique
  - **navigation.py** : Gestion de la structure de navigation
  - **seo_generator.py** : Générateur intelligent de métadonnées SEO
- **tests/** : Tests unitaires pour les différentes fonctionnalités

## Génération de métadonnées SEO

L'une des fonctionnalités clés de l'agent Website Builder est la génération automatique de métadonnées SEO optimisées. Le module `seo_generator.py` génère intelligemment :

- Titres et méta-descriptions optimisés pour le SEO
- Données structurées schema.org adaptées au type de contenu
- Balises Open Graph pour le partage sur les réseaux sociaux
- Balises Twitter Card pour l'affichage sur Twitter
- Mots-clés pertinents basés sur la niche et le contenu

Le générateur prend en compte le type de page (produit, collection, page statique, article de blog) et adapte les métadonnées en conséquence. Il utilise également des déclencheurs émotionnels spécifiques à la niche pour rendre les titres et descriptions plus attrayants.

### Utilisation du générateur SEO

```python
from tools.seo_generator import SEOMetaGenerator

# Initialiser le générateur avec une configuration personnalisée
seo_generator = SEOMetaGenerator(config={
    'shop_name': 'Ma Boutique',
    'maxTitleLength': 60,
    'maxDescriptionLength': 160,
    'includeEmotionalTriggers': True
})

# Informations sur la boutique
shop_info = {
    'name': 'Ma Boutique',
    'domain': 'ma-boutique.myshopify.com'
}

# Données d'un produit
product_data = {
    'type': 'product',
    'name': 'Montre Connectée',
    'description': 'Une montre intelligente avec suivi d\'activité.',
    'price': 99.99,
    'currency': 'EUR',
    'images': ['https://example.com/montre.jpg'],
    'features': ['Écran tactile', 'Étanche', 'Batterie longue durée']
}

# Générer les métadonnées SEO
metadata = seo_generator.generate_metadata(
    page_data=product_data,
    shop_info=shop_info,
    niche='electronics'
)

# Utiliser les métadonnées générées
print(f"Titre SEO: {metadata['title']}")
print(f"Description: {metadata['description']}")
print(f"URL canonique: {metadata['canonical']}")
```

## Tests

Pour exécuter les tests unitaires pour l'agent Website Builder, utilisez la commande suivante :

```bash
cd services/website-builder
python -m unittest discover -s tests
```

Pour exécuter uniquement les tests du générateur SEO :

```bash
python -m unittest tests.test_seo_generator
```

## Intégration avec l'API centrale

L'agent Website Builder communique avec les autres agents via l'API centrale. Il peut :

1. Récupérer les tâches en attente
2. Mettre à jour le statut des tâches
3. Signaler son statut et ses capacités
4. Envoyer les résultats des opérations effectuées

Pour plus d'informations sur l'API centrale, consultez la documentation dans le dossier `services/api`.
