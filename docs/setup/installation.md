# Guide d'installation

Ce guide vous accompagnera à travers toutes les étapes nécessaires pour installer et configurer le système autonome de dropshipping. Assurez-vous d'avoir consulté les [prérequis](prerequisites.md) avant de commencer cette installation.

## Table des matières
1. [Préparation de l'environnement](#préparation-de-lenvironnement)
2. [Clonage du dépôt](#clonage-du-dépôt)
3. [Configuration](#configuration)
4. [Installation avec Docker](#installation-avec-docker)
5. [Installation manuelle (développement)](#installation-manuelle-développement)
6. [Vérification de l'installation](#vérification-de-linstallation)
7. [Configuration post-installation](#configuration-post-installation)
8. [Dépannage](#dépannage)

## Préparation de l'environnement

### Installation des dépendances système

Pour Ubuntu/Debian:

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances essentielles
sudo apt install -y curl git python3-pip python3-venv

# Installation de Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installation de docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Configuration des permissions Docker
sudo usermod -aG docker $USER
newgrp docker
```

Pour CentOS/RHEL:

```bash
# Mise à jour du système
sudo yum update -y

# Installation des dépendances essentielles
sudo yum install -y curl git python3-pip

# Installation de Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installation de docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Configuration des permissions Docker
sudo usermod -aG docker $USER
newgrp docker
```

### Configuration du pare-feu

```bash
# Si vous utilisez UFW (Ubuntu)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
# Optionnel: accès distant PostgreSQL
# sudo ufw allow 5432/tcp

# Si vous utilisez firewalld (CentOS)
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

## Clonage du dépôt

```bash
# Cloner le dépôt
git clone https://github.com/Godjoberto04/dropshipping-crew-ai.git
cd dropshipping-crew-ai
```

## Configuration

### Création des fichiers de configuration

```bash
# Copier les fichiers d'exemple
cp .env.example .env
cp docker-compose.override.yml.example docker-compose.override.yml
```

### Modification des fichiers de configuration

Éditez le fichier `.env` avec votre éditeur préféré:

```bash
nano .env
```

Configurez les variables suivantes:

```
# Configuration générale
DEBUG=False
SECRET_KEY=votre_clef_secrete_longue_et_aléatoire

# Base de données
DB_HOST=postgres
DB_PORT=5432
DB_NAME=dropshipping
DB_USER=dropshipping_user
DB_PASSWORD=votre_mot_de_passe_sécurisé

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=votre_mot_de_passe_redis

# API Claude
CLAUDE_API_KEY=votre_clef_api_claude

# API Shopify
SHOPIFY_API_KEY=votre_clef_api_shopify
SHOPIFY_API_SECRET=votre_secret_api_shopify
SHOPIFY_STORE_URL=votre_boutique.myshopify.com

# Autres configurations (optionnelles)
ALIEXPRESS_API_KEY=votre_clef_api_aliexpress
CJ_DROPSHIPPING_API_KEY=votre_clef_api_cj
```

## Installation avec Docker

### Lancement des services

```bash
# Construction et démarrage des conteneurs
docker-compose up -d

# Vérification que les conteneurs sont en cours d'exécution
docker-compose ps
```

### Initialisation de la base de données

```bash
# Exécution des migrations
docker-compose exec api python manage.py migrate

# Création d'un superutilisateur (pour l'accès au dashboard)
docker-compose exec api python manage.py createsuperuser
```

## Installation manuelle (développement)

Si vous préférez une installation manuelle pour le développement:

```bash
# Création d'un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sous Windows: venv\Scripts\activate

# Installation des dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configuration de la base de données locale
createdb dropshipping  # Si vous utilisez PostgreSQL
python manage.py migrate

# Lancement de l'application en mode développement
python manage.py runserver
```

## Vérification de l'installation

Après l'installation, vérifiez que les services fonctionnent correctement:

1. Accédez au dashboard à l'adresse `http://votre_serveur_ip/`
2. Vérifiez l'API à l'adresse `http://votre_serveur_ip/api/v1/system/health`
3. Accédez à la documentation de l'API à l'adresse `http://votre_serveur_ip/api/docs`

## Configuration post-installation

### Configuration de Nginx

Si vous souhaitez utiliser un nom de domaine avec HTTPS:

```bash
# Installation de Certbot pour Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx

# Obtention d'un certificat SSL
sudo certbot --nginx -d votre-domaine.com

# Vérification du renouvellement automatique
sudo certbot renew --dry-run
```

### Configuration des sauvegardes

```bash
# Création d'un script de sauvegarde
mkdir -p /path/to/backups

cat > /path/to/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql"

# Sauvegarde de la base de données
docker-compose exec -T postgres pg_dump -U $DB_USER $DB_NAME > $BACKUP_FILE

# Compression
gzip $BACKUP_FILE

# Nettoyage des anciennes sauvegardes (conservation des 7 derniers jours)
find $BACKUP_DIR -name "db_backup_*.sql.gz" -type f -mtime +7 -delete
EOF

chmod +x /path/to/backup.sh

# Ajout à cron pour exécution quotidienne
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/backup.sh") | crontab -
```

## Dépannage

Si vous rencontrez des problèmes lors de l'installation, consultez ces étapes de dépannage:

### Vérification des logs

```bash
# Affichage des logs de tous les services
docker-compose logs

# Affichage des logs d'un service spécifique
docker-compose logs api
docker-compose logs data-analyzer
```

### Problèmes courants

#### Les conteneurs ne démarrent pas

```bash
# Vérification de l'état des conteneurs
docker-compose ps -a

# Vérification des erreurs de démarrage
docker-compose logs --tail=100
```

#### Problèmes de connexion à la base de données

```bash
# Vérification que la base de données est en cours d'exécution
docker-compose exec postgres pg_isready

# Test de connexion manuelle
docker-compose exec postgres psql -U $DB_USER -d $DB_NAME
```

#### Problèmes d'accès à l'API

```bash
# Vérification que l'API est en cours d'exécution
curl http://localhost:8000/api/v1/system/health

# Vérification des logs API
docker-compose logs api
```

Pour un dépannage plus détaillé, consultez le [guide de dépannage](../troubleshooting.md).

## Prochaines étapes

Maintenant que le système est installé, vous pouvez consulter les guides d'utilisation des différents agents:

- [Agent Data Analyzer](../usage/data-analyzer.md)
- [Agent Website Builder](../usage/website-builder.md)
- [Agent Content Generator](../usage/content-generator.md)
- [Agent Order Manager](../usage/order-manager.md)
