# Dropshipping Autonome avec Crew AI

> **🔔 MISE À JOUR: Développement de la page ContentGenerator pour le Dashboard Centralisé**  
> Une interface complète pour la génération de contenu optimisé SEO a été développée pour le Dashboard Centralisé. Les utilisateurs peuvent désormais générer des descriptions de produits, sélectionner des templates et visualiser les métadonnées SEO via une interface intuitive. Voir la [dernière mise à jour](docs/updates/2025-03-28.md) pour plus de détails.

> **✅ MISE À JOUR PRÉCÉDENTE: Développement de la page WebsiteBuilder pour le Dashboard Centralisé**  
> Une interface complète pour la gestion des sites Shopify a été développée pour le Dashboard Centralisé. Les utilisateurs peuvent désormais gérer les thèmes, collections, pages et paramètres de leur boutique via une interface intuitive et réactive. Voir la [mise à jour du 21 mars](docs/updates/2025-03-21.md) pour plus de détails.

Système autonome de dropshipping géré par une flotte d'agents d'IA utilisant Crew AI.

## 🔍 Vue d'ensemble

Système entièrement autonome pour gérer une boutique de dropshipping en exploitant les capacités de Claude et des agents IA. Le système est composé de 5 agents spécialisés qui travaillent ensemble pour analyser le marché, créer et gérer une boutique Shopify, générer du contenu optimisé SEO, gérer les commandes et maintenir le site à jour. Un dashboard centralisé est en cours de développement pour faciliter le pilotage de l'ensemble du système.

## 🚀 Déploiement actuel

- **Serveur**: Scaleway DEV1-M (Paris)
- **IP**: 163.172.160.102
- **API**: http://163.172.160.102/api/
- **Dashboard**: http://163.172.160.102/
- **Statut actuel**: 
  - ✅ Agent Data Analyzer: Opérationnel
  - ✅ Agent Website Builder: Opérationnel
  - ✅ Agent Content Generator: Opérationnel
  - ✅ Agent Order Manager: Opérationnel
  - ✅ Agent Site Updater: Opérationnel (5/5 modules)
    - ✅ Price Monitor: Opérationnel
    - ✅ A/B Testing: Opérationnel
    - ✅ Product Rotation: Opérationnel
    - ✅ SEO Optimization: Opérationnel
    - ✅ Performance Monitor: Opérationnel
  - 🔨 Dashboard Centralisé: En développement actif
    - ✅ Vue d'ensemble: Opérationnel
    - ✅ Data Analyzer: Opérationnel 
    - ✅ Website Builder: Opérationnel
    - ✅ Content Generator: Opérationnel
    - 🔨 Order Manager: En développement
    - 🔨 Site Updater: En développement
    - ✅ Paramètres: Opérationnel

## 📊 Architecture du système

- [Présentation détaillée des agents](docs/architecture/agents.md)
- [Infrastructure technique](docs/architecture/infrastructure.md)
- [Architecture d'API centralisée](docs/architecture/api.md)
- [Structure du projet](docs/architecture/structure.md)

## 📝 Mises à jour

- [Mars 28, 2025 🔔](docs/updates/2025-03-28.md) - Développement de la page ContentGenerator pour le Dashboard Centralisé
- [Mars 21, 2025](docs/updates/2025-03-21.md) - Développement de la page WebsiteBuilder pour le Dashboard Centralisé
- [Mars 20, 2025](docs/updates/2025-03-20.md) - Développement actif du Dashboard Centralisé
- [Mars 19, 2025](docs/updates/2025-03-19.md) - Implémentation complète du module Performance Monitor pour l'agent Site Updater
- [Mars 18, 2025](docs/updates/2025-03-18.md) - Implémentation du module SEO Optimization pour l'agent Site Updater
- [Toutes les mises à jour](docs/updates/index.md)

## 💻 Installation et déploiement

- [Prérequis](docs/setup/prerequisites.md)
- [Guide d'installation](docs/setup/installation.md)

## 🔧 Utilisation des agents

- [Agent Data Analyzer](docs/usage/data-analyzer.md)
- [Agent Website Builder](docs/usage/website-builder.md)
- [Agent Content Generator](docs/usage/content-generator.md)
- [Agent Order Manager](docs/usage/order-manager.md)
- [Agent Site Updater](docs/usage/site-updater.md)

## 🔬 Tests unitaires

- [Tests et couverture](docs/testing/overview.md)

## 📈 Plans d'amélioration

- [Points d'amélioration identifiés](docs/roadmap/improvement-points.md)
- [Prochaines étapes](docs/roadmap/next-steps.md)
- [Plan de développement du Dashboard](docs/roadmap/dashboard-development-plan.md)

## 📋 Documentation complémentaire

- [Guide complet de la documentation](docs/index.md)

## 💰 Coûts du projet

- [Détail des coûts](docs/costs.md)

## ❓ Dépannage

- [Guide de dépannage](docs/troubleshooting.md)

## 📧 Contact et support

Ce projet est développé par un passionné d'IA autonome. Pour toute question ou suggestion, ouvrez une issue sur ce dépôt ou contactez le propriétaire.

## 📜 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
