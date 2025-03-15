# Agent Order Manager

Cet agent est responsable de la gestion complète des commandes pour le système de dropshipping autonome. Il offre une intégration native avec plusieurs fournisseurs dropshipping (AliExpress, CJ Dropshipping) et se synchronise avec Shopify pour un traitement automatisé des commandes.

## Fonctionnalités principales

- Gestion complète des commandes e-commerce
- Intégration avec les fournisseurs dropshipping (AliExpress, CJ Dropshipping)
- API REST complète pour la gestion des commandes
- Synchronisation avec Shopify
- Suivi des commandes et expéditions
- Gestion des notifications client

## Architecture

L'agent Order Manager utilise une architecture modulaire avec les composants suivants :

- **API** : Interface REST pour interagir avec l'agent
- **Modèles** : Représentation des données (commandes, fournisseurs, expéditions)
- **Services** : Logique métier pour le traitement des commandes
- **Intégrations** : Connecteurs pour Shopify et les fournisseurs dropshipping
- **Storage** : Couche d'accès aux données

## Intégrations

### Fournisseurs supportés

- **AliExpress** : Recherche de produits, création de commandes, suivi d'expédition
- **CJ Dropshipping** : Recherche de produits, création de commandes, suivi d'expédition

## Installation et configuration

Voir le fichier docker-compose.yml à la racine du projet et le .env.example pour les variables d'environnement nécessaires.

## Documentation détaillée

Pour plus d'informations sur l'utilisation de l'agent, consultez [Guide de l'agent Order Manager](../../docs/order-manager-guide.md).
