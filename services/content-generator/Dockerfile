# Utiliser une image Python officielle comme base
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers de l'application
COPY . .

# Créer les répertoires nécessaires s'ils n'existent pas
RUN mkdir -p data
RUN mkdir -p logs

# Définir les variables d'environnement par défaut
# Ces valeurs peuvent être surchargées lors du démarrage du conteneur
ENV CLAUDE_API_KEY=""
ENV API_BASE_URL="http://api:8000"
ENV AGENT_ID="content-generator"
ENV AGENT_VERSION="0.1.0"
ENV POLL_INTERVAL=5
ENV DEFAULT_LANGUAGE="fr"
ENV DEFAULT_TONE="persuasive"

# Exposer le port si nécessaire pour des requêtes HTTP directes
# (Commenté car généralement les agents communiquent via l'API centrale)
# EXPOSE 8000

# Commande pour exécuter l'application
CMD ["python", "main.py"]