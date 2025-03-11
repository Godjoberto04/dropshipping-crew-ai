"""
Client pour l'API Claude d'Anthropic
"""

import json
import logging
import httpx
import time
import asyncio
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger("content_generator.claude_client")

class ClaudeClient:
    """
    Client pour l'API Claude (Anthropic) utilisé pour la génération de contenu.
    Cette classe gère les appels à l'API Claude, la gestion des prompts, et le formatage des réponses.
    """
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "claude-3-haiku-20240307",
        max_retries: int = 3,
        timeout: int = 120
    ):
        """
        Initialise le client Claude.
        
        Args:
            api_key: Clé API Anthropic
            model: Identifiant du modèle Claude à utiliser
            max_retries: Nombre maximum de tentatives en cas d'erreur
            timeout: Délai d'attente maximum en secondes pour les appels API
        """
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        self.api_url = "https://api.anthropic.com/v1/messages"
        
        if not self.api_key:
            logger.warning("Aucune clé API Claude fournie. Le client fonctionnera en mode simulation.")
        
        logger.info(f"Client Claude initialisé (modèle: {model})")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        json_response: bool = False
    ) -> str:
        """
        Génère du contenu en utilisant l'API Claude.
        
        Args:
            prompt: Prompt principal pour Claude
            system_prompt: Prompt système pour guider le comportement (facultatif)
            temperature: Contrôle de la créativité (0.0-1.0)
            max_tokens: Nombre maximum de tokens dans la réponse
            json_response: Si True, demande une réponse au format JSON
            
        Returns:
            Le contenu généré par Claude
        """
        # Mode simulation si pas de clé API
        if not self.api_key:
            logger.warning("Génération en mode simulation (pas de clé API)")
            return self._simulate_response(prompt, json_response)
        
        # Construction de la requête
        headers = {
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "x-api-key": self.api_key,
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Ajout du prompt système si fourni
        if system_prompt:
            payload["system"] = system_prompt
        
        # Spécifier le format JSON si demandé
        if json_response:
            payload["response_format"] = {"type": "json_object"}
        
        # Envoi de la requête avec gestion des erreurs et retries
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    logger.debug(f"Envoi de la requête à Claude (taille du prompt: {len(prompt)} caractères)")
                    start_time = time.time()
                    
                    response = await client.post(
                        self.api_url,
                        headers=headers,
                        json=payload
                    )
                    
                    duration = time.time() - start_time
                    logger.debug(f"Réponse reçue en {duration:.2f}s")
                    
                    # Vérification du code de statut
                    response.raise_for_status()
                    
                    # Analyse de la réponse
                    response_data = response.json()
                    
                    # Extraction du contenu généré
                    generated_content = response_data["content"][0]["text"]
                    
                    return generated_content
                    
            except httpx.HTTPStatusError as e:
                retry_count += 1
                wait_time = 2 ** retry_count  # Backoff exponentiel
                
                if retry_count >= self.max_retries:
                    logger.error(f"Échec de la requête après {self.max_retries} tentatives: {str(e)}")
                    raise
                
                logger.warning(f"Erreur HTTP {e.response.status_code}, nouvelle tentative dans {wait_time}s...")
                await asyncio.sleep(wait_time)
                
            except httpx.RequestError as e:
                retry_count += 1
                wait_time = 2 ** retry_count
                
                if retry_count >= self.max_retries:
                    logger.error(f"Échec de la connexion après {self.max_retries} tentatives: {str(e)}")
                    raise
                
                logger.warning(f"Erreur de connexion, nouvelle tentative dans {wait_time}s...")
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"Erreur inattendue: {str(e)}")
                raise
    
    def _simulate_response(self, prompt: str, json_format: bool = False) -> str:
        """
        Simule une réponse de Claude lorsque l'API n'est pas disponible.
        Utilisé principalement pour les tests et le développement.
        
        Args:
            prompt: Le prompt fourni
            json_format: Si True, renvoie une réponse au format JSON
            
        Returns:
            Une réponse simulée
        """
        logger.info("Génération d'une réponse simulée")
        
        # Détection si c'est une demande de description produit
        if "description" in prompt.lower() and "produit" in prompt.lower():
            if json_format:
                return json.dumps({
                    "description": "Ceci est une description de produit simulée. Ce produit innovant combine fonctionnalité et style pour répondre à vos besoins quotidiens. Fabriqué avec des matériaux de haute qualité, il est conçu pour durer et offrir une expérience utilisateur exceptionnelle.",
                    "metadata": {
                        "tone": "persuasive",
                        "word_count": 42,
                        "seo_score": 85
                    }
                })
            else:
                return """
                # Produit Innovant de Qualité Supérieure
                
                Découvrez notre produit innovant, conçu pour transformer votre expérience quotidienne. Alliant fonctionnalité et élégance, ce produit deviendra rapidement indispensable dans votre vie.
                
                ## Caractéristiques principales
                
                * Matériaux premium pour une durabilité exceptionnelle
                * Design ergonomique pour un confort optimal
                * Fonctionnalités avancées qui simplifient votre quotidien
                * Fabriqué selon des normes environnementales strictes
                
                Ne vous contentez plus de l'ordinaire quand l'extraordinaire est à portée de main.
                """
        else:
            if json_format:
                return json.dumps({
                    "content": "Ceci est une réponse simulée pour le développement. En production, cette réponse proviendrait directement de l'API Claude.",
                    "metadata": {
                        "simulation": True,
                        "prompt_length": len(prompt)
                    }
                })
            else:
                return "Ceci est une réponse simulée pour le développement. En production, cette réponse proviendrait directement de l'API Claude."