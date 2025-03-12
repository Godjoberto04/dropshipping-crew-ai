# Agent Content Generator

## Description

L'agent Content Generator est le troisième agent implémenté dans le projet Dropshipping Crew AI. Il est responsable de la génération automatique de contenu optimisé pour le SEO, en particulier les descriptions de produits, les pages de catégories et les articles de blog.

## Fonctionnalités actuelles (v0.1.0)

- Génération de descriptions de produits optimisées pour le SEO
- Support pour différentes niches (mode, électronique, maison, beauté)
- Support pour différents tons de communication (persuasif, informatif, enjoué, professionnel)
- Optimisation SEO avec génération de métadonnées (meta title, meta description, mots-clés)
- Support multilangue (français, anglais)
- Publication automatique via l'intégration avec Website Builder (Shopify)

## Architecture

L'agent Content Generator est organisé en plusieurs modules :

```
content-generator/
├── main.py                 # Point d'entrée principal
├── config.py               # Configuration
├── generators/             # Générateurs de contenu spécifiques
│   └── product_description.py
├── optimizers/             # Optimiseurs de contenu
│   └── seo_optimizer.py
├── templates/              # Templates par type de contenu et niche
│   └── product_templates.py
├── tools/                  # Outils utilitaires
│   ├── api_client.py
│   └── claude_client.py
├── integrations/           # Intégrations avec d'autres agents
│   ├── data_analyzer.py
│   └── shopify.py
└── tests/                  # Tests unitaires et d'intégration
```

## Installation et configuration

### Avec Docker (recommandé)

1. Assurez-vous que Docker et Docker Compose sont installés
2. Configurez les variables d'environnement dans `.env` à la racine du projet
3. Lancez l'agent avec : `docker-compose up -d content-generator`

### Installation manuelle

1. Assurez-vous que Python 3.10+ est installé
2. Installez les dépendances : `pip install -r requirements.txt`
3. Configurez les variables d'environnement (voir section Configuration)
4. Lancez l'agent : `python main.py`

### Configuration

L'agent utilise les variables d'environnement suivantes :

```
# Configuration de l'agent
AGENT_ID=content-generator
AGENT_VERSION=0.1.0
API_BASE_URL=http://api:8000
POLL_INTERVAL=5

# Configuration API Claude
CLAUDE_API_KEY=votre_clé_api_claude
CLAUDE_MODEL=claude-3-haiku-20240307

# Paramètres de génération
DEFAULT_LANGUAGE=fr
DEFAULT_TONE=persuasive
```

## Utilisation

L'agent communique avec l'API centrale pour recevoir et traiter des tâches. Voici comment l'utiliser via l'API :

### Génération de description de produit

```bash
curl -X POST "http://votre-serveur:8000/agents/content-generator/action" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "generate_product_description",
    "product_data": {
      "name": "Écouteurs Bluetooth Premium",
      "features": ["Autonomie 24h", "Suppression active du bruit", "Résistant à l\'eau"],
      "price": "89.99",
      "brand": "TechSound"
    },
    "tone": "persuasif",
    "niche": "electronics",
    "language": "fr",
    "auto_publish": false
  }'
```

### Optimisation de contenu existant

```bash
curl -X POST "http://votre-serveur:8000/agents/content-generator/action" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "optimize_content",
    "content": "Votre contenu à optimiser...",
    "content_type": "product_description",
    "keywords": ["mot-clé 1", "mot-clé 2"]
  }'
```

## Développement

### Extension des fonctionnalités

Pour ajouter un nouveau type de générateur de contenu :

1. Créez un nouveau module dans le répertoire `generators/`
2. Implémentez la classe de générateur avec les méthodes nécessaires
3. Ajoutez les templates correspondants dans le répertoire `templates/`
4. Mettez à jour `main.py` pour intégrer le nouveau générateur

### Exécution des tests

Voir la documentation détaillée dans [docs/tests-content-generator.md](../../docs/tests-content-generator.md)

```bash
python -m pytest tests/
```

## Intégration avec les autres agents

### Data Analyzer

L'agent Content Generator peut enrichir les données produit en se connectant à l'agent Data Analyzer. Cela permet d'incorporer des informations de marché pertinentes dans les descriptions générées.

### Website Builder

L'agent peut publier directement les contenus générés sur la boutique Shopify via l'agent Website Builder grâce au paramètre `auto_publish`.

## Prochaines étapes de développement

1. **Phase 2** : Ajout des générateurs de pages catégories et articles de blog
2. **Phase 3** : Implémentation d'une optimisation SEO avancée avec analyse concurrentielle
3. **Phase 4** : Intégration complète avec le système de workflows

## Résolution des problèmes courants

### L'agent ne se connecte pas à l'API centrale

Vérifiez que :
- La variable d'environnement `API_BASE_URL` est correctement configurée
- L'API centrale est en cours d'exécution et accessible
- Les ports nécessaires sont ouverts si vous utilisez Docker

### Erreurs avec l'API Claude

Vérifiez que :
- La clé API Claude est valide et correctement configurée
- Le modèle spécifié est disponible dans votre abonnement
- Vous n'avez pas dépassé vos limites d'utilisation de l'API Claude

---

Pour plus d'informations, consultez la [documentation complète de l'agent Content Generator](../../docs/content-generator-guide.md).