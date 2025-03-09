# Guide d'utilisation des agents Crew AI

Ce guide détaille comment utiliser efficacement les agents Crew AI dans notre projet de dropshipping autonome. Il couvre la configuration, l'exécution et l'optimisation des différents agents.

## Introduction à Crew AI

[Crew AI](https://github.com/joaomdmoura/crewAI) est un framework open-source qui permet de créer des équipes d'agents d'IA autonomes qui collaborent pour accomplir des tâches complexes. Dans notre projet, nous utilisons Crew AI avec l'API Claude pour créer une flotte d'agents spécialisés gérant différents aspects d'une boutique de dropshipping.

## Configuration de base pour tous les agents

### Prérequis

1. Installer les dépendances
```bash
pip install crewai anthropic pandas requests beautifulsoup4
```

2. Configurer l'API Claude
```python
import os
os.environ["ANTHROPIC_API_KEY"] = "votre_clé_api_claude"
```

### Structure d'un agent Crew AI

Chaque agent dans Crew AI se compose de ces éléments essentiels :

1. **Rôle** : Définit la fonction de l'agent (ex: "Expert en Analyse de Marché")
2. **Goal (Objectif)** : Définit ce que l'agent doit accomplir
3. **Backstory (Histoire)** : Donne du contexte et de la personnalité à l'agent
4. **Tools (Outils)** : Capacités spécifiques données à l'agent pour accomplir ses tâches
5. **Allow_delegation** : Indique si l'agent peut déléguer des tâches à d'autres agents

Exemple de définition d'agent :
```python
from crewai import Agent

data_analyzer = Agent(
    role="Expert en Analyse de Marché",
    goal="Identifier les produits tendance avec une marge potentielle de 30%+",
    backstory="Vous êtes un analyste de marché chevronné avec 15 ans d'expérience...",
    verbose=True,
    allow_delegation=False,
    tools=[WebScrapingTool(), ProductAnalysisTool(), TrendIdentificationTool()]
)
```

## Les agents du système

### 1. Data Analyzer

**Objectif** : Analyser le marché pour identifier les produits à fort potentiel pour le dropshipping.

**Outils** :
- `WebScrapingTool` : Scrape les sites e-commerce pour collecter des données produits
- `ProductAnalysisTool` : Analyse la rentabilité et le potentiel des produits
- `TrendIdentificationTool` : Identifie les tendances actuelles du marché

**Exécution** :
```python
def run_market_analysis(competitor_urls, market_segment=None):
    # Définition de l'agent et des tâches
    data_analyzer = Agent(...)
    analyze_task = Task(...)
    
    # Création du crew
    market_crew = Crew(
        agents=[data_analyzer],
        tasks=[analyze_task],
        verbose=2,
        process=Process.sequential
    )
    
    # Exécution de l'analyse
    result = market_crew.kickoff(
        inputs={
            "competitor_urls": competitor_urls,
            "market_segment": market_segment
        }
    )
    
    return result
```

**Optimisation des prompts** :

Pour obtenir les meilleurs résultats, utilisez des prompts spécifiques qui :
1. Définissent clairement les critères de sélection des produits (marge, tendance, concurrence)
2. Spécifient le format exact de sortie (JSON structuré)
3. Précisent le niveau de détail attendu

### 2. Website Builder

**Objectif** : Créer et configurer une boutique Shopify optimisée pour les conversions.

**Outils** :
- `ShopifyAPITool` : Interagit avec l'API Shopify pour gérer la boutique
- `ThemeOptimizationTool` : Personnalise et optimise le thème Shopify
- `StoreStructureTool` : Configure la structure et la navigation du site

**Exécution** :
```python
def setup_shopify_store(shop_name, product_category, theme_preference=None):
    # Définition de l'agent et des tâches
    website_builder = Agent(...)
    setup_task = Task(...)
    
    # Création du crew
    website_crew = Crew(
        agents=[website_builder],
        tasks=[setup_task],
        verbose=2
    )
    
    # Exécution de la configuration
    result = website_crew.kickoff(
        inputs={
            "shop_name": shop_name,
            "product_category": product_category,
            "theme_preference": theme_preference
        }
    )
    
    return result
```

### 3. Content Generator

**Objectif** : Générer du contenu optimisé SEO pour les produits et le site.

**Outils** :
- `SEOKeywordTool` : Recherche et analyse les mots-clés pertinents
- `ContentGenerationTool` : Génère les descriptions et contenus
- `MetaTagOptimizationTool` : Optimise les balises meta pour le SEO

**Exécution** :
```python
def generate_product_content(product_data, seo_keywords=None):
    # Définition de l'agent et des tâches
    content_generator = Agent(...)
    content_task = Task(...)
    
    # Création du crew
    content_crew = Crew(
        agents=[content_generator],
        tasks=[content_task]
    )
    
    # Exécution de la génération
    result = content_crew.kickoff(
        inputs={
            "product_data": product_data,
            "seo_keywords": seo_keywords
        }
    )
    
    return result
```

### 4. Order Manager

**Objectif** : Gérer les commandes et les relations avec les fournisseurs.

**Outils** :
- `OrderProcessingTool` : Traite les commandes entrantes
- `SupplierCommunicationTool` : Communique avec les fournisseurs
- `CustomerNotificationTool` : Envoie des notifications aux clients

### 5. Site Updater

**Objectif** : Maintenir le site à jour (prix, stocks, contenus).

**Outils** :
- `PriceMonitoringTool` : Surveille les prix des concurrents
- `InventoryUpdateTool` : Met à jour les niveaux de stock
- `CompetitorTrackingTool` : Suit les actions des concurrents

## Workflow entre agents

Pour une collaboration efficace entre agents, vous pouvez créer un workflow :

```python
from crewai import Crew, Process

# Créer les agents
data_analyzer = Agent(...)
website_builder = Agent(...)
content_generator = Agent(...)

# Créer les tâches
analyze_task = Task(...)
website_task = Task(...)
content_task = Task(...)

# Créer le crew avec tous les agents et tâches
dropshipping_crew = Crew(
    agents=[data_analyzer, website_builder, content_generator],
    tasks=[analyze_task, website_task, content_task],
    verbose=2,
    process=Process.sequential  # Les tâches s'exécutent dans l'ordre défini
)

# Exécuter le workflow complet
result = dropshipping_crew.kickoff()
```

## Techniques avancées

### 1. Mémoire partagée

Pour permettre aux agents de partager des informations :

```python
from crewai.memory import PostgresMemory

# Configuration de la mémoire
shared_memory = PostgresMemory(
    connection_string="postgresql://user:password@postgres:5432/dbname",
    table_name="agent_memory"
)

# Utilisation dans les agents
agent = Agent(
    memory=shared_memory,
    # autres paramètres...
)
```

### 2. Parallel Processing

Pour exécuter des tâches en parallèle :

```python
# Configurer le crew avec parallel processing
crew = Crew(
    agents=[agent1, agent2, agent3],
    tasks=[task1, task2, task3],
    process=Process.parallel  # Exécute les tâches en parallèle
)
```

### 3. Feedback Loops

Pour créer des boucles de rétroaction :

```python
# Tâche avec rétroaction
feedback_task = Task(
    description="Évaluer et améliorer l'analyse",
    expected_output="Analyse révisée",
    agent=data_analyzer,
    human_input=True  # Permettre l'input humain pour le feedback
)
```

## Bonnes pratiques

1. **Définitions précises** : Définissez clairement le rôle, l'objectif et le contexte de chaque agent
2. **Instructions détaillées** : Fournissez des instructions précises dans les prompts
3. **Format de sortie** : Spécifiez toujours le format de sortie attendu (JSON, texte structuré, etc.)
4. **Logging** : Utilisez `verbose=True` pour le debugging et l'analyse
5. **Gestion des erreurs** : Implémentez une gestion robuste des erreurs pour les outils
6. **Monitoring** : Surveillez les performances des agents et ajustez les prompts au besoin

## Dépannage

### Problèmes courants et solutions

1. **L'agent ne comprend pas la tâche**
   - Solution : Améliorez la clarté des instructions et du contexte

2. **Résultats incohérents**
   - Solution : Standardisez les formats de sortie et utilisez des exemples

3. **L'agent dépasse les limites de tokens**
   - Solution : Divisez les tâches complexes en sous-tâches plus petites

4. **Communication inter-agents défaillante**
   - Solution : Utilisez la mémoire partagée et des formats d'entrée/sortie standardisés

## Exemples de code

### Exemple complet d'un agent Data Analyzer

```python
import os
from crewai import Agent, Task, Crew, Process
from tools.scraping import WebScrapingTool
from tools.product_analysis import ProductAnalysisTool
from tools.trend_identification import TrendIdentificationTool

# Configuration de l'API Claude
os.environ["ANTHROPIC_API_KEY"] = "votre_clé_api_claude"

# Création des outils
web_scraping_tool = WebScrapingTool()
product_analysis_tool = ProductAnalysisTool()
trend_identification_tool = TrendIdentificationTool()

# Définition de l'agent
data_analyzer = Agent(
    role="Expert en Analyse de Marché et de Concurrence",
    goal="Identifier les produits tendance avec une marge potentielle de 30%+ et une faible concurrence",
    backstory="""Vous êtes un analyste de marché chevronné avec 15 ans d'expérience dans l'identification 
    des tendances e-commerce et des opportunités de dropshipping. Votre réputation repose sur votre 
    capacité à trouver des produits à fort potentiel avant qu'ils ne deviennent mainstream.""",
    verbose=True,
    allow_delegation=False,
    tools=[web_scraping_tool, product_analysis_tool, trend_identification_tool]
)

# Définition de la tâche
analyze_products_task = Task(
    description="""Analyser les sites web de concurrents pour identifier les produits à fort potentiel 
    pour le dropshipping. Focus sur les produits avec une marge potentielle >30%, une tendance 
    à la hausse et une concurrence modérée.""",
    expected_output="""Un rapport d'analyse détaillé au format JSON listant les 10 produits les plus 
    prometteurs avec leur nom, prix fournisseur, prix recommandé, marge potentielle, niveau de 
    concurrence, direction de la tendance et justification.""",
    agent=data_analyzer,
    context=[
        "Extraire les données de produits des sites concurrents",
        "Analyser la rentabilité potentielle de chaque produit",
        "Évaluer le niveau de concurrence pour chaque produit",
        "Identifier les tendances actuelles du marché",
        "Sélectionner les 10 meilleurs produits selon les critères définis"
    ]
)

# Création du crew
market_analysis_crew = Crew(
    agents=[data_analyzer],
    tasks=[analyze_products_task],
    verbose=2,
    process=Process.sequential
)

# Exécution de l'analyse
competitor_urls = [
    "https://example-shop.com/category/accessories",
    "https://another-shop.com/bestsellers"
]

result = market_analysis_crew.kickoff(
    inputs={
        "competitor_urls": competitor_urls,
        "market_segment": "smartphone accessories",
        "min_margin": 30
    }
)

print(result)
```

Ce guide vous aidera à tirer le meilleur parti des agents Crew AI dans votre projet de dropshipping autonome. N'hésitez pas à ajuster et expérimenter avec les différentes configurations pour optimiser les performances des agents.