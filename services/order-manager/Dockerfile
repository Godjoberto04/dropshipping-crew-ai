FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances systèmes nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code source
COPY . .

# Exposer le port
EXPOSE 8080

# Commande de démarrage
CMD ["python", "-m", "api.app"]
