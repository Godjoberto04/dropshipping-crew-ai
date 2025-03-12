# Tests unitaires pour l'agent Content Generator

Ce répertoire contient les tests unitaires pour l'agent Content Generator.

## Structure

```
tests/
├── __init__.py
├── README.md
├── test_product_description.py - Tests pour le générateur de descriptions produit
├── test_seo_optimizer.py      - Tests pour l'optimiseur SEO
├── test_claude_client.py      - Tests pour le client Claude
└── test_main.py               - Tests d'intégration pour l'agent
```

## Exécution des tests

Pour exécuter tous les tests :

```bash
python -m pytest
```

Pour exécuter un fichier de test spécifique :

```bash
python -m pytest tests/test_product_description.py
```

Pour exécuter un test spécifique :

```bash
python -m pytest tests/test_product_description.py::test_format_product_info
```

## Mocks

Les tests utilisent des mocks pour simuler les dépendances externes (API Claude, API centrale, etc.) afin d'isoler les composants et d'éviter de faire des appels réels pendant les tests.

## Configuration de test

Les tests utilisent un fichier de configuration spécifique pour l'environnement de test (`test_config.py`) qui surcharge certains paramètres pour faciliter les tests.