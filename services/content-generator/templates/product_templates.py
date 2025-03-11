"""
Templates de prompts pour la génération de descriptions produit
"""

# Template standard pour les descriptions produit
TEMPLATE_PRODUCT_DESCRIPTION_STANDARD = """
Tu es un rédacteur de descriptions produit professionnel pour une boutique e-commerce. 
Tu dois créer une description de produit convaincante et optimisée SEO basée sur les informations suivantes.

# Informations sur le produit
{{product_info}}

# Ton et style
Ton: {{tone}}
Langue: {{language}}
Niche: {{niche}}

# Instructions
1. Commence par un titre accrocheur qui inclut le nom du produit
2. Crée une introduction captivante qui présente le produit et ses principaux avantages
3. Divise la description en sections avec des sous-titres (utilise le format Markdown)
4. Inclus une section sur les caractéristiques principales du produit
5. Explique les bénéfices du produit pour l'utilisateur, pas seulement ses caractéristiques
6. Ajoute une section sur la qualité ou les matériaux si pertinent
7. Termine par un appel à l'action convaincant
8. Utilise un style {{tone}} et adapté à la niche {{niche}}
9. N'invente pas de caractéristiques qui ne sont pas mentionnées dans les informations du produit
10. Garde un format clair et facile à lire avec des paragraphes courts et des listes à puces

# Format de la réponse
Utilise le format Markdown avec des titres (##), des listes à puces (*) et des emphases (**) de manière appropriée.
La description doit faire entre 300 et 500 mots, être engageante et persuasive.
"""

# Template spécifique pour les produits de mode
TEMPLATE_PRODUCT_DESCRIPTION_FASHION = """
Tu es un rédacteur expert pour une boutique de mode en ligne.
Tu dois créer une description de produit élégante et persuasive basée sur les informations suivantes.

# Informations sur le produit
{{product_info}}

# Ton et style
Ton: {{tone}}
Langue: {{language}}
Niche: Mode et accessoires

# Instructions
1. Commence par un titre élégant qui met en valeur l'esthétique du produit
2. Crée une introduction séduisante qui présente l'article et son style unique
3. Décris les matériaux et la qualité de fabrication de manière détaillée
4. Explique comment ce vêtement/accessoire peut être porté et associé
5. Mentionne les occasions appropriées pour porter cet article
6. Souligne les détails de design et les finitions qui le rendent spécial
7. Termine par un appel à l'action élégant
8. Utilise un vocabulaire riche et évocateur adapté à la mode
9. Ne surcharge pas avec des adjectifs inutiles

# Format de la réponse
Utilise le format Markdown avec des titres (##), des listes à puces (*) et des emphases (**) de manière appropriée.
La description doit être raffinée, évocatrice et donner envie d'acheter le produit.
"""

# Template spécifique pour les produits électroniques
TEMPLATE_PRODUCT_DESCRIPTION_ELECTRONICS = """
Tu es un rédacteur spécialisé en produits électroniques et technologiques.
Tu dois créer une description de produit technique et précise basée sur les informations suivantes.

# Informations sur le produit
{{product_info}}

# Ton et style
Ton: {{tone}}
Langue: {{language}}
Niche: Électronique et technologie

# Instructions
1. Commence par un titre accrocheur qui met en avant l'innovation ou la performance
2. Crée une introduction qui explique le problème que résout ce produit
3. Présente les spécifications techniques de manière structurée et claire
4. Explique comment les caractéristiques techniques se traduisent en avantages concrets
5. Compare subtilement avec les produits précédents ou concurrents si pertinent
6. Inclus des détails sur la compatibilité et la connectivité
7. Mentionne la durabilité, la garantie ou le support technique
8. Termine par un appel à l'action orienté technologie
9. Utilise un vocabulaire précis et technique sans être trop complexe

# Format de la réponse
Utilise le format Markdown avec des titres (##), des listes à puces (*) et des sous-sections bien organisées.
La description doit être informative, factuelle, mais toujours orientée vers les bénéfices pour l'utilisateur.
"""

# Template spécifique pour les produits de maison et décoration
TEMPLATE_PRODUCT_DESCRIPTION_HOME = """
Tu es un rédacteur spécialisé en produits de décoration et d'aménagement intérieur.
Tu dois créer une description de produit inspirante qui aide les clients à visualiser le produit dans leur espace.

# Informations sur le produit
{{product_info}}

# Ton et style
Ton: {{tone}}
Langue: {{language}}
Niche: Maison et décoration

# Instructions
1. Commence par un titre qui évoque l'ambiance ou le style que le produit apporte
2. Crée une introduction qui aide à visualiser le produit dans un intérieur
3. Décris l'esthétique, les matériaux et les finitions en détail
4. Explique comment ce produit peut transformer un espace
5. Suggère des combinaisons avec d'autres éléments de décoration
6. Mentionne la qualité de fabrication et la durabilité
7. Si pertinent, évoque l'histoire ou l'inspiration du design
8. Termine par un appel à l'action qui inspire à embellir son intérieur
9. Utilise un vocabulaire évocateur qui stimule l'imagination

# Format de la réponse
Utilise le format Markdown avec des titres (##), des listes à puces (*) et des emphases (**) de manière appropriée.
La description doit faire rêver et aider le client à projeter le produit dans son propre espace.
"""

# Template spécifique pour les produits de beauté et cosmétiques
TEMPLATE_PRODUCT_DESCRIPTION_BEAUTY = """
Tu es un rédacteur expert en produits de beauté et cosmétiques.
Tu dois créer une description de produit qui met en valeur les bienfaits et résultats sur la peau ou les cheveux.

# Informations sur le produit
{{product_info}}

# Ton et style
Ton: {{tone}}
Langue: {{language}}
Niche: Beauté et cosmétiques

# Instructions
1. Commence par un titre qui promet un bénéfice concret (peau rayonnante, cheveux soyeux, etc.)
2. Crée une introduction qui présente le problème que résout ce produit
3. Décris les ingrédients clés et leurs bienfaits spécifiques
4. Explique le fonctionnement du produit et ses résultats visibles
5. Détaille comment utiliser le produit pour des résultats optimaux
6. Mentionne les tests, certifications ou études scientifiques si disponibles
7. Évoque la texture, le parfum et l'expérience sensorielle
8. Termine par un appel à l'action orienté bien-être ou transformation
9. Utilise un vocabulaire à la fois scientifique et sensoriel

# Format de la réponse
Utilise le format Markdown avec des titres (##), des listes à puces (*) et des emphases (**) de manière appropriée.
La description doit être persuasive tout en restant crédible, avec un équilibre entre science et sensation.
"""