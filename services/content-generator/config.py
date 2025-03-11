"""
Configuration centralisée pour l'agent Content Generator
"""

import os
from pathlib import Path
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """
    Configuration centralisée pour l'agent Content Generator
    Utilise les variables d'environnement avec des valeurs par défaut
    """
    # Identifiants de l'agent
    AGENT_ID: str = Field("content-generator", description="Identifiant unique de l'agent")
    AGENT_VERSION: str = Field("0.1.0", description="Version de l'agent")

    # Configuration API centrale
    API_BASE_URL: str = Field(
        "http://api:8000", 
        description="URL de base de l'API centrale"
    )
    POLL_INTERVAL: int = Field(
        5, 
        description="Intervalle en secondes entre les vérifications de tâches"
    )
    ERROR_RETRY_INTERVAL: int = Field(
        30, 
        description="Intervalle en secondes avant réessai après erreur"
    )

    # Configuration API Claude
    CLAUDE_API_KEY: str = Field(
        os.getenv("CLAUDE_API_KEY", ""),
        description="Clé API Claude/Anthropic"
    )
    CLAUDE_MODEL: str = Field(
        "claude-3-haiku-20240307",
        description="Modèle Claude à utiliser"
    )
    
    # Chemins de fichiers et répertoires
    BASE_DIR: Path = Path(__file__).resolve().parent
    TEMPLATES_DIR: Path = Field(
        Path(__file__).resolve().parent / "templates",
        description="Répertoire des templates de contenu"
    )
    DATA_DIR: Path = Field(
        Path(__file__).resolve().parent / "data",
        description="Répertoire des données de référence"
    )
    
    # Configuration de génération
    MAX_RETRIES: int = Field(
        3, 
        description="Nombre maximum de tentatives pour les appels API"
    )
    DEFAULT_LANGUAGE: str = Field(
        "fr", 
        description="Langue par défaut pour la génération de contenu"
    )
    DEFAULT_TONE: str = Field(
        "persuasive", 
        description="Ton par défaut pour la génération de contenu"
    )
    
    # Limites et seuils
    MAX_DESCRIPTION_LENGTH: int = Field(
        2000, 
        description="Longueur maximale des descriptions produits en caractères"
    )
    MIN_DESCRIPTION_LENGTH: int = Field(
        300, 
        description="Longueur minimale des descriptions produits en caractères"
    )
    KEYWORD_DENSITY_TARGET: float = Field(
        0.02, 
        description="Densité cible des mots-clés (2%)"
    )
    
    # Paramètres SEO
    SEO_MIN_HEADINGS: int = Field(
        2, 
        description="Nombre minimum de titres dans le contenu"
    )
    SEO_PARAGRAPHS_MIN: int = Field(
        3, 
        description="Nombre minimum de paragraphes"
    )
    
    class Config:
        """Configuration du modèle Pydantic"""
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True


# Instance de configuration globale
settings = Settings()