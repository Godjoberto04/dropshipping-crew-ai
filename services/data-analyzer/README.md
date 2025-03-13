# Data Analyzer - Agent d'analyse et de recommandation produit

L'agent Data Analyzer est responsable de l'analyse du marché, de l'identification des produits à fort potentiel et de la génération de rapports d'analyse dans le système dropshipping-crew-ai.

## Fonctionnalités

- Analyse des tendances Google Trends pour les produits et les niches
- Évaluation multicritères des produits selon 15 facteurs clés
- Optimisation par niche pour une évaluation contextualisée
- Génération de recommandations avec explication détaillée
- Calcul du niveau de confiance pour chaque évaluation
- Identification des forces et faiblesses des produits
- Traitement par lots pour l'analyse de multiples produits

## Architecture

L'agent Data Analyzer est organisé en modules spécialisés :

```
data_sources/             # Sources de données externes
  ├── trends/             # Module d'analyse de tendances
  │   └── trends_analyzer.py  # Analyse via Google Trends
  ├── marketplaces/       # Analyse des marketplaces (à venir)
  ├── seo/                # Analyse SEO (à venir)
  └── social/             # Analyse des réseaux sociaux (à venir)

models/                   # Modèles d'analyse et de prédiction
  ├── scoring/            # Système de scoring des produits
  │   ├── base.py         # Classe de base pour les scorers
  │   ├── multicriteria.py  # Système de scoring avancé
  │   ├── multicriteria_core.py  # Fonctions principales du scoring
  │   └── criteria/       # Critères d'évaluation individuels
  │       ├── market.py   # Potentiel de marché
  │       ├── competition.py  # Niveau de concurrence
  │       ├── profitability.py  # Rentabilité
  │       ├── operational.py  # Aspects opérationnels
  │       └── trend.py    # Tendances et saisonnalité

tests/                    # Tests unitaires
  └── test_multicriteria_scorer.py  # Tests du système de scoring

tools/                    # Outils utilitaires
  ├── api_client.py       # Client pour l'API centrale
  └── ...
```

## Système de scoring multicritères

Le cœur de l'agent Data Analyzer est son système de scoring multicritères avancé. Ce système évalue les produits selon 5 catégories principales :

1. **Potentiel de marché**
   - Volume de recherche
   - Taux de croissance
   - Taille du marché

2. **Niveau de concurrence**
   - Nombre de concurrents
   - Concurrence par les prix
   - Barrières à l'entrée

3. **Rentabilité**
   - Marge brute
   - Stabilité des prix
   - Potentiel de ventes additionnelles

4. **Aspects opérationnels**
   - Complexité d'expédition
   - Taux de retour anticipé
   - Fiabilité du fournisseur

5. **Tendances et timing**
   - Consistance de la tendance
   - Impact de la saisonnalité
   - Mentions sur réseaux sociaux

### Optimisation par niche

Le système ajuste automatiquement les poids des critères en fonction de la niche du produit. Par exemple :

- **Mode** : Accent accru sur les tendances et les mentions sociales
- **Électronique** : Importance des aspects opérationnels et de la fiabilité fournisseur
- **Décoration** : Attention particulière à la complexité d'expédition
- **Beauté** : Focus sur le potentiel de marché et les mentions sociales
- **Fitness** : Attention à la saisonnalité et au taux de croissance

### Indice de confiance

Chaque évaluation est accompagnée d'un indice de confiance basé sur :
- La complétude des données disponibles
- La consistance des scores entre les différentes catégories
- La disponibilité des critères critiques (volume de recherche, marge, concurrence)

## Utilisation

### Exemple d'analyse d'un produit

```python
from models.scoring.multicriteria import AdvancedProductScorer

# Initialiser le scorer
scorer = AdvancedProductScorer()

# Enregistrer des sources de données
scorer.register_data_source('trends', trends_analyzer)
scorer.register_data_source('marketplace', marketplace_analyzer)

# Analyser un produit
product_data = {
    'id': 'product-123',
    'name': 'Écouteurs Bluetooth sans fil',
    'niche': 'electronics',
    # Autres données du produit...
}

result = scorer.score_product(product_data)

# Accéder aux résultats
overall_score = result['overall_score']
recommendation = result['recommendation']
strengths = result['strengths']
weaknesses = result['weaknesses']
explanation = result['explanation']

print(f"Score: {overall_score}/100 - {recommendation}")
```

### API REST

L'agent Data Analyzer expose ses fonctionnalités via l'API centrale :

```
POST /api/v1/analyze/product
```

Corps de la requête :
```json
{
  "product_id": "product-123",
  "product_name": "Écouteurs Bluetooth sans fil",
  "niche": "electronics",
  "url": "https://example.com/product/123",
  "keywords": ["wireless earbuds", "bluetooth headphones"],
  "price": 49.99,
  "supplier_price": 29.99
}
```

Réponse :
```json
{
  "overall_score": 78.5,
  "category_scores": {
    "market_potential": 85,
    "competition": 62,
    "profitability": 75,
    "operational": 80,
    "trend": 90
  },
  "recommendation": "Potentiel élevé - Fortement recommandé",
  "confidence": 85,
  "strengths": [
    {
      "category": "market_potential",
      "display_name": "Potentiel de marché",
      "score": 85,
      "description": "Fort potentiel de marché"
    }
  ],
  "weaknesses": [],
  "explanation": {
    "summary": "Ce produit présente un excellent potentiel pour le dropshipping avec un score global élevé.",
    "key_factors": [
      "+ Potentiel de marché (85/100): Fort potentiel de marché",
      "+ Tendance (90/100): Forte tendance à la hausse"
    ],
    "confidence_statement": "L'évaluation est très fiable avec un niveau de confiance de 85%."
  }
}
```

## Tests

Le système inclut une suite complète de tests unitaires pour garantir son bon fonctionnement :

```bash
# Exécuter tous les tests
python -m unittest discover -s tests

# Exécuter un test spécifique
python -m unittest tests.test_multicriteria_scorer
```

## Contributions

Ce module implémente [le plan d'amélioration de l'agent Data Analyzer](../docs/plan-data-analyzer-amelioration.md) et suit la stratégie d'intégration des ressources communautaires établie pour le projet.

## À venir

- Intégration de scrapers pour AliExpress et Amazon
- Intégration avec les APIs SEO (SEMrush, Ahrefs)
- Système d'analyse des commentaires sociaux
- Modules de détection d'anomalies et d'alertes
- Système d'apprentissage basé sur les performances réelles
