#!/usr/bin/env python3
"""
Configuration de l'agent Data Analyzer.
Gère les paramètres et variables d'environnement nécessaires au fonctionnement de l'agent.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

class Settings(BaseSettings):
    """Paramètres de configuration pour l'agent Data Analyzer."""
    
    # Informations de l'agent
    AGENT_ID: str = Field(default="data-analyzer", description="Identifiant unique de l'agent")
    AGENT_VERSION: str = Field(default="2.0.0", description="Version de l'agent")
    
    # Configuration de l'API
    API_BASE_URL: str = Field(
        default=os.getenv("API_BASE_URL", "http://api:8000"),
        description="URL de base de l'API centrale"
    )
    
    # Intervalles
    POLL_INTERVAL: int = Field(
        default=int(os.getenv("POLL_INTERVAL", "10")),
        description="Intervalle (en secondes) entre chaque vérification de tâches"
    )
    ERROR_RETRY_INTERVAL: int = Field(
        default=int(os.getenv("ERROR_RETRY_INTERVAL", "30")),
        description="Intervalle (en secondes) avant de réessayer après une erreur"
    )
    
    # Configuration des fonctionnalités
    ENABLE_TRENDS_ANALYSIS: bool = Field(
        default=os.getenv("ENABLE_TRENDS_ANALYSIS", "True").lower() in ("true", "1", "t"),
        description="Activer l'analyse des tendances via Google Trends"
    )
    ENABLE_MARKETPLACE_ANALYSIS: bool = Field(
        default=os.getenv("ENABLE_MARKETPLACE_ANALYSIS", "True").lower() in ("true", "1", "t"),
        description="Activer l'analyse des marketplaces"
    )
    ENABLE_SOCIAL_ANALYSIS: bool = Field(
        default=os.getenv("ENABLE_SOCIAL_ANALYSIS", "False").lower() in ("true", "1", "t"),
        description="Activer l'analyse des réseaux sociaux"
    )
    
    # Paramètres PyTrends
    PYTRENDS_HL: str = Field(
        default=os.getenv("PYTRENDS_HL", "fr"),
        description="Langue pour Google Trends (fr, en-US, etc.)"
    )
    PYTRENDS_TZ: int = Field(
        default=int(os.getenv("PYTRENDS_TZ", "0")),
        description="Fuseau horaire pour Google Trends (-360 à 360)"
    )
    PYTRENDS_GEO: str = Field(
        default=os.getenv("PYTRENDS_GEO", "FR"),
        description="Pays par défaut pour Google Trends (FR, US, etc.)"
    )
    PYTRENDS_TIMEFRAMES: Dict[str, str] = Field(
        default={
            "short_term": "now 7-d",
            "medium_term": "today 3-m",
            "long_term": "today 12-m",
            "five_years": "today 5-y"
        },
        description="Périodes disponibles pour l'analyse de tendances"
    )
    
    # Proxy configuration (optionnel)
    PROXY_ENABLED: bool = Field(
        default=os.getenv("PROXY_ENABLED", "False").lower() in ("true", "1", "t"),
        description="Activer l'utilisation d'un proxy pour les requêtes"
    )
    PROXY_URL: Optional[str] = Field(
        default=os.getenv("PROXY_URL", None),
        description="URL du proxy (ex: http://user:pass@host:port)"
    )
    
    # Thresholds for scoring
    SCORING_THRESHOLDS: Dict[str, int] = Field(
        default={
            "high_potential": 75,
            "medium_potential": 60,
            "low_potential": 40
        },
        description="Seuils pour la classification des scores"
    )
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent
    DATA_DIR: Path = Field(default=BASE_DIR / "data")
    CACHE_DIR: Path = Field(default=BASE_DIR / "cache")
    
    class Config:
        """Configuration pour Pydantic."""
        env_file = ".env"

# Instance de configuration unique
settings = Settings()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join("logs", f"data_analyzer.log"))
    ]
)

# Création des répertoires nécessaires
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.CACHE_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    """
    Récupère un logger configuré.
    
    Args:
        name: Nom du logger
        
    Returns:
        Logger configuré
    """
    return logging.getLogger(name)
