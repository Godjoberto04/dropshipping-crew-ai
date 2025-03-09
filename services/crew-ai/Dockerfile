FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    unzip \
    ca-certificates \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Utiliser Playwright au lieu de Selenium (plus simple à installer dans Docker)
ENV PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir playwright && \
    playwright install --with-deps chromium

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer le répertoire pour les logs
RUN mkdir -p /app/logs && touch /app/data_analyzer.log && chmod 777 /app/data_analyzer.log

# Commande de démarrage
CMD ["python", "main.py"]
