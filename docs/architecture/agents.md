# Agents du système

Le système est composé de 5 agents spécialisés qui travaillent ensemble pour gérer entièrement une boutique de dropshipping.

## 1. Data Analyzer ✅

Agent chargé d'analyser le marché, d'identifier les produits à fort potentiel et de générer des rapports d'analyse.

### Fonctionnalités principales
- Analyse des tendances du marché via Google Trends et autres sources
- Détection des produits à fort potentiel commercial
- Évaluation de la concurrence et des opportunités de niche
- Analyse prédictive des performances futures des produits
- Système de scoring multicritères pour évaluer les produits
- Détection de saisonnalité pour optimiser les lancements
- Analyse de complémentarité pour maximiser la valeur du panier

### Modules clés
- **TrendsAnalyzer**: Analyse des tendances Google Trends avec détection avancée
- **MarketplaceAnalyzer**: Scraping et analyse des produits sur plateformes concurrentes
- **ScoringSystem**: Évaluation multicritère des produits avec pondération dynamique
- **ComplementaryAnalyzer**: Identification de produits complémentaires et création de bundles
- **CacheManager**: Système de cache optimisé pour réduire les requêtes API

### Architecture
L'agent Data Analyzer utilise une architecture modulaire Python avec des classes spécialisées, ayant migré d'une structure basée sur CrewAI/LangChain vers des classes Python standards pour une meilleure performance et stabilité.

### Interaction avec les autres agents
- Fournit des données au **Website Builder** pour la sélection des produits à mettre en avant
- Alimente le **Content Generator** avec des informations sur les tendances et les points forts à mettre en avant
- Guide l'**Order Manager** dans la sélection des produits à commander en priorité
- Fournit des données d'analyse au **Site Updater** pour l'optimisation du site

### État actuel et limitations
- ✅ Modules TrendsAnalyzer et ComplementaryAnalyzer entièrement fonctionnels
- ✅ Système de cache implémenté pour optimiser les performances
- ✅ Tests unitaires pour les principaux modules
- 🔄 Intégration avec SEMrush/Ahrefs en cours de développement
- 🔄 Module d'analyse des réseaux sociaux à améliorer

## 2. Website Builder ✅

Agent chargé de générer et maintenir le site e-commerce, en organisant les produits et en optimisant l'expérience utilisateur.

### Fonctionnalités principales
- Configuration et personnalisation du site Shopify
- Gestion de la structure du site et navigation
- Organisation des catégories et collections de produits
- Optimisation de l'expérience utilisateur et du tunnel de conversion
- Intégration des composants UI optimisés pour la conversion

### Modules clés
- **ShopifyManager**: Interface complète avec l'API Shopify
- **ThemeManager**: Gestion et personnalisation des thèmes
- **NavigationBuilder**: Construction de la navigation et menus
- **ProductOrganizer**: Organisation des produits en collections et catégories
- **SEOOptimizer**: Optimisation SEO technique des pages

### Architecture
L'agent Website Builder utilise une architecture orientée API avec une approche synchrone, s'interfaçant directement avec l'API Shopify et fournissant un ensemble d'opérations atomiques pour construire et maintenir le site.

### Interaction avec les autres agents
- Reçoit des données du **Data Analyzer** pour la structuration du catalogue
- Intègre le contenu créé par le **Content Generator**
- Communique avec l'**Order Manager** pour la mise à jour des stocks
- Reçoit des instructions du **Site Updater** pour les optimisations continues

### État actuel et limitations
- ✅ Configuration de base d'une boutique Shopify
- ✅ Gestion des thèmes et personnalisation
- ✅ Intégration API complète
- 🔄 Optimisation SEO à améliorer
- 🔄 A/B testing à implémenter
- 🔄 Tests unitaires à compléter

## 3. Content Generator ✅

Agent chargé de créer tout le contenu textuel du site, des descriptions produits aux articles de blog.

### Fonctionnalités principales
- Génération de descriptions de produits optimisées SEO
- Création de contenu marketing persuasif
- Optimisation des métadonnées pour le référencement
- Support pour différentes niches avec templates spécialisés
- Adaptation du ton et style selon le public cible

### Modules clés
- **ProductDescriptionGenerator**: Génération de descriptions produits
- **SEOOptimizer**: Optimisation du contenu pour le référencement
- **TemplateManager**: Gestion des templates par niche et type de contenu
- **ClaudeClient**: Interface avec l'API Claude pour la génération de contenu
- **APIClient**: Communication avec l'API centrale

### Architecture
L'agent Content Generator utilise une architecture asynchrone moderne basée sur FastAPI, permettant un traitement parallèle des requêtes de génération de contenu avec un système de file d'attente pour les tâches longues.

### Interaction avec les autres agents
- Reçoit des données du **Data Analyzer** sur les produits et tendances
- Fournit du contenu optimisé au **Website Builder** pour intégration
- Collabore avec l'**Order Manager** pour les descriptions de produits spécifiques
- Reçoit des demandes d'optimisation du **Site Updater** pour améliorer le contenu existant

### État actuel et limitations
- ✅ Génération de descriptions produits optimisées
- ✅ Support pour plusieurs niches (mode, électronique, maison, beauté)
- ✅ Tests unitaires complets
- 🔄 Génération d'articles de blog en développement
- 🔄 Optimisation SEO avancée à finaliser

## 4. Order Manager ✅

Agent chargé de gérer tout le cycle de vie des commandes, des fournisseurs aux clients.

### Fonctionnalités principales
- Gestion complète des commandes e-commerce
- Intégration avec les fournisseurs dropshipping (AliExpress, CJ Dropshipping)
- Synchronisation avec Shopify pour le traitement des commandes
- Suivi automatisé des expéditions
- Gestion des retours et problèmes clients
- Notifications personnalisées aux clients

### Modules clés
- **OrderService**: Service central de gestion des commandes
- **SupplierIntegrations**: Connecteurs pour les fournisseurs dropshipping
- **ShopifySync**: Synchronisation bidirectionnelle avec Shopify
- **TrackingManager**: Suivi des expéditions et mises à jour
- **NotificationSystem**: Alertes et notifications clients

### Architecture
L'agent Order Manager utilise une architecture API REST complète avec une base de données dédiée pour stocker l'historique des commandes et un système de file d'attente pour les opérations asynchrones.

### Interaction avec les autres agents
- Reçoit des informations sur les produits du **Data Analyzer**
- Se coordonne avec le **Website Builder** pour les mises à jour de stocks
- Utilise le contenu du **Content Generator** pour les communications clients
- Fournit des données de performance au **Site Updater** pour l'analyse des produits

### État actuel et limitations
- ✅ Intégration complète avec AliExpress et CJ Dropshipping
- ✅ Synchronisation Shopify fonctionnelle
- ✅ API REST complète pour la gestion des commandes
- ✅ Tests unitaires pour les intégrations fournisseurs
- 🔄 Intégration avec d'autres fournisseurs à développer
- 🔄 Dashboard dédié pour le suivi des commandes à améliorer

## 5. Site Updater 🔨

Agent chargé de maintenir et d'optimiser le site e-commerce en continu.

### Fonctionnalités principales
- Surveillance automatique des prix concurrents
- Ajustement dynamique des prix selon la demande et la concurrence
- Rotation intelligente des produits mis en avant
- Tests A/B automatisés pour optimiser les conversions
- Optimisation SEO continue des pages
- Analyse des performances du site et recommandations d'amélioration

### Modules clés
- **CompetitorTracker**: Surveillance des concurrents et analyse des prix
- **ProductRotator**: Rotation intelligente des produits en vitrine
- **ABTestManager**: Gestion des tests A/B et analyse des résultats
- **SEOOptimizationManager**: Optimisation continue du référencement

### Architecture
L'agent Site Updater utilise une architecture modulaire avec des services spécialisés qui s'exécutent périodiquement ou sont déclenchés par des événements spécifiques. Il s'appuie sur un système de règles configurables pour la prise de décision automatisée et utilise des algorithmes d'apprentissage pour optimiser les stratégies au fil du temps.

### Interaction avec les autres agents
- Reçoit des données d'analyse du **Data Analyzer** pour les décisions d'optimisation
- Envoie des commandes de mise à jour au **Website Builder**
- Demande des générations ou optimisations de contenu au **Content Generator**
- Analyse les données de vente de l'**Order Manager** pour évaluer les performances

### État actuel et limitations
- 🔨 Architecture de base en développement
- 🔨 Module CompetitorTracker en développement
- 🔨 Module ProductRotator en développement
- 🔨 Module ABTestManager en développement
- 🔨 Module SEOOptimizationManager en développement
- 🕐 Intégration complète avec les APIs Shopify à implémenter
- 🕐 Tests unitaires à développer
- 🕐 Interface utilisateur de contrôle à créer