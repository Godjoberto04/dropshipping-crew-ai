"""
Configuration spécifique pour les tests de l'agent Content Generator
"""

from pathlib import Path
from pydantic import BaseSettings, Field

class TestSettings(BaseSettings):
    """
    Configuration pour l'environnement de test
    """
    # Identifiants de l'agent
    AGENT_ID: str = Field("content-generator-test", description="Identifiant unique de l'agent pour les tests")
    AGENT_VERSION: str = Field("0.1.0-test", description="Version de l'agent pour les tests")

    # Configuration API centrale
    API_BASE_URL: str = Field(
        "http://localhost:8000", 
        description="URL de base de l'API centrale pour les tests"
    )
    POLL_INTERVAL: int = Field(
        0.1, 
        description="Intervalle en secondes entre les vérifications de tâches (court pour les tests)"
    )
    ERROR_RETRY_INTERVAL: int = Field(
        0.1, 
        description="Intervalle en secondes avant réessai après erreur (court pour les tests)"
    )

    # Configuration API Claude (factice pour les tests)
    CLAUDE_API_KEY: str = Field(
        "fake-api-key-for-testing",
        description="Clé API Claude factice pour les tests"
    )
    CLAUDE_MODEL: str = Field(
        "claude-3-haiku-20240307",
        description="Modèle Claude à utiliser pour les tests"
    )
    
    # Chemins de fichiers et répertoires pour les tests
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    TEMPLATES_DIR: Path = Field(
        Path(__file__).resolve().parent / "test_templates",
        description="Répertoire des templates de contenu pour les tests"
    )
    DATA_DIR: Path = Field(
        Path(__file__).resolve().parent / "test_data",
        description="Répertoire des données de référence pour les tests"
    )
    
    # Configuration de génération
    MAX_RETRIES: int = Field(
        1, 
        description="Nombre maximum de tentatives pour les appels API (réduit pour les tests)"
    )
    DEFAULT_LANGUAGE: str = Field(
        "fr", 
        description="Langue par défaut pour la génération de contenu"
    )
    DEFAULT_TONE: str = Field(
        "persuasive", 
        description="Ton par défaut pour la génération de contenu"
    )
    
    # Limites et seuils (réduits pour les tests)
    MAX_DESCRIPTION_LENGTH: int = Field(
        500, 
        description="Longueur maximale des descriptions produits en caractères (réduite pour les tests)"
    )
    MIN_DESCRIPTION_LENGTH: int = Field(
        50, 
        description="Longueur minimale des descriptions produits en caractères (réduite pour les tests)"
    )
    
    class Config:
        """Configuration du modèle Pydantic"""
        case_sensitive = True

# Instance de configuration pour les tests
test_settings = TestSettings()