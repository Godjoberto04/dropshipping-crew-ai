# Vue d'ensemble des tests unitaires et d'intégration

## Introduction

La qualité et la fiabilité du système Dropshipping Crew AI reposent fortement sur une stratégie de test complète. Cette documentation présente l'approche de test adoptée pour le projet, les outils utilisés, et comment exécuter et étendre les tests existants.

## Philosophie de test

Notre approche de test suit plusieurs principes clés :

1. **Tests automatisés** : Tous les tests doivent être automatisés pour permettre une intégration continue.
2. **Couverture complète** : Viser un taux de couverture de code d'au moins 85% pour le code de production.
3. **Isolation** : Les tests unitaires doivent tester des composants isolés sans dépendances externes.
4. **Mocking intelligent** : Utiliser des mocks et des stubs pour simuler les dépendances externes.
5. **Tests d'intégration** : Valider les interactions entre les composants et avec les API externes.
6. **Tests de bout en bout** : Confirmer que le système fonctionne correctement dans son ensemble.

## Structure des tests

Les tests suivent une structure cohérente dans chaque service du projet :

```
services/
  └── [service-name]/
      ├── app/
      │   └── [code source]
      └── tests/
          ├── unit/            # Tests unitaires isolés
          │   ├── test_models.py
          │   ├── test_utils.py
          │   └── ...
          ├── integration/     # Tests d'intégration
          │   ├── test_api.py
          │   ├── test_database.py
          │   └── ...
          ├── e2e/             # Tests de bout en bout
          │   └── test_workflows.py
          ├── fixtures/        # Données de test réutilisables
          │   ├── mock_data.py
          │   └── ...
          └── conftest.py      # Configuration et fixtures pytest
```

## Outils et frameworks de test

Le projet utilise les outils suivants pour les tests :

| Outil | Objectif |
|-------|----------|
| **pytest** | Framework de test principal |
| **pytest-cov** | Mesure de la couverture de code |
| **pytest-mock** | Création de mocks et stubs |
| **pytest-asyncio** | Tests de code asynchrone |
| **requests-mock** | Simulation des réponses API externes |
| **factory-boy** | Génération de données de test |
| **Faker** | Création de données aléatoires réalistes |
| **Pydantic** | Validation des modèles de données |

## Types de tests

### Tests unitaires

Les tests unitaires vérifient le comportement des plus petites unités de code (fonctions, classes) en isolation.

Exemple de test unitaire pour un service :

```python
# tests/unit/test_product_service.py
import pytest
from app.services.product_service import calculate_profit_margin

def test_calculate_profit_margin():
    # Given
    cost_price = 10.0
    selling_price = 25.0
    
    # When
    margin = calculate_profit_margin(cost_price, selling_price)
    
    # Then
    assert margin == 0.6  # 60% margin
    
def test_calculate_profit_margin_zero_cost():
    # Given
    cost_price = 0
    selling_price = 25.0
    
    # When/Then
    with pytest.raises(ValueError):
        calculate_profit_margin(cost_price, selling_price)
```

### Tests d'intégration

Les tests d'intégration vérifient les interactions entre plusieurs composants, y compris les bases de données et les API.

Exemple de test d'intégration pour l'API :

```python
# tests/integration/test_order_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_order(mock_database, mock_supplier_api):
    # Given
    order_data = {
        "customer_id": "cust_123456",
        "products": [
            {"product_id": "prod_123", "quantity": 2}
        ],
        "shipping_address": {
            "name": "Jean Dupont",
            "address": "123 Rue des Exemples",
            "city": "Paris",
            "zip": "75001",
            "country": "France"
        }
    }
    
    # When
    response = client.post("/api/orders", json=order_data)
    
    # Then
    assert response.status_code == 201
    data = response.json()
    assert "order_id" in data
    assert mock_supplier_api.called
```

### Tests de bout en bout (E2E)

Les tests E2E vérifient les workflows complets du système, simulant des scénarios réels d'utilisation.

Exemple de test E2E :

```python
# tests/e2e/test_order_workflow.py
import pytest
import requests
import time

@pytest.mark.e2e
def test_complete_order_workflow():
    # 1. Create product via Data Analyzer
    product_response = requests.post(
        "http://api-gateway/data-analyzer/products/analyze",
        json={"product_url": "https://example.com/sample-product"}
    )
    assert product_response.status_code == 200
    product_data = product_response.json()
    
    # 2. Add product to website via Website Builder
    website_response = requests.post(
        "http://api-gateway/website-builder/products",
        json=product_data
    )
    assert website_response.status_code == 201
    product_id = website_response.json()["product_id"]
    
    # 3. Create a test order
    order_response = requests.post(
        "http://api-gateway/order-manager/orders/test",
        json={
            "product_id": product_id,
            "quantity": 1,
            "customer": {
                "email": "test@example.com",
                "name": "Test Customer"
            }
        }
    )
    assert order_response.status_code == 201
    order_id = order_response.json()["order_id"]
    
    # 4. Wait for order processing
    time.sleep(5)
    
    # 5. Verify order status
    status_response = requests.get(
        f"http://api-gateway/order-manager/orders/{order_id}"
    )
    assert status_response.status_code == 200
    order_data = status_response.json()
    assert order_data["status"] == "processing"
```

## Mocking et fixtures

Pour simuler les dépendances externes, nous utilisons des mocks et des fixtures :

```python
# tests/conftest.py
import pytest
import mongomock
import redis
from unittest.mock import Mock

@pytest.fixture
def mock_mongodb():
    """Fixture pour simuler MongoDB"""
    return mongomock.MongoClient()

@pytest.fixture
def mock_redis():
    """Fixture pour simuler Redis"""
    redis_mock = Mock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    return redis_mock

@pytest.fixture
def mock_shopify_api():
    """Fixture pour simuler l'API Shopify"""
    shopify_mock = Mock()
    shopify_mock.get_products.return_value = [
        {"id": "prod1", "title": "Product 1", "price": "19.99"}
    ]
    shopify_mock.create_order.return_value = {
        "id": "order1", 
        "status": "created"
    }
    return shopify_mock
```

## Exécution des tests

### Tests unitaires et d'intégration

Pour exécuter les tests unitaires et d'intégration pour un service spécifique :

```bash
cd services/[service-name]
python -m pytest tests/unit tests/integration -v
```

Pour exécuter avec la couverture de code :

```bash
python -m pytest tests/unit tests/integration --cov=app --cov-report=term --cov-report=html
```

### Tests de bout en bout

Pour exécuter les tests E2E (nécessite que les services soient en cours d'exécution) :

```bash
python -m pytest tests/e2e -v
```

### Tests dans l'environnement Docker

Vous pouvez également exécuter les tests dans l'environnement Docker à l'aide de la commande suivante :

```bash
docker-compose -f docker-compose.test.yml up --build
```

## État actuel de la couverture des tests

| Service | Couverture globale | Tests unitaires | Tests d'intégration | Tests E2E |
|---------|-------------------|-----------------|---------------------|-----------|
| **Data Analyzer** | 87% | 92% | 83% | 75% |
| **Website Builder** | 82% | 89% | 78% | 70% |
| **Content Generator** | 85% | 91% | 81% | 72% |
| **Order Manager** | 89% | 94% | 85% | 78% |
| **API Orchestrator** | 83% | 88% | 80% | 69% |

## Bonnes pratiques pour l'écriture des tests

### 1. Structure AAA (Arrange, Act, Assert)

Organisez vos tests selon le modèle AAA :

```python
def test_something():
    # Arrange (Given) - Préparer les données et conditions
    user = User(name="Test User", email="test@example.com")
    
    # Act (When) - Exécuter l'action à tester
    result = user.generate_profile_url()
    
    # Assert (Then) - Vérifier le résultat
    assert result == "https://example.com/users/test-user"
```

### 2. Noms de tests descriptifs

Utilisez des noms de tests qui décrivent clairement le scénario et le résultat attendu :

```python
def test_calculate_total_price_applies_discount_when_order_above_threshold():
    # Test content
```

### 3. Isolation des tests

Assurez-vous que chaque test est indépendant et peut s'exécuter seul :

```python
@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup - avant chaque test
    setup_test_database()
    
    yield  # Exécution du test
    
    # Teardown - après chaque test
    clean_test_database()
```

### 4. Évitez la logique conditionnelle dans les tests

Les tests doivent être déterministes et éviter les conditions :

```python
# Mauvais
def test_search():
    result = search_products("phone")
    if len(result) > 0:
        assert result[0].category == "Electronics"
    else:
        assert True  # Évitez ce type de pattern

# Bon
def test_search_returns_electronics_category():
    result = search_products("phone")
    assert len(result) > 0
    assert result[0].category == "Electronics"
```

## Tests de performance

En plus des tests fonctionnels, nous effectuons des tests de performance pour assurer que le système répond aux exigences de charge :

### Tests de charge avec Locust

```python
# locustfile.py
from locust import HttpUser, task, between

class ShopifyUser(HttpUser):
    wait_time = between(1, 5)
    
    @task(2)
    def view_products(self):
        self.client.get("/api/products")
    
    @task(1)
    def create_order(self):
        self.client.post("/api/orders", json={
            # Order data here
        })
```

Pour exécuter les tests de charge :

```bash
locust -f locustfile.py --host=http://your-api-server
```

## Intégration continue

Les tests sont intégrés dans notre pipeline CI/CD avec GitHub Actions :

```yaml
# .github/workflows/test.yml
name: Run Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest tests/unit tests/integration --cov=app
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v2
```

## Comment contribuer aux tests

1. **Maintenir les tests existants** : Mettez à jour les tests lorsque vous modifiez le code.
2. **Ajouter des tests pour les nouvelles fonctionnalités** : Tout nouveau code doit être accompagné de tests.
3. **Corriger les tests défectueux** : Si un test échoue après une modification légitime, mettez-le à jour.
4. **Améliorer la couverture** : Identifiez les zones faiblement couvertes et ajoutez des tests.

## Ressources pour les tests

- [Documentation Pytest](https://docs.pytest.org/)
- [Guide des meilleures pratiques pour les tests Python](https://docs.python-guide.org/writing/tests/)
- [Tutoriel FastAPI TestClient](https://fastapi.tiangolo.com/tutorial/testing/)
- [Factory Boy avec Pytest](https://factoryboy.readthedocs.io/en/stable/index.html)

## Conclusion

Une stratégie de test robuste est essentielle pour maintenir la qualité et la fiabilité du système Dropshipping Crew AI. En suivant les bonnes pratiques décrites dans ce document, nous pouvons garantir que notre système fonctionne correctement, est résilient face aux erreurs et peut évoluer avec confiance.
