#!/bin/bash

# Script pour optimiser Nginx pour le dashboard de Dropshipping Crew AI
# À exécuter avec les privilèges root ou sudo

set -e  # Exit on error

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}== Optimisation de Nginx pour le dashboard de Dropshipping Crew AI ==${NC}"

# Vérifier si Nginx est installé
if ! command -v nginx &> /dev/null; then
    echo -e "${RED}Nginx n'est pas installé. Veuillez d'abord exécuter setup_nginx.sh${NC}"
    exit 1
fi

# Créer un dossier de cache pour Nginx
echo -e "${GREEN}Création du dossier de cache...${NC}"
mkdir -p /var/cache/nginx
chown -R www-data:www-data /var/cache/nginx

# Créer une configuration optimisée pour Nginx
echo -e "${GREEN}Création de la configuration optimisée...${NC}"
cat > /etc/nginx/conf.d/performance.conf << 'EOF'
# Optimisation de la performance Nginx

# Compression Gzip
gzip on;
gzip_comp_level 5;
gzip_min_length 256;
gzip_proxied any;
gzip_vary on;
gzip_types
  application/javascript
  application/json
  application/x-javascript
  application/xml
  application/xml+rss
  text/css
  text/javascript
  text/plain
  text/xml;

# Cache des fichiers statiques
open_file_cache max=1000 inactive=20s;
open_file_cache_valid 30s;
open_file_cache_min_uses 2;
open_file_cache_errors on;

# Optimisation des tampons
client_body_buffer_size 10K;
client_header_buffer_size 1k;
client_max_body_size 8m;
large_client_header_buffers 4 4k;

# Timeouts
client_body_timeout 12;
client_header_timeout 12;
keepalive_timeout 15;
send_timeout 10;

# Cache pour les assets statiques
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=STATIC:10m inactive=24h max_size=1g;
EOF

# Optimiser la configuration principale de Nginx
echo -e "${GREEN}Optimisation de la configuration principale...${NC}"
# Sauvegarder la configuration actuelle
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak

# Créer une nouvelle configuration avec plus de workers
cat > /etc/nginx/nginx.conf << 'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 1024;
    multi_accept on;
    use epoll;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF

# Optimiser la configuration du site
echo -e "${GREEN}Optimisation de la configuration du site...${NC}"
cat > /etc/nginx/sites-available/dropship-dashboard << 'EOF'
server {
    listen 80;
    server_name _; # Remplacer par votre nom de domaine si disponible

    # Journalisation
    access_log /var/log/nginx/dropship.access.log;
    error_log /var/log/nginx/dropship.error.log;

    # Racine pour les fichiers statiques du dashboard
    root /var/www/html/dashboard;
    index index.html;

    # Optimisation des caches et expirations
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Configuration pour servir le dashboard
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Configuration pour le proxy vers l'API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache STATIC;
        proxy_cache_valid 200 1h;
        proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
    }
}
EOF

# Créer un lien symbolique pour activer la configuration (au cas où il n'existerait pas)
echo -e "${GREEN}Activation de la configuration...${NC}"
ln -sf /etc/nginx/sites-available/dropship-dashboard /etc/nginx/sites-enabled/

# Supprimer la configuration par défaut (si elle existe encore)
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm -f /etc/nginx/sites-enabled/default
fi

# Vérifier la configuration
echo -e "${GREEN}Vérification de la configuration Nginx...${NC}"
nginx -t

# Redémarrer Nginx
echo -e "${GREEN}Redémarrage de Nginx...${NC}"
systemctl restart nginx

echo -e "${GREEN}Optimisation de Nginx terminée!${NC}"
echo -e "Vous pouvez accéder au dashboard à l'adresse: ${YELLOW}http://$(hostname -I | awk '{print $1}')${NC}"
echo -e "L'API est accessible à l'adresse: ${YELLOW}http://$(hostname -I | awk '{print $1}')/api/${NC}"

exit 0
