# Tests unitaires et d'intégration pour l'agent Content Generator

Ce document décrit les tests unitaires et d'intégration implémentés pour l'agent Content Generator du projet dropshipping-crew-ai.

## Structure des tests

Les tests sont organisés dans le répertoire `services/content-generator/tests/` et se répartissent comme suit :

```
tests/
├── __init__.py
├── README.md                - Documentation et instructions pour les tests
├── test_claude_client.py      - Tests pour le client Claude
├── test_config.py            - Configuration spécifique pour les tests
├── test_main.py               - Tests d'intégration pour l'agent principal
├── test_product_description.py - Tests pour le générateur de descriptions produit
├── test_seo_optimizer.py      - Tests pour l'optimiseur SEO
├── test_templates/           - Templates de test
└── test_data/               - Données de test
```

## Tests implémentés

### Tests du générateur de descriptions produit

- **test_format_product_info** : Teste le formatage des informations produit pour le prompt
- **test_prepare_prompt** : Teste la préparation du prompt avec les variables appropriées
- **test_clean_description** : Teste le nettoyage des descriptions générées
- **test_get_system_prompt** : Teste la génération du prompt système
- **test_generate** : Teste le processus complet de génération d'une description

### Tests de l'optimiseur SEO

- **test_extract_keywords** : Teste l'extraction automatique de mots-clés
- **test_analyze_keyword_density** : Teste l'analyse de densité des mots-clés
- **test_optimize** : Teste l'optimisation du contenu
- **test_generate_meta_description** : Teste la génération de méta-description
- **test_calculate_improvement_score** : Teste le calcul du score d'amélioration

### Tests du client Claude

- **test_generate** : Teste la génération de texte via l'API Claude
- **test_generate_error_handling** : Teste la gestion des erreurs API
- **test_rate_limit_handling** : Teste la gestion des limites de taux

### Tests d'intégration de l'agent Content Generator

- **test_register_agent** : Teste l'enregistrement de l'agent auprès de l'API centrale
- **test_process_task_product_description** : Teste le traitement d'une tâche de génération de description
- **test_process_task_optimize_content** : Teste le traitement d'une tâche d'optimisation de contenu
- **test_process_task_with_auto_publish** : Teste la publication automatique
- **test_process_task_error_handling** : Teste la gestion des erreurs lors du traitement des tâches
- **test_poll_tasks** : Teste la boucle principale de vérification des tâches

## Exécution des tests

### Prérequis

Pour exécuter les tests, vous devez avoir installé les dépendances de développement :

```bash
pip install -r requirements.txt
```

### Exécuter tous les tests

Pour exécuter tous les tests avec pytest :

```bash
python -m pytest services/content-generator/tests/
```

### Exécuter un fichier de test spécifique

```bash
python -m pytest services/content-generator/tests/test_seo_optimizer.py
```

### Exécuter un test spécifique

```bash
python -m pytest services/content-generator/tests/test_seo_optimizer.py::TestSEOOptimizer::test_extract_keywords
```

### Exécuter les tests avec couverture de code

```bash
python -m pytest --cov=services.content-generator services/content-generator/tests/
```

## Tests dans l'environnement Docker

Les tests peuvent également être exécutés dans l'environnement Docker pour garantir la cohérence avec l'environnement de production :

```bash
docker-compose run --rm content-generator python -m pytest tests/
```

## Mocks et isolation

Les tests utilisent des mocks pour isoler les composants et éviter les appels réels aux APIs externes :

- **API Claude** : Toutes les interactions avec l'API Claude sont mockées pour éviter d'utiliser des crédits réels et assurer la stabilité des tests
- **API centrale** : Les appels à l'API centrale sont mockés pour tester l'agent indépendamment
- **Intégrations** : Les intégrations avec Data Analyzer et Shopify sont également mockées

## Organisation des tests asynchrones

L'agent Content Generator utilisant asyncio, les tests doivent gérer correctement les fonctions asynchrones. Nous utilisons `pytest-asyncio` pour faciliter l'exécution des tests asynchrones.

Exemple d'utilisation dans les tests :

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    # Test de fonction asynchrone
    result = await my_async_function()
    assert result == expected_value
```

## Configuration spécifique pour les tests

Le fichier `test_config.py` contient une configuration spécifique pour les tests, avec des valeurs adaptées pour faciliter et accélérer les tests :

- Intervalles réduits pour les boucles
- Limites réduites pour les tailles de contenu
- Clés API factices
- Répertoires spécifiques pour les tests

## Bonnes pratiques pour ajouter de nouveaux tests

1. **Isolation** : Chaque test doit être indépendant et ne pas dépendre de l'état laissé par d'autres tests
2. **Mocks appropriés** : Utiliser des mocks pour toutes les dépendances externes
3. **Assertions claires** : Chaque test doit avoir des assertions précises sur ce qui est testé
4. **Nommage descriptif** : Les noms des tests doivent clairement indiquer ce qui est testé
5. **Documentation** : Ajouter des docstrings pour expliquer le but de chaque test
6. **Test de réussite et d'échec** : Tester les cas de succès et d'échec pour chaque fonctionnalité

## Évolution future des tests

À mesure que l'agent Content Generator évolue, les tests devront être enrichis pour couvrir les nouvelles fonctionnalités :

1. **Génération de pages catégories** : Tests pour la génération de contenu de pages catégories
2. **Génération d'articles de blog** : Tests pour la génération d'articles de blog optimisés SEO
3. **Intégration avec le moteur de workflows** : Tests pour l'intégration avec le nouveau système d'orchestration
4. **Multilinguisme avancé** : Tests pour la génération de contenu dans plusieurs langues
5. **Optimisation de contenu avancée** : Tests pour les nouvelles fonctionnalités d'optimisation SEO

---

*Document créé le 12 mars 2025*