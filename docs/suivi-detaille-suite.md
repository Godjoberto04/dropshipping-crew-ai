# Suite du document de suivi détaillé

## Techniques d'optimisation spécifiques à Crew AI (suite)

### 1. Optimisation des prompts (suite)

Pour maximiser l'efficacité des agents, nous utiliserons des techniques avancées de prompt engineering :

```python
# Exemple de prompt optimisé pour Data Analyzer
data_analyzer_prompt = """
Vous êtes un analyste de marché expert en dropshipping avec 15 ans d'expérience. Votre objectif est d'identifier les produits à fort potentiel sur le marché.

Tâche: Analyser les données extraites de {site_url} pour identifier les produits avec:
1. Marge potentielle d'au moins 30%
2. Tendance à la hausse dans les recherches
3. Concurrence modérée
4. Facilité de livraison (petit, léger)

Suivez ce processus d'analyse:
1. Examinez d'abord les prix et calculez les marges potentielles
2. Évaluez le niveau de concurrence pour chaque produit
3. Identifiez les produits qui correspondent à tous les critères
4. Présentez les 5 meilleurs produits avec justification

Format de sortie JSON requis:
{
  "top_products": [
    {
      "name": "Nom du produit",
      "supplier_price": 0.00,
      "recommended_price": 0.00,
      "potential_margin_percent": 00,
      "competition_level": "Low/Medium/High",
      "trend_direction": "Up/Stable/Down",
      "recommendation_score": 0.0,
      "justification": "Explication détaillée"
    }
  ]
}

Important: Assurez-vous que votre analyse est factuelle et basée uniquement sur les données fournies.
"""
```

### 2. Système de mémoire optimisée

Implémentation d'un système de mémoire efficace pour les agents:

```python
from crewai.memory import PostgresMemory
import os

# Configuration de la mémoire PostgreSQL pour les agents
postgres_memory = PostgresMemory(
    connection_string=f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@postgres:5432/{os.getenv('POSTGRES_DB')}",
    table_name="crew_agent_memory",
    ttl=30  # Durée de vie en jours
)

# Utilisation avec les agents
data_analyzer = Agent(
    role="Expert en Analyse de Marché",
    goal="Identifier les produits tendance avec une marge potentielle de 30%+",
    backstory="Vous êtes un analyste de marché chevronné...",
    memory=postgres_memory,
    tools=[WebScrapingTool(), ProductAnalysisTool(), TrendIdentificationTool()]
)
```

### 3. Workflow optimisé avec tasks

Configuration des tâches structurées pour maximiser l'efficacité:

```python
from crewai import Task, Crew

# Définition de tâches structurées
analyze_market_task = Task(
    description="Analyser le marché pour identifier les produits à fort potentiel",
    expected_output="Liste des 10 produits les plus prometteurs au format JSON",
    agent=data_analyzer,
    context=[
        "Focus sur les produits avec marge >30%",
        "Privilégier les produits avec tendance à la hausse",
        "Éviter les produits trop volumineux ou lourds"
    ],
    output_file="market_analysis_results.json"
)

# Configuration du workflow avec boucle de feedback
feedback_task = Task(
    description="Évaluer et améliorer l'analyse de marché",
    expected_output="Analyse révisée avec recommandations améliorées",
    agent=data_analyzer,
    context=["Utiliser les résultats précédents pour affiner l'analyse"],
    async_execution=False,  # Exécution synchrone pour permettre le feedback
    human_input=True  # Permettre l'input humain pour le feedback
)

# Création d'un crew avec les tâches
market_analysis_crew = Crew(
    agents=[data_analyzer],
    tasks=[analyze_market_task, feedback_task],
    verbose=2,  # Niveau de détail des logs
    process=Process.sequential  # Exécution séquentielle des tâches
)

# Exécution du crew
result = market_analysis_crew.kickoff(
    inputs={
        "competitor_urls": ["https://competitor1.com", "https://competitor2.com"],
        "market_segment": "accessories",
        "min_margin": 30
    }
)
```

## Modifications nécessaires à l'infrastructure existante

Pour adapter l'infrastructure actuelle à notre nouvelle approche, les modifications suivantes sont requises:

### 1. Installation et configuration de Nginx

```bash
# Installer Nginx
sudo apt update
sudo apt install -y nginx

# Configurer Nginx pour le dashboard et l'API
sudo nano /etc/nginx/sites-available/dropship-dashboard

# Contenu du fichier:
server {
    listen 80;
    server_name 163.172.160.102;  # Remplacer par votre nom de domaine si vous en avez un

    # Journalisation
    access_log /var/log/nginx/dropship.access.log;
    error_log /var/log/nginx/dropship.error.log;

    # Racine pour les fichiers statiques du dashboard
    root /var/www/html/dashboard;
    index index.html;

    # Configuration pour servir le dashboard
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Configuration pour le proxy vers l'API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Activer la configuration
sudo ln -s /etc/nginx/sites-available/dropship-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Créer le répertoire pour le dashboard
sudo mkdir -p /var/www/html/dashboard
```

### 2. Adaptation de l'API FastAPI existante

Modification du fichier `/opt/dropship-crew-ai/services/api/app/main.py` pour optimiser l'API :

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import os
import json
from datetime import datetime

app = FastAPI(title="Dropshipping Crew AI API")

# Configurer CORS pour permettre les requêtes depuis le dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines exactes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles de données
class ProductAnalysis(BaseModel):
    name: str
    supplier_price: float
    recommended_price: float
    potential_margin_percent: float
    competition_level: str
    trend_direction: str
    recommendation_score: float
    justification: str

class AnalysisResults(BaseModel):
    top_products: List[ProductAnalysis]
    analysis_date: datetime
    source_urls: List[str]

@app.get("/")
def read_root():
    """Endpoint racine de l'API"""
    return {
        "message": "Bienvenue sur l'API du projet Dropshipping Autonome avec Crew AI",
        "version": "1.0.0",
        "status": "online"
    }

@app.get("/status")
def get_status():
    """Renvoie le statut des différents services du système"""
    # Dans une implémentation réelle, vous interrogeriez les services
    # Ici, nous renvoyons des données simulées
    return {
        "services": {
            "postgres": {"status": "online", "version": "14"},
            "redis": {"status": "online", "version": "7"},
            "api": {"status": "online", "version": "1.0.0"},
            "data_analyzer": {"status": "partial", "version": "0.1.0"},
            "website_builder": {"status": "offline", "version": None},
            "content_generator": {"status": "offline", "version": None},
            "order_manager": {"status": "offline", "version": None},
            "site_updater": {"status": "offline", "version": None}
        },
        "system": {
            "server": "Scaleway DEV1-M",
            "cpu_usage": 15.2,  # pourcentage simulé
            "memory_usage": 32.1,  # pourcentage simulé
            "disk_usage": 23.8   # pourcentage simulé
        }
    }

@app.get("/agents/data-analyzer/status")
def get_data_analyzer_status():
    """Renvoie le statut de l'agent Data Analyzer"""
    return {
        "status": "partial",
        "version": "0.1.0",
        "last_run": datetime.now().isoformat(),
        "capabilities": [
            "Website scraping",
            "Product analysis"
        ],
        "pending_capabilities": [
            "Trend analysis",
            "Competition assessment"
        ]
    }

@app.post("/agents/data-analyzer/analyze")
async def trigger_analysis(urls: List[str]):
    """Déclenche une analyse de marché sur les URLs spécifiées"""
    if not urls or len(urls) == 0:
        raise HTTPException(status_code=400, detail="Au moins une URL est requise")
        
    # Dans une implémentation réelle, vous déclencheriez l'agent ici
    # Pour l'instant, nous simulons une réponse
    return {
        "task_id": "task_123456",
        "status": "queued",
        "message": f"Analyse démarrée sur {len(urls)} URLs",
        "estimated_completion": (datetime.now().timestamp() + 300)  # +5 minutes
    }

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Récupère le statut d'une tâche en cours"""
    # Simulation de statut de tâche
    return {
        "task_id": task_id,
        "status": "in_progress",
        "progress": 65,  # pourcentage
        "message": "Analyse des produits en cours",
        "started_at": (datetime.now().timestamp() - 150),  # -2.5 minutes
        "estimated_completion": (datetime.now().timestamp() + 150)  # +2.5 minutes
    }

@app.get("/analysis/results/latest")
async def get_latest_analysis():
    """Récupère les résultats de la dernière analyse"""
    # Simuler des résultats d'analyse
    return {
        "analysis_id": "analysis_789012",
        "created_at": datetime.now().isoformat(),
        "source_urls": ["https://example-shop.com/category/accessories"],
        "top_products": [
            {
                "name": "Housse de protection smartphone premium",
                "supplier_price": 3.50,
                "recommended_price": 15.99,
                "potential_margin_percent": 78.1,
                "competition_level": "Medium",
                "trend_direction": "Up",
                "recommendation_score": 8.7,
                "justification": "Forte marge, tendance à la hausse et concurrence modérée"
            },
            {
                "name": "Chargeur sans fil 15W",
                "supplier_price": 7.20,
                "recommended_price": 24.99,
                "potential_margin_percent": 71.2,
                "competition_level": "Medium",
                "trend_direction": "Up",
                "recommendation_score": 8.4,
                "justification": "Produit tendance avec bonne marge et facilité d'expédition"
            }
            # Plus de produits seraient inclus dans une implémentation réelle
        ]
    }

# Points de terminaison supplémentaires à implémenter pour les autres agents...
```

### 3. Modification de l'agent Data Analyzer

Mettre à jour le fichier `/opt/dropship-crew-ai/services/crew-ai/main.py` :

```python
import os
import json
import time
from typing import Dict, List, Any
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from tools.scraping import WebScrapingTool
from tools.product_analysis import ProductAnalysisTool
from tools.trend_identification import TrendIdentificationTool

# Charger les variables d'environnement
load_dotenv()

# Configuration de l'API key Claude
os.environ["ANTHROPIC_API_KEY"] = os.getenv("CLAUDE_API_KEY")

# Création des outils
web_scraping_tool = WebScrapingTool()
product_analysis_tool = ProductAnalysisTool()
trend_identification_tool = TrendIdentificationTool()

# Définition de l'agent Data Analyzer
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

# Définition des tâches
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

# Fonction pour exécuter l'analyse de marché
def run_market_analysis(competitor_urls: List[str], market_segment: str = None):
    """
    Exécute une analyse de marché en utilisant l'agent Data Analyzer
    
    Args:
        competitor_urls: Liste des URLs de sites concurrents à analyser
        market_segment: Segment de marché à cibler (optionnel)
        
    Returns:
        Résultats de l'analyse au format JSON
    """
    # Création du crew avec l'agent Data Analyzer
    market_analysis_crew = Crew(
        agents=[data_analyzer],
        tasks=[analyze_products_task],
        verbose=2,
        process=Process.sequential
    )
    
    # Configuration des inputs pour l'analyse
    inputs = {
        "competitor_urls": competitor_urls,
        "min_margin": 30
    }
    
    if market_segment:
        inputs["market_segment"] = market_segment
    
    # Exécution de l'analyse
    print(f"Démarrage de l'analyse sur {len(competitor_urls)} URLs...")
    result = market_analysis_crew.kickoff(inputs=inputs)
    
    # Traitement et retour des résultats
    try:
        # Tentative de parsing des résultats en JSON
        results_json = json.loads(result)
        return results_json
    except json.JSONDecodeError:
        # Si le résultat n'est pas du JSON valide, retourne un format standard
        return {
            "error": "Impossible de parser les résultats en JSON",
            "raw_result": result
        }

# Fonction principale pour les tests en ligne de commande
if __name__ == "__main__":
    # URLs de test
    test_urls = [
        "https://example-shop.com/category/accessories",
        "https://another-shop.com/bestsellers"
    ]
    
    # Exécution de l'analyse
    analysis_results = run_market_analysis(test_urls, "smartphone accessories")
    
    # Affichage des résultats
    print(json.dumps(analysis_results, indent=2))
```

### 4. Création d'un Dashboard statique initial

Créer le fichier `/var/www/html/dashboard/index.html` pour un dashboard simple avec visualisation des résultats d'analyse.

## Plan d'action pour les prochains jours

### Jour 1: Installation et configuration de Nginx
1. **Installer Nginx sur le serveur**
   ```bash
   sudo apt update
   sudo apt install -y nginx
   ```

2. **Configurer Nginx pour le dashboard et l'API**
   ```bash
   sudo nano /etc/nginx/sites-available/dropship-dashboard
   ```
   Utiliser la configuration fournie dans ce document.

3. **Activer la configuration et démarrer Nginx**
   ```bash
   sudo ln -s /etc/nginx/sites-available/dropship-dashboard /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

4. **Créer le répertoire pour le dashboard**
   ```bash
   sudo mkdir -p /var/www/html/dashboard
   ```

5. **Créer le fichier index.html du dashboard**
   Utiliser le code HTML fourni précédemment.

### Jour 2: Adaptation de l'API FastAPI
1. **Modifier le fichier main.py de l'API**
   ```bash
   sudo nano /opt/dropship-crew-ai/services/api/app/main.py
   ```
   Remplacer par le code fourni dans ce document.

2. **Reconstruire et redémarrer le service API**
   ```bash
   cd /opt/dropship-crew-ai
   docker-compose build api
   docker-compose up -d api
   ```

### Jour 3: Configuration avancée de Crew AI
1. **Installer les dépendances Crew AI**
   ```bash
   cd /opt/dropship-crew-ai/services/crew-ai
   sudo nano requirements.txt
   ```
   Mettre à jour avec les versions les plus récentes.

2. **Créer les fichiers d'outils pour l'agent Data Analyzer**
   ```bash
   sudo mkdir -p /opt/dropship-crew-ai/services/crew-ai/tools
   sudo touch /opt/dropship-crew-ai/services/crew-ai/tools/__init__.py
   sudo nano /opt/dropship-crew-ai/services/crew-ai/tools/scraping.py
   ```
   Implémenter WebScrapingTool comme décrit dans ce document.

3. **Créer les outils additionnels**
   ```bash
   sudo nano /opt/dropship-crew-ai/services/crew-ai/tools/product_analysis.py
   sudo nano /opt/dropship-crew-ai/services/crew-ai/tools/trend_identification.py
   ```
   Implémenter les autres outils.

4. **Mise à jour du fichier main.py pour utiliser Crew AI**
   ```bash
   sudo nano /opt/dropship-crew-ai/services/crew-ai/main.py
   ```
   Utiliser le code fourni dans ce document.

### Jour 4: Test initial du système
1. **Tester l'API**
   ```bash
   curl http://localhost:8000/status
   ```

2. **Tester Nginx et le dashboard**
   Accéder à `http://163.172.160.102/` dans un navigateur.

3. **Tester l'agent Data Analyzer**
   ```bash
   cd /opt/dropship-crew-ai/services/crew-ai
   python main.py
   ```

4. **Corriger les problèmes éventuels**
   Ajuster la configuration en fonction des erreurs rencontrées.

## Résumé des modifications de l'approche

Cette nouvelle approche offre plusieurs avantages par rapport à la méthode précédente:

1. **Utilisation optimisée de Crew AI**: Exploitation complète du framework pour accélérer le développement
2. **Réduction des délais**: Passage d'un horizon de 3-4 mois à 8 semaines
3. **Optimisation des coûts**: Maintien d'un budget raisonnable (27-47€/mois)
4. **Flexibilité accrue**: Déploiement progressif permettant de valider chaque composant
5. **Infrastructure simplifiée**: Utilisation de Nginx hors Docker pour éviter les problèmes d'intégration rencontrés

En suivant cette approche, nous pouvons obtenir:
- Un agent Data Analyzer fonctionnel dès la semaine 1
- Une boutique Shopify avec produits dès la semaine 3
- Un système complet à la fin de la semaine 8

Cette stratégie équilibre parfaitement rapidité de développement, performance et maîtrise des coûts, tout en exploitant au maximum les capacités de Crew AI.
