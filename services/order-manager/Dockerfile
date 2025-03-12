FROM python:3.9-slim

WORKDIR /app

# Installe les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie les fichiers de requirements
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Création des répertoires nécessaires
RUN mkdir -p /app/data /app/logs

# Copie du code source
COPY . .

# Exposition du port
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]