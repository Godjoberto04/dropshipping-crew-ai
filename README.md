# Dropshipping Crew AI

## Vue d'ensemble

Dropshipping Crew AI est un projet innovant qui vise à automatiser entièrement les opérations d'une boutique de dropshipping grâce à un système d'agents IA spécialisés qui travaillent ensemble via une architecture API centralisée. Chaque agent est responsable d'une fonction spécifique de la chaîne de valeur du dropshipping, de l'analyse de marché à la gestion des commandes.

## Architecture du système

Le système est composé de 5 agents principaux qui communiquent entre eux via une API REST centralisée:

1. **Data Analyzer**: Analyse les tendances du marché, identifie les produits prometteurs et évalue leur potentiel de rentabilité
2. **Website Builder**: Génère et optimise les sites e-commerce pour les produits sélectionnés
3. **Content Generator**: Crée du contenu marketing, descriptions produits et matériel promotionnel
4. **Order Manager**: Gère les commandes, le suivi et la logistique (en développement)
5. **Site Updater**: Maintient le site à jour avec de nouveaux produits et ajustements de prix (en développement)

### API Centralisée

L'API centralisée joue un rôle crucial en permettant:
- La communication entre les agents
- L'orchestration des workflows
- Le stockage et la gestion des données
- L'accès unifié aux fonctionnalités du système

## Agents

### Data Analyzer

L'agent Data Analyzer combine plusieurs sources de données et techniques d'analyse avancées pour:

- Analyser les tendances de recherche via Google Trends
- Évaluer le potentiel SEO des produits avec l'intégration Ahrefs
- Scraper les marketplaces concurrentes pour l'analyse de prix
- Prédire les performances futures avec des modèles de séries temporelles
- Identifier les anomalies et opportunités du marché
- Évaluer la complémentarité entre produits pour maximiser la valeur du panier

#### Module d'analyse de complémentarité

Le module d'analyse de complémentarité permet d'identifier les produits qui se vendent bien ensemble, optimisant ainsi les stratégies d'upsell et de cross-sell. Fonctionnalités principales:

- Algorithmes de recommandation basés sur les comportements d'achat
- Identification de patterns d'achat complémentaires
- Calcul des corrélations entre catégories de produits
- Suggestions pour la création de bundles et offres groupées
- API dédiée pour l'intégration avec les autres agents

### Website Builder

L'agent Website Builder génère automatiquement des sites e-commerce optimisés pour la conversion, comprenant:

- Création de pages produits optimisées pour le SEO
- Intégration d'éléments de confiance et preuves sociales
- Optimisation de l'expérience utilisateur et des tunnels d'achat
- Système de templates par niche de produits
- Performance optimisée pour tous les appareils
- Générateur de métadonnées SEO intelligent pour toutes les pages

#### Générateur de métadonnées SEO

Le générateur de métadonnées SEO est un nouveau composant qui crée automatiquement des balises meta optimisées pour le référencement:

- Génération de titres et descriptions personnalisés par page et produit
- Création de balises Open Graph pour une meilleure présence sur les réseaux sociaux
- Optimisation du balisage Schema.org pour les rich snippets dans les résultats de recherche
- Mots-clés spécifiques à la niche et adaptés à chaque produit
- Analyse concurrentielle pour améliorer le positionnement

### Content Generator

L'agent Content Generator crée tout le contenu textuel nécessaire:

- Descriptions de produits convaincantes
- Articles de blog optimisés pour le SEO
- Emails marketing et séquences de nurturing
- Textes publicitaires pour les campagnes marketing
- FAQ et pages d'information

## Infrastructure technique

Le système est construit sur une infrastructure moderne et évolutive:

- Backend: FastAPI, Python 3.9+
- Base de données: PostgreSQL, Redis (cache)
- Serveur: Scaleway DEV1-M
- Intégrations: APIs Claude, Shopify, et services tiers

## Statut du projet

Le projet est actuellement en développement actif. Les composants suivants sont fonctionnels:

- ✅ Data Analyzer: Version 1.0 complète avec analyses de tendances et prédictions
- ✅ Website Builder: Version 1.0 avec génération de sites e-commerce
- 🔄 Content Generator: En développement, version alpha disponible
- 📅 Order Manager: Planifié pour le prochain trimestre
- 📅 Site Updater: Planifié pour le prochain trimestre

## Documentation

Une documentation détaillée est disponible pour chaque agent:

- [Guide d'utilisation du Data Analyzer](docs/data_analyzer_guide.md)
- [Documentation technique du Website Builder](docs/website_builder_technical.md)
- [Guide des API](docs/api_reference.md)

## Contribuer

Les contributions sont les bienvenues! Pour contribuer:

1. Forkez le repository
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add some amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
