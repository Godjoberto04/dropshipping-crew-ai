FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances systèmes
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de l'application
COPY . /app/

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Création du répertoire de logs
RUN mkdir -p /app/logs

# Commande de démarrage
CMD ["python", "main.py"]