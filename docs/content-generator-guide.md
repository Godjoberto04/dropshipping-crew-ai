# Guide de l'agent Content Generator

Ce guide détaille le fonctionnement, l'utilisation et la configuration de l'agent Content Generator, responsable de la génération automatisée de contenu optimisé pour les boutiques de dropshipping dans le système.

## Aperçu de l'agent

L'agent Content Generator est conçu pour :

1. **Générer des descriptions de produits** persuasives et optimisées SEO
2. **Optimiser du contenu existant** pour améliorer le référencement
3. **Créer des contenus pour pages catégories** et articles de blog (fonctionnalités à venir)
4. **S'intégrer parfaitement** avec les autres agents (Data Analyzer, Website Builder)
5. **Personnaliser le contenu** selon la niche, le ton et la langue

## Configuration

### Variables d'environnement

Les variables d'environnement suivantes peuvent être configurées dans le fichier `.env` ou directement lors du déploiement du conteneur :

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `CLAUDE_API_KEY` | Clé API Claude (Anthropic) pour la génération de contenu | (requis) |
| `API_BASE_URL` | URL de base de l'API centrale | http://api:8000 |
| `AGENT_ID` | Identifiant de l'agent | content-generator |
| `AGENT_VERSION` | Version de l'agent | 0.1.0 |
| `POLL_INTERVAL` | Intervalle entre les vérifications de tâches (secondes) | 5 |
| `DEFAULT_LANGUAGE` | Langue par défaut pour la génération | fr |
| `DEFAULT_TONE` | Ton par défaut pour la génération | persuasive |

### Configuration Docker

```yaml
# Extrait du docker-compose.yml
content-generator:
  build: ./services/content-generator
  restart: unless-stopped
  volumes:
    - ./logs:/app/logs
  environment:
    - CLAUDE_API_KEY=${CLAUDE_API_KEY}
    - API_BASE_URL=http://api:8000
  depends_on:
    - api
```

## Utilisation de l'API

### Générer une description de produit

```bash
curl -X POST "http://votre-serveur:8000/agents/content-generator/action" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "generate_product_description",
    "product_data": {
      "name": "Écouteurs Bluetooth Premium",
      "features": ["Autonomie 24h", "Suppression active du bruit", "Résistant à l'eau"],
      "price": "89.99",
      "brand": "TechSound",
      "specifications": {
        "Connectivité": "Bluetooth 5.2",
        "Autonomie": "24 heures (avec boîtier)",
        "Résistance": "IPX7"
      }
    },
    "tone": "persuasif",
    "niche": "electronics",
    "language": "fr",
    "auto_publish": false
  }'
```

#### Paramètres

| Paramètre | Type | Description | Requis |
|-----------|------|-------------|--------|
| `action` | string | Action à effectuer : "generate_product_description" | Oui |
| `product_data` | object | Données du produit | Oui |
| `product_data.name` | string | Nom du produit | Oui |
| `product_data.features` | array | Caractéristiques principales du produit | Non |
| `product_data.specifications` | object | Spécifications techniques | Non |
| `product_data.price` | string | Prix du produit | Non |
| `product_data.brand` | string | Marque du produit | Non |
| `product_data.description` | string | Description existante (à enrichir) | Non |
| `tone` | string | Ton de la description : "persuasif", "informatif", "expert", etc. | Non |
| `niche` | string | Niche du produit : "electronics", "fashion", "home", "beauty", etc. | Non |
| `language` | string | Langue de la description | Non |
| `auto_publish` | boolean | Publication automatique via Website Builder | Non |
| `enrich_data` | boolean | Enrichissement des données via Data Analyzer | Non |

#### Réponse

```json
{
  "task_id": "4d68cd3e-4c0a-4c1d-8f0a-1e7e8f3edade",
  "status": "completed",
  "result": {
    "description": "## Écouteurs Bluetooth Premium TechSound - L'Excellence Audio Sans Compromis\n\nPlongez dans une expérience audio exceptionnelle avec les Écouteurs Bluetooth Premium de TechSound. Conçus pour les audiophiles exigeants, ces écouteurs sans fil combinent technologie de pointe, confort optimal et durabilité impressionnante.\n\n### Immersion Sonore Inégalée\n\n* **Suppression active du bruit** qui vous isole des distractions extérieures\n* Son haute fidélité avec des basses profondes et des aigus cristallins\n* Technologie Bluetooth 5.2 pour une connexion stable et sans latence\n\n### Autonomie Record\n\nProfitez de votre musique sans interruption grâce à une autonomie exceptionnelle de 24 heures avec le boîtier de charge. Quelques minutes de charge suffisent pour plusieurs heures d'écoute - idéal pour les voyages et longues journées de travail.\n\n### Robustesse à Toute Épreuve\n\nCertifiés IPX7, ces écouteurs résistent parfaitement à l'eau et à la transpiration. Que vous soyez sous la pluie ou en pleine séance de sport intensive, votre musique vous accompagne sans faillir.\n\n### Confort Irréprochable\n\nLeurs embouts ergonomiques s'adaptent parfaitement à la forme de votre oreille pour un maintien sécurisé et un confort prolongé, même après plusieurs heures d'utilisation.\n\n## Transformez Votre Expérience Audio Dès Maintenant\n\nNe vous contentez plus d'un son ordinaire. À seulement 89,99€, les Écouteurs Bluetooth Premium TechSound représentent l'investissement idéal pour tous ceux qui recherchent une qualité audio exceptionnelle au quotidien.\n\n**Commandez aujourd'hui et redécouvrez vos morceaux préférés comme jamais auparavant!**",
    "seo_metadata": {
      "meta_description": "Découvrez les Écouteurs Bluetooth Premium TechSound avec suppression active du bruit, 24h d'autonomie et résistance à l'eau IPX7. Son haute fidélité et confort optimal pour une expérience audio exceptionnelle.",
      "title_tag": "Écouteurs Bluetooth Premium TechSound - Immersion Sonore & Autonomie 24h",
      "keywords": ["écouteurs bluetooth", "suppression bruit", "résistant eau", "autonomie 24h", "techsound"]
    },
    "raw_description": "..."
  }
}
```

### Optimiser un contenu existant

```bash
curl -X POST "http://votre-serveur:8000/agents/content-generator/action" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "optimize_content",
    "content": "Votre contenu à optimiser...",
    "content_type": "product_description",
    "keywords": ["mot-clé 1", "mot-clé 2"],
    "title": "Titre du contenu"
  }'
```

#### Paramètres

| Paramètre | Type | Description | Requis |
|-----------|------|-------------|--------|
| `action` | string | Action à effectuer : "optimize_content" | Oui |
| `content` | string | Contenu à optimiser | Oui |
| `content_type` | string | Type de contenu : "product_description", "category_page", "blog_article" | Non |
| `keywords` | array | Mots-clés cibles pour l'optimisation | Non |
| `title` | string | Titre du contenu | Non |

#### Réponse

```json
{
  "task_id": "7a91ed3e-4c0a-4c1d-8f0a-1e7e8f3edade",
  "status": "completed",
  "result": {
    "optimized_content": "Contenu optimisé avec mots-clés intégrés...",
    "seo_metadata": {
      "meta_description": "Description méta optimisée avec mots-clés pertinents.",
      "keywords": ["mot-clé 1", "mot-clé 2", "mot-clé 3"]
    },
    "original_content": "Contenu original...",
    "improvement_score": 85.5
  }
}
```

## Fonctionnalités avancées

### Niches spécialisées

L'agent Content Generator prend en charge différentes niches avec des templates et styles adaptés :

- **electronics** : Contenu technique et axé sur les performances
- **fashion** : Style élégant et axé sur le design et le style
- **home** : Contenu évocateur pour les produits de maison et décoration
- **beauty** : Descriptions axées sur les bénéfices et les résultats

Pour utiliser un style spécifique à une niche, spécifiez le paramètre `niche` approprié.

### Tons disponibles

Plusieurs tons sont disponibles pour personnaliser le contenu :

- **persuasif** : Style commercial et incitatif
- **informatif** : Contenu factuel et éducatif
- **expert** : Style professionnel et technique
- **conversationnel** : Ton décontracté et accessible
- **luxe** : Style haut de gamme et exclusif

### Langues supportées

L'agent prend actuellement en charge les langues suivantes :

- **fr** : Français (par défaut)
- **en** : Anglais
- **es** : Espagnol
- **de** : Allemand

## Intégration avec les autres agents

### Avec Data Analyzer

L'agent Content Generator peut enrichir les données produit via Data Analyzer en définissant `enrich_data: true`. Cela permet d'obtenir des informations complémentaires sur le produit, comme les tendances, le potentiel de marché et les mots-clés populaires.

### Avec Website Builder

L'agent peut publier directement le contenu généré sur la boutique Shopify via Website Builder en définissant `auto_publish: true`. Le contenu sera alors automatiquement mis à jour ou créé dans la boutique.

## Fonctionnalités à venir

Les prochaines versions de l'agent Content Generator incluront :

- Génération de pages catégories complètes
- Création d'articles de blog optimisés SEO
- Génération de séquences d'emails marketing
- Support multilingue étendu
- Adaptateurs de niche plus spécialisés
- Système de feedback et d'amélioration continue

## Dépannage

### Problèmes courants

1. **Erreur "API key is invalid"**
   - Vérifiez que votre clé API Claude est valide et correctement configurée

2. **Temps de génération trop long**
   - Les temps de réponse peuvent varier selon la complexité du contenu demandé
   - Vérifiez que l'agent a accès à internet pour communiquer avec l'API Claude

3. **Problème d'intégration avec Website Builder**
   - Assurez-vous que l'agent Website Builder est opérationnel
   - Vérifiez les logs pour identifier d'éventuelles erreurs de communication

### Logs et monitoring

Les logs de l'agent sont disponibles dans le répertoire `/logs` du conteneur. Pour les consulter :

```bash
docker logs content-generator
# ou
docker exec -it content-generator cat /app/logs/content_generator_YYYYMMDD.log
```