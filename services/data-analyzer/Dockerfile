# Utiliser une image Python officielle
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code source
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p logs data cache

# Exposer le port si nécessaire pour les besoins futurs
# EXPOSE 8000

# Définir les variables d'environnement
ENV PYTHONUNBUFFERED=1

# Commande d'entrée
CMD ["python", "main.py"]
