#!/bin/bash

# Script pour optimiser la configuration Nginx existante
# À exécuter après setup_nginx.sh

set -e  # Exit on error

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}== Optimisation de Nginx pour le dashboard de Dropshipping Crew AI ==${NC}"

# Créer un fichier de configuration pour les paramètres globaux optimisés
echo -e "${GREEN}Création de la configuration d'optimisation...${NC}"
cat > /etc/nginx/conf.d/optimize.conf << 'EOF'
# Optimisation de la mise en cache
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=dropship_cache:10m max_size=500m inactive=60m;
proxy_cache_key "$scheme$request_method$host$request_uri";
proxy_cache_valid 200 302 10m;
proxy_cache_valid 404 1m;

# Compression gzip
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

# Sécurité
server_tokens off;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header X-Frame-Options SAMEORIGIN;
EOF

# Mettre à jour la configuration du site
echo -e "${GREEN}Mise à jour de la configuration du site...${NC}"
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

    # Configuration pour servir le dashboard
    location / {
        try_files $uri $uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public, max-age=3600";
    }

    # Configuration pour les ressources statiques
    location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|otf|eot)$ {
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }

    # Configuration pour le proxy vers l'API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache dropship_cache;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Définir timeout plus long pour les opérations d'analyse
        proxy_read_timeout 300s;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
    }
    
    # Configuration pour le monitoring (optionnel - activer si besoin)
    #location /nginx_status {
    #    stub_status on;
    #    access_log off;
    #    allow 127.0.0.1;
    #    deny all;
    #}
}
EOF

# Vérifier la configuration
echo -e "${GREEN}Vérification de la configuration Nginx...${NC}"
nginx -t

# Redémarrer Nginx
echo -e "${GREEN}Redémarrage de Nginx...${NC}"
systemctl restart nginx

echo -e "${GREEN}Optimisation terminée!${NC}"
echo -e "Le dashboard optimisé est accessible à l'adresse: ${YELLOW}http://$(hostname -I | awk '{print $1}')${NC}"
echo -e "L'API est accessible à l'adresse: ${YELLOW}http://$(hostname -I | awk '{print $1}')/api/${NC}"

exit 0
