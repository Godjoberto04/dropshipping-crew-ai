# Guide d'utilisation de l'agent Content Generator

L'agent Content Generator est un composant clé du système autonome de dropshipping, responsable de la création de tout le contenu textuel du site, allant des descriptions de produits optimisées SEO aux textes marketing persuasifs et aux articles de blog.

## Table des matières
1. [Fonctionnalités principales](#fonctionnalités-principales)
2. [Architecture et modules](#architecture-et-modules)
3. [Utilisation via l'API](#utilisation-via-lapi)
4. [Exemples de code](#exemples-de-code)
5. [Cas d'utilisation](#cas-dutilisation)
6. [Templates et personnalisation](#templates-et-personnalisation)
7. [Optimisation SEO](#optimisation-seo)
8. [Limitations connues](#limitations-connues)
9. [Dépannage](#dépannage)

## Fonctionnalités principales

L'agent Content Generator offre les fonctionnalités suivantes:

### Génération de descriptions produits
- Création de descriptions produits engageantes et optimisées SEO
- Adaptation du ton et du style selon la niche et le public cible
- Mise en valeur des caractéristiques et avantages clés
- Intégration des mots-clés pertinents pour le référencement

### Création de contenu marketing
- Génération de slogans et phrases d'accroche
- Création de contenu promotionnel pour les bannières et pages spéciales
- Rédaction d'emails marketing et newsletters
- Textes pour campagnes publicitaires

### Optimisation SEO
- Génération de métadonnées optimisées (titres, descriptions)
- Structuration du contenu avec des balises HTML appropriées
- Intégration naturelle des mots-clés cibles
- Création de textes d'ancrage optimisés pour les liens internes

### Contenu de pages statiques
- Rédaction de pages "À propos", FAQ, Mentions légales
- Création de contenu pour les pages de politique (livraison, retours, confidentialité)
- Textes pour les pages de landing et promotions spéciales

## Architecture et modules

L'agent Content Generator est construit sur une architecture asynchrone moderne basée sur FastAPI, avec plusieurs modules spécialisés:

### ProductDescriptionGenerator
Module principal pour la génération de descriptions produits adaptées à différentes catégories.

### SEOOptimizer
Optimise le contenu généré pour le référencement naturel.

### TemplateManager
Gère les templates par niche et type de contenu pour assurer une cohérence stylistique.

### ClaudeClient
Interface avec l'API Claude pour la génération de contenu de haute qualité.

### APIClient
Permet la communication avec l'API centrale du système.

## Utilisation via l'API

L'agent Content Generator expose ses fonctionnalités via l'API REST centrale du système.

### Endpoints principaux

#### Génération de description produit
```
POST /api/v1/agents/content-generator/product-descriptions
```

Paramètres:
```json
{
  "product": {
    "name": "Écouteurs sans fil BlueBeat Pro",
    "category": "Électronique / Audio",
    "features": [
      "Bluetooth 5.2",
      "Autonomie de 36 heures avec étui de charge",
      "Résistant à l'eau et la sueur (IPX7)",
      "Réduction de bruit active",
      "Commandes tactiles"
    ],
    "specifications": {
      "brand": "TechAudio",
      "color": "Noir",
      "weight": "65g",
      "dimensions": "5.4 x 4.2 x 2.2 cm"
    },
    "target_audience": "Sportifs et amateurs de musique",
    "price_point": "Premium"
  },
  "requirements": {
    "tone": "Professionnel et enthousiaste",
    "length": "Medium",
    "seo_keywords": ["écouteurs sans fil", "écouteurs bluetooth", "réduction de bruit"],
    "highlight_features": ["autonomie", "étanchéité"]
  }
}
```

Réponse:
```json
{
  "status": "success",
  "content_id": "desc_12345",
  "description": {
    "short": "Les écouteurs BlueBeat Pro offrent un son exceptionnel, une autonomie impressionnante de 36h et une résistance totale à l'eau (IPX7) pour accompagner tous vos entraînements.",
    "full": "# Écouteurs sans fil BlueBeat Pro\n\nPlongez dans un univers sonore d'exception avec les **écouteurs sans fil BlueBeat Pro** de TechAudio. Conçus pour les sportifs et les mélomanes exigeants, ces écouteurs bluetooth allient performance audio, confort et durabilité.\n\n## Une autonomie record pour vous accompagner partout\n\nAvec leur impressionnante **autonomie de 36 heures** grâce à leur étui de charge compact, les BlueBeat Pro vous accompagnent toute la journée et bien plus. Profitez de votre musique préférée pendant vos trajets, séances d'entraînement et sessions de travail sans craindre de tomber en panne de batterie.\n\n## Résistance totale à l'eau et à la sueur\n\nLa certification **IPX7** garantit une **étanchéité parfaite**, vous permettant d'utiliser vos écouteurs dans toutes les conditions : pluie intense, transpiration abondante lors de vos séances de sport les plus intenses, et même une immersion accidentelle dans l'eau.\n\n## Qualité sonore exceptionnelle et immersion totale\n\nDotés de la technologie de **réduction de bruit active**, ces écouteurs vous isolent des distractions extérieures pour une expérience d'écoute immersive. La dernière version Bluetooth 5.2 assure une connexion stable et sans latence avec tous vos appareils.\n\n## Design ergonomique et contrôle intuitif\n\nLes commandes tactiles vous permettent de gérer facilement votre musique et vos appels d'un simple toucher. Légers (65g) et parfaitement ajustés, vous oublierez que vous les portez même après plusieurs heures d'utilisation.\n\nTransformez votre expérience audio avec les écouteurs BlueBeat Pro et découvrez ce que signifie vraiment la liberté sans fil.",
    "meta_title": "Écouteurs BlueBeat Pro | Sans Fil Bluetooth avec Réduction de Bruit Active",
    "meta_description": "Découvrez les écouteurs sans fil BlueBeat Pro avec 36h d'autonomie, résistance IPX7 et réduction de bruit active. Parfaits pour le sport et la musique."
  }
}
```

#### Génération de métadonnées SEO
```
POST /api/v1/agents/content-generator/metadata
```

Paramètres:
```json
{
  "page_type": "product",
  "title": "Écouteurs sans fil BlueBeat Pro",
  "content_summary": "Écouteurs bluetooth avec autonomie de 36h, résistance à l'eau IPX7 et réduction de bruit active, idéals pour le sport.",
  "keywords": ["écouteurs sans fil", "écouteurs bluetooth", "écouteurs sport"],
  "category": "Audio",
  "competitors": ["Sony WF-1000XM4", "Apple AirPods Pro"]
}
```

Réponse:
```json
{
  "status": "success",
  "content_id": "meta_12345",
  "metadata": {
    "title": "Écouteurs BlueBeat Pro | Sans Fil Bluetooth avec Réduction de Bruit | TechGadgetsPro",
    "description": "Découvrez les écouteurs sans fil BlueBeat Pro avec 36h d'autonomie, résistance IPX7 et réduction de bruit active. Son exceptionnel et confort optimal pour le sport.",
    "og_title": "BlueBeat Pro: Écouteurs Bluetooth Étanches pour le Sport",
    "og_description": "Une expérience audio immersive avec 36h d'autonomie et isolation phonique parfaite pour vos entraînements. Livraison gratuite!",
    "structured_data": {
      "@context": "https://schema.org/",
      "@type": "Product",
      "name": "Écouteurs sans fil BlueBeat Pro",
      "description": "Écouteurs bluetooth avec autonomie de 36h, résistance à l'eau IPX7 et réduction de bruit active, idéals pour le sport.",
      "brand": "TechAudio",
      "category": "Audio"
    }
  }
}
```

#### Génération de contenu de page
```
POST /api/v1/agents/content-generator/page-content
```

Paramètres:
```json
{
  "page_type": "about_us",
  "company_info": {
    "name": "TechGadgetsPro",
    "founding_year": 2024,
    "mission": "Offrir des gadgets technologiques innovants à prix abordables",
    "values": ["Qualité", "Innovation", "Service client", "Prix juste"]
  },
  "requirements": {
    "tone": "Professionnel et chaleureux",
    "sections": ["histoire", "mission", "équipe", "valeurs", "engagement"]
  }
}
```

Réponse:
```json
{
  "status": "success",
  "content_id": "page_12345",
  "page_content": {
    "title": "À propos de TechGadgetsPro",
    "meta_title": "Notre Histoire et Notre Mission | TechGadgetsPro",
    "meta_description": "Découvrez TechGadgetsPro, votre source de gadgets technologiques innovants depuis 2024. Qualité, innovation et service client au meilleur prix.",
    "sections": [
      {
        "title": "Notre Histoire",
        "content": "Fondée en 2024, TechGadgetsPro est née d'une passion commune pour les technologies innovantes et accessibles. En observant le marché des gadgets électroniques, nous avons constaté un écart important entre les produits haut de gamme à prix prohibitifs et les alternatives économiques de qualité douteuse.\n\nNous avons alors décidé de créer une alternative: une boutique en ligne proposant des gadgets technologiques soigneusement sélectionnés, alliant qualité, fonctionnalités avancées et prix raisonnables."
      },
      {
        "title": "Notre Mission",
        "content": "Chez TechGadgetsPro, notre mission est simple mais ambitieuse: offrir des gadgets technologiques innovants qui améliorent votre quotidien, sans vider votre portefeuille.\n\nNous croyons fermement que l'innovation technologique devrait être accessible à tous. C'est pourquoi nous travaillons sans relâche pour dénicher les produits offrant le meilleur rapport qualité-prix sur le marché."
      },
      {
        "title": "Notre Équipe",
        "content": "Derrière TechGadgetsPro se cache une équipe passionnée de geeks, de testeurs rigoureux et d'experts en service client. Chaque membre apporte son expertise unique pour garantir que les produits que nous proposons répondent à nos standards élevés et que votre expérience d'achat soit irréprochable."
      },
      {
        "title": "Nos Valeurs",
        "content": "**Qualité:** Nous ne compromettrons jamais sur la qualité. Chaque produit est minutieusement évalué avant d'être ajouté à notre catalogue.\n\n**Innovation:** Nous sommes constamment à la recherche des dernières innovations pour vous proposer des gadgets qui font réellement la différence.\n\n**Service client:** Votre satisfaction est notre priorité absolue. Notre équipe est disponible pour répondre à toutes vos questions et résoudre rapidement tout problème.\n\n**Prix juste:** Nous croyons qu'une technologie de qualité ne devrait pas coûter une fortune. Nous nous efforçons de maintenir des prix abordables sans sacrifier la qualité."
      },
      {
        "title": "Notre Engagement",
        "content": "Au-delà de la vente de produits, nous nous engageons à créer une relation durable avec nos clients. Cela signifie être transparents sur nos produits, offrir un service après-vente attentif, et toujours rechercher des moyens d'améliorer notre offre.\n\nNous vous remercions de faire partie de l'aventure TechGadgetsPro et nous nous réjouissons de vous accompagner dans votre exploration des technologies innovantes."
      }
    ]
  }
}
```

## Exemples de code

### Exemple Python

Voici comment utiliser l'API avec Python:

```python
import requests
import json

BASE_URL = "http://your-server-ip/api/v1"
API_KEY = "your_api_key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Génération de description produit
def generate_product_description(product_name, category, features, specifications, target_audience, price_point):
    endpoint = f"{BASE_URL}/agents/content-generator/product-descriptions"
    
    payload = {
        "product": {
            "name": product_name,
            "category": category,
            "features": features,
            "specifications": specifications,
            "target_audience": target_audience,
            "price_point": price_point
        },
        "requirements": {
            "tone": "Professionnel et enthousiaste",
            "length": "Medium",
            "seo_keywords": [product_name.lower(), category.lower().split(" / ")[0]],
            "highlight_features": features[:2]  # Mettre en avant les deux premières caractéristiques
        }
    }
    
    response = requests.post(endpoint, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Génération de métadonnées SEO
def generate_metadata(title, content_summary, keywords, category):
    endpoint = f"{BASE_URL}/agents/content-generator/metadata"
    
    payload = {
        "page_type": "product",
        "title": title,
        "content_summary": content_summary,
        "keywords": keywords,
        "category": category
    }
    
    response = requests.post(endpoint, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Utilisation des fonctions
product_description = generate_product_description(
    "Smartwatch FitLife Pro",
    "Électronique / Wearables",
    [
        "Suivi de 15 activités sportives",
        "Étanche jusqu'à 50m",
        "Autonomie de 14 jours",
        "Écran AMOLED 1.4 pouces",
        "Capteur de fréquence cardiaque"
    ],
    {
        "brand": "FitTech",
        "color": "Noir",
        "weight": "45g",
        "dimensions": "4.5 x 3.8 x 1.2 cm"
    },
    "Sportifs et personnes soucieuses de leur santé",
    "Milieu de gamme"
)

metadata = generate_metadata(
    "Smartwatch FitLife Pro",
    "Montre connectée avec suivi de 15 sports, étanche 50m, autonomie 14 jours et écran AMOLED.",
    ["smartwatch", "montre connectée", "suivi fitness"],
    "Wearables"
)

print(json.dumps(product_description, indent=2))
print(json.dumps(metadata, indent=2))
```

### Exemple avec Curl

```bash
# Génération de description produit
curl -X POST "http://your-server-ip/api/v1/agents/content-generator/product-descriptions" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "product": {
      "name": "Écouteurs sans fil BlueBeat Pro",
      "category": "Électronique / Audio",
      "features": [
        "Bluetooth 5.2",
        "Autonomie de 36 heures avec étui de charge",
        "Résistant à l'eau et la sueur (IPX7)",
        "Réduction de bruit active",
        "Commandes tactiles"
      ],
      "specifications": {
        "brand": "TechAudio",
        "color": "Noir",
        "weight": "65g",
        "dimensions": "5.4 x 4.2 x 2.2 cm"
      },
      "target_audience": "Sportifs et amateurs de musique",
      "price_point": "Premium"
    },
    "requirements": {
      "tone": "Professionnel et enthousiaste",
      "length": "Medium",
      "seo_keywords": ["écouteurs sans fil", "écouteurs bluetooth", "réduction de bruit"],
      "highlight_features": ["autonomie", "étanchéité"]
    }
  }'

# Génération de métadonnées SEO
curl -X POST "http://your-server-ip/api/v1/agents/content-generator/metadata" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "page_type": "product",
    "title": "Écouteurs sans fil BlueBeat Pro",
    "content_summary": "Écouteurs bluetooth avec autonomie de 36h, résistance à l'eau IPX7 et réduction de bruit active, idéals pour le sport.",
    "keywords": ["écouteurs sans fil", "écouteurs bluetooth", "écouteurs sport"],
    "category": "Audio",
    "competitors": ["Sony WF-1000XM4", "Apple AirPods Pro"]
  }'
```

## Cas d'utilisation

Voici quelques cas d'utilisation typiques de l'agent Content Generator:

### 1. Génération de contenu pour un nouveau produit

Lorsque vous ajoutez un nouveau produit à votre boutique:

1. Collectez les informations techniques et caractéristiques du produit
2. Utilisez l'endpoint `/product-descriptions` pour générer une description optimisée
3. Utilisez l'endpoint `/metadata` pour générer les métadonnées SEO
4. Intégrez le contenu généré dans votre fiche produit Shopify

### 2. Création d'une nouvelle catégorie de produits

Pour lancer une nouvelle catégorie dans votre boutique:

1. Définissez le positionnement et les caractéristiques générales de la catégorie
2. Utilisez l'endpoint `/page-content` avec `page_type: "category_page"`
3. Générez un contenu d'introduction optimisé SEO pour la page de catégorie
4. Utilisez des mots-clés spécifiques à la niche pour améliorer le référencement

### 3. Mise en place d'une campagne promotionnelle

Pour créer une promotion saisonnière:

1. Définissez les détails de la promotion (offres, durée, produits concernés)
2. Utilisez l'endpoint `/content-generator/promotional` pour générer:
   - Titres accrocheurs pour bannières
   - Descriptions de la promotion
   - Argumentaire de vente adapté à la saisonnalité
3. Générez les textes d'emails marketing associés à la promotion

### 4. Refonte des pages statiques du site

Pour améliorer les pages institutionnelles:

1. Rassemblez les informations clés sur votre entreprise (mission, valeurs, historique)
2. Utilisez l'endpoint `/page-content` pour chaque type de page (about_us, contact, faq)
3. Mettez à jour vos pages avec un contenu plus engageant et optimisé SEO
4. Assurez la cohérence du ton et du style entre toutes les pages du site

## Templates et personnalisation

L'agent Content Generator utilise un système de templates sophistiqué pour adapter le contenu généré selon vos besoins spécifiques.

### Templates par niche

Des templates spécialisés sont disponibles pour différentes niches:

| Niche | Style de contenu | Emphase |
|-------|------------------|---------|
| Mode | Élégant, tendance, inspirant | Matériaux, style, occasions |
| Électronique | Technique, précis, informatif | Spécifications, performances, compatibilité |
| Maison & Jardin | Chaleureux, descriptif, pratique | Utilité, design, durabilité |
| Beauté | Sensoriel, aspirationnel, émotionnel | Bénéfices, ingrédients, résultats |
| Sport | Dynamique, motivant, technique | Performance, confort, durabilité |
| Jouets | Ludique, éducatif, rassurant | Sécurité, âge approprié, bénéfices éducatifs |

### Personnalisation des templates

Vous pouvez créer vos propres templates ou modifier les existants via l'endpoint:

```
POST /api/v1/agents/content-generator/templates/customize
```

Exemple de personnalisation de template:

```json
{
  "template_name": "electronics_product",
  "sections": [
    {
      "name": "intro",
      "pattern": "Découvrez le/la ${product.name}, ${custom_intro_text}. Ce ${product.category} ${custom_benefit_description}."
    },
    {
      "name": "features",
      "pattern": "## Caractéristiques principales\n\n${bullet_list_features}"
    },
    {
      "name": "technical_specs",
      "pattern": "## Spécifications techniques\n\n${specs_table}"
    },
    {
      "name": "use_cases",
      "pattern": "## Utilisations idéales\n\n${use_cases_paragraphs}"
    },
    {
      "name": "conclusion",
      "pattern": "Améliorez votre expérience ${custom_experience_text} avec le/la ${product.name}. ${call_to_action}"
    }
  ],
  "variables": {
    "custom_intro_text": "l'innovation qui révolutionne votre quotidien",
    "custom_benefit_description": "vous offre des performances exceptionnelles dans un design compact et élégant",
    "custom_experience_text": "technologique",
    "call_to_action": "Commandez dès maintenant et recevez-le sous 48h!"
  }
}
```

### Styles de ton

L'API permet également de spécifier différents styles de ton:

- **Professionnel**: Formel, informatif, crédible
- **Enthousiaste**: Énergique, positif, motivant
- **Luxe**: Élégant, exclusif, raffiné
- **Amical**: Décontracté, accessible, conversationnel
- **Technique**: Précis, détaillé, factuel
- **Minimaliste**: Concis, direct, essentiel

## Optimisation SEO

L'agent Content Generator intègre des fonctionnalités avancées d'optimisation SEO:

### Analyse de mots-clés

Utilisez l'endpoint d'analyse de mots-clés pour optimiser votre contenu:

```
POST /api/v1/agents/content-generator/keyword-analysis
```

Exemple de requête:

```json
{
  "primary_keyword": "écouteurs bluetooth sans fil",
  "related_keywords": ["casque audio bluetooth", "écouteurs sport", "écouteurs réduction bruit"],
  "competitor_urls": [
    "https://www.example.com/product1",
    "https://www.example.com/product2"
  ]
}
```

Réponse:

```json
{
  "keyword_analysis": {
    "primary_keyword": {
      "search_volume": "Medium-High",
      "competition": "High",
      "recommended_density": "1.5-2.5%",
      "recommended_placements": ["title", "h1", "first paragraph", "meta description"]
    },
    "related_keywords": [
      {
        "keyword": "écouteurs sport",
        "search_volume": "Medium",
        "competition": "Medium",
        "recommended_density": "0.8-1.2%"
      },
      ...
    ],
    "content_recommendations": {
      "recommended_length": "500-800 words",
      "heading_structure": ["H1: Primary keyword", "H2: Features with related keywords", "H2: Technical specifications", "H2: Use cases with long-tail keywords"],
      "semantic_terms": ["audio", "son", "charge", "autonomie", "connexion", "appairage", "codec"]
    }
  }
}
```

### Structure de contenu optimisée

L'agent génère automatiquement des structures de contenu optimisées pour le SEO:

- Titres H1, H2, H3 correctement hiérarchisés
- Paragraphes introductifs avec mots-clés prioritaires
- Densité de mots-clés appropriée
- Liens internes avec textes d'ancrage optimisés
- Balisage schema.org pour le rich snippets

## Limitations connues

### Limites actuelles

- **Longueur de contenu**: Limite de 5000 mots par génération de contenu
- **Images et médias**: L'agent ne génère pas de contenu visuel
- **Langues**: Support complet pour français et anglais, support partiel pour espagnol, allemand et italien
- **Rate limits**: Maximum 100 requêtes/heure pour les descriptions produits, 50 requêtes/heure pour les autres types de contenu
- **Niches spécialisées**: Certaines niches très techniques peuvent nécessiter des ajustements manuels

### Contournements possibles

- Pour les contenus longs, utilisez l'approche de génération par sections avec l'endpoint `/content-sections`
- Pour les limitations linguistiques, utilisez le paramètre `base_language` pour générer en anglais ou français, puis utilisez le paramètre `translate_to` pour obtenir une traduction
- Pour les niches spécialisées, utilisez le paramètre `expert_mode: true` et fournissez des exemples via `reference_content`

## Dépannage

### Problèmes courants

#### Contenu généré trop générique
Le contenu ne semble pas assez spécifique au produit.
**Solution**: Fournissez plus de détails techniques et de caractéristiques distinctives dans votre requête.

#### Erreur 429 (Too Many Requests)
Vous avez dépassé les rate limits de l'API.
**Solution**: Espacez vos requêtes ou utilisez le mode batch.

#### Contenu dupliqué entre produits similaires
Les descriptions semblent trop similaires entre produits de même catégorie.
**Solution**: Utilisez le paramètre `ensure_uniqueness: true` et spécifiez des `unique_selling_points` différents pour chaque produit.

#### Mots-clés mal intégrés
L'intégration des mots-clés semble forcée ou non naturelle.
**Solution**: Utilisez moins de mots-clés mais plus pertinents, et spécifiez `natural_integration: true`.

### Logs et diagnostics

Pour diagnostiquer les problèmes, utilisez l'endpoint de logs:

```
GET /api/v1/agents/content-generator/logs
```

Paramètres:
```
?level=error&start_date=2025-03-15&end_date=2025-03-16
```

### Support et ressources supplémentaires

Pour une assistance plus détaillée:

1. Consultez les logs système pour les erreurs détaillées
2. Vérifiez le statut du service via l'endpoint `/system/health`
3. Pour un support spécifique, consultez le [guide de dépannage général](../troubleshooting.md) ou ouvrez une issue sur le dépôt GitHub
