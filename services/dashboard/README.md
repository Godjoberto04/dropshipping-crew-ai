# Dashboard pour Dropshipping Crew AI

## Vue d'ensemble

Ce dashboard est une interface utilisateur complète pour gérer et surveiller le système Dropshipping Crew AI. Il permet de visualiser l'état des différents agents, lancer des analyses de marché, configurer la boutique et générer du contenu optimisé pour le SEO.

## Fonctionnalités

### 1. Vue d'ensemble du système
- Affichage en temps réel du statut de tous les services
- Métriques clés du projet (produits analysés, produits en boutique, commandes, chiffre d'affaires)
- Performances du serveur (CPU, mémoire, disque)
- Statut détaillé des agents IA

### 2. Gestion des agents
- **Data Analyzer** : Analyse de marché et identification des produits à fort potentiel
- **Website Builder** : Configuration et personnalisation de la boutique Shopify
- **Content Generator** : Création de descriptions de produits optimisées pour le SEO
- Statut et suivi des agents en développement (Order Manager, Site Updater)

### 3. Orchestration
- Vue d'ensemble de l'architecture d'orchestration API
- Visualisation des workflows entre agents
- Suivi des tâches en cours

## Structure du code

Le dashboard est composé de trois fichiers JavaScript principaux :

- `dashboard.js` : Fonctions de base pour l'initialisation du dashboard et la mise à jour des informations système
- `dashboard_part2.js` : Fonctions pour les agents, métriques et gestion des actions utilisateur
- `dashboard_part3.js` : Fonctions utilitaires pour les simulations et affichages spécifiques

Cette séparation permet une meilleure organisation du code et facilite la maintenance.

## Mise à jour du 12 mars 2025

Cette mise à jour majeure du dashboard reflète les dernières avancées du projet :

- Ajout d'une nouvelle section pour l'agent Content Generator désormais implémenté
- Mise à jour du statut des agents pour refléter l'état actuel du projet
- Ajout d'une section Orchestration pour visualiser les workflows entre agents
- Amélioration visuelle et UX du dashboard
- Affichage des métriques actualisées

## Comment utiliser les fichiers JavaScript

Pour utiliser les trois fichiers JavaScript, ajoutez les balises script suivantes à votre HTML :

```html
<script src="js/dashboard.js"></script>
<script src="js/dashboard_part2.js"></script>
<script src="js/dashboard_part3.js"></script>
```

Ou mettez à jour le fichier index.html pour charger ces trois fichiers au lieu d'un seul.

## Captures d'écran

*Des captures d'écran seront ajoutées ici une fois que le dashboard sera déployé sur le serveur.*

## Prochaines étapes

- **Intégration complète du moteur de workflow** : Mise en place des flux de travail automatisés entre agents
- **Tableau de bord d'orchestration avancé** : Visualisation et contrôle des workflows en temps réel
- **Système d'alerte** : Notification en cas d'erreurs ou d'opportunités détectées
- **Interface pour les agents en développement** : Préparation des interfaces pour Order Manager et Site Updater