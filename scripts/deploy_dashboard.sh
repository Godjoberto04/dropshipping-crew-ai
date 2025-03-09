#!/bin/bash

# Script pour déployer le dashboard sur le serveur via Nginx
# À exécuter avec les privilèges root ou sudo

set -e  # Exit on error

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}== Déploiement du dashboard de Dropshipping Crew AI ==${NC}"

# Vérifier si Nginx est installé
if ! command -v nginx &> /dev/null; then
    echo -e "${YELLOW}Nginx n'est pas installé. Installation en cours...${NC}"
    apt update
    apt install -y nginx
    echo -e "${GREEN}Nginx installé avec succès.${NC}"
else
    echo -e "${GREEN}Nginx est déjà installé.${NC}"
fi

# Configurer le pare-feu (si UFW est installé)
if command -v ufw &> /dev/null; then
    echo -e "${GREEN}Configuration du pare-feu...${NC}"
    ufw allow 'Nginx HTTP'
    ufw allow 'Nginx HTTPS'
    echo -e "${GREEN}Pare-feu configuré.${NC}"
fi

# Créer le répertoire pour le dashboard
echo -e "${GREEN}Création du répertoire pour le dashboard...${NC}"
mkdir -p /var/www/html/dashboard/{css,js}

# Définir les permissions correctes
echo -e "${GREEN}Configuration des permissions...${NC}"
chown -R www-data:www-data /var/www/html/dashboard
chmod -R 755 /var/www/html

# Copier les fichiers du dashboard
echo -e "${GREEN}Copie des fichiers du dashboard...${NC}"
if [ -d "/opt/dropship-crew-ai/services/dashboard" ]; then
    cp -r /opt/dropship-crew-ai/services/dashboard/* /var/www/html/dashboard/
    echo -e "${GREEN}Fichiers copiés avec succès.${NC}"
else
    echo -e "${YELLOW}Répertoire source du dashboard non trouvé. Création d'un fichier HTML de base...${NC}"
    
    # Créer un fichier HTML basique pour le dashboard
    cat > /var/www/html/dashboard/index.html << 'EOF'
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dropshipping Autonome - Dashboard</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">Dropshipping Autonome</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="#" id="refreshStatus">
                            <i class="bi bi-arrow-clockwise"></i> Rafraîchir
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row mb-4">
            <div class="col">
                <h1>Tableau de bord</h1>
                <p class="text-muted">Statut du système de dropshipping autonome avec Crew AI</p>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        Statut du système
                    </div>
                    <div class="card-body">
                        <div class="row" id="servicesStatus">
                            <div class="col-12">
                                <div class="d-flex justify-content-center">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">Chargement...</span>
                                    </div>
                                </div>
                                <p class="text-center mt-2">Chargement du statut des services...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        Performances du serveur
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">CPU</label>
                            <div class="progress">
                                <div class="progress-bar" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Mémoire</label>
                            <div class="progress">
                                <div class="progress-bar bg-info" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Disque</label>
                            <div class="progress">
                                <div class="progress-bar bg-warning" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        Analyse de marché
                    </div>
                    <div class="card-body">
                        <form id="analysisForm" class="mb-4">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="urls" class="form-label">URLs à analyser</label>
                                        <textarea class="form-control" id="urls" rows="3" placeholder="https://example-shop.com/category/accessories&#10;https://another-shop.com/bestsellers"></textarea>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="marketSegment" class="form-label">Segment de marché (optionnel)</label>
                                        <input type="text" class="form-control" id="marketSegment" placeholder="Ex: smartphone accessories">
                                    </div>
                                    <div class="d-grid gap-2">
                                        <button type="submit" class="btn btn-primary" id="runAnalysisBtn">
                                            <span class="spinner-border spinner-border-sm d-none" role="status" aria-hidden="true" id="analysisSpinner"></span>
                                            Lancer l'analyse
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </form>
                        <div id="analysisResults">
                            <div class="alert alert-info">
                                Aucune analyse n'a encore été effectuée. Utilisez le formulaire ci-dessus pour lancer une analyse.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="js/dashboard.js"></script>
</body>
</html>
EOF

    # Créer le fichier CSS pour le dashboard
    mkdir -p /var/www/html/dashboard/css
    cat > /var/www/html/dashboard/css/style.css << 'EOF'
.status-card {
    transition: all 0.3s ease;
}
.status-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.status-online {
    border-left: 5px solid #198754;
}
.status-partial {
    border-left: 5px solid #ffc107;
}
.status-offline {
    border-left: 5px solid #dc3545;
}
.card-header {
    font-weight: bold;
}
EOF

    # Créer le fichier JavaScript pour le dashboard
    mkdir -p /var/www/html/dashboard/js
    cat > /var/www/html/dashboard/js/dashboard.js << 'EOF'
document.addEventListener('DOMContentLoaded', function() {
    // Charger le statut initial du système
    fetchSystemStatus();
    
    // Configurer le bouton de rafraîchissement
    document.getElementById('refreshStatus').addEventListener('click', function(e) {
        e.preventDefault();
        fetchSystemStatus();
    });
    
    // Configurer le formulaire d'analyse
    document.getElementById('analysisForm').addEventListener('submit', function(e) {
        e.preventDefault();
        runAnalysis();
    });
});

// Fonction pour récupérer le statut du système
function fetchSystemStatus() {
    fetch('/api/status')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération du statut');
            }
            return response.json();
        })
        .then(data => {
            updateStatusCards(data);
            updateSystemPerformance(data.system);
        })
        .catch(error => {
            console.error('Erreur:', error);
            // Afficher une erreur à l'utilisateur
            const servicesStatus = document.getElementById('servicesStatus');
            servicesStatus.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger">
                        Impossible de récupérer le statut du système. L'API semble inaccessible.
                    </div>
                </div>
            `;
        });
}

// Fonction pour mettre à jour les cartes de statut
function updateStatusCards(data) {
    const servicesStatus = document.getElementById('servicesStatus');
    servicesStatus.innerHTML = '';
    
    for (const [service, info] of Object.entries(data.services)) {
        let statusClass = 'status-offline';
        if (info.status === 'online') {
            statusClass = 'status-online';
        } else if (info.status === 'partial') {
            statusClass = 'status-partial';
        }
        
        const statusText = info.status === 'online' ? 'En ligne' : 
                         info.status === 'partial' ? 'Partiellement implémenté' : 'Hors ligne';
        
        const version = info.version ? `v${info.version}` : '';
        
        servicesStatus.innerHTML += `
            <div class="col-md-6 mb-3">
                <div class="card status-card ${statusClass}">
                    <div class="card-body">
                        <h5 class="card-title">${service.charAt(0).toUpperCase() + service.slice(1)}</h5>
                        <p class="card-text">${statusText} ${version}</p>
                    </div>
                </div>
            </div>
        `;
    }
}

// Fonction pour mettre à jour les performances du système
function updateSystemPerformance(system) {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars[0].style.width = `${system.cpu_usage}%`;
    progressBars[0].textContent = `${system.cpu_usage}%`;
    progressBars[0].setAttribute('aria-valuenow', system.cpu_usage);
    
    progressBars[1].style.width = `${system.memory_usage}%`;
    progressBars[1].textContent = `${system.memory_usage}%`;
    progressBars[1].setAttribute('aria-valuenow', system.memory_usage);
    
    progressBars[2].style.width = `${system.disk_usage}%`;
    progressBars[2].textContent = `${system.disk_usage}%`;
    progressBars[2].setAttribute('aria-valuenow', system.disk_usage);
}

// Fonction pour lancer une analyse
function runAnalysis() {
    const urlsText = document.getElementById('urls').value;
    const marketSegment = document.getElementById('marketSegment').value;
    
    // Validation de base
    if (!urlsText.trim()) {
        alert('Veuillez entrer au moins une URL à analyser');
        return;
    }
    
    // Préparer les données
    const urls = urlsText.split('\n').filter(url => url.trim() !== '');
    const requestData = { urls: urls };
    
    // Afficher le spinner
    const spinner = document.getElementById('analysisSpinner');
    const button = document.getElementById('runAnalysisBtn');
    spinner.classList.remove('d-none');
    button.disabled = true;
    
    // Mise à jour de l'UI pour indiquer que l'analyse est en cours
    const analysisResults = document.getElementById('analysisResults');
    analysisResults.innerHTML = `
        <div class="alert alert-warning">
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                <div>
                    <strong>Analyse en cours...</strong><br>
                    Analyse de ${urls.length} URLs. Cette opération peut prendre plusieurs minutes.
                </div>
            </div>
        </div>
    `;
    
    // Appel à l'API pour lancer l'analyse
    fetch('/api/agents/data-analyzer/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Stocker l'ID de la tâche et démarrer le polling
        const taskId = data.task_id;
        pollTaskStatus(taskId);
    })
    .catch(error => {
        console.error('Erreur:', error);
        analysisResults.innerHTML = `
            <div class="alert alert-danger">
                <strong>Erreur!</strong> Impossible de lancer l'analyse: ${error.message}
            </div>
        `;
        spinner.classList.add('d-none');
        button.disabled = false;
    });
}

// Fonction pour vérifier l'état d'une tâche périodiquement
function pollTaskStatus(taskId) {
    const spinner = document.getElementById('analysisSpinner');
    const button = document.getElementById('runAnalysisBtn');
    const analysisResults = document.getElementById('analysisResults');
    
    let pollInterval = 5000; // 5 secondes
    
    // Fonction récursive pour le polling
    function checkStatus() {
        fetch(`/api/tasks/${taskId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(taskStatus => {
                // Mettre à jour la barre de progression
                analysisResults.innerHTML = `
                    <div class="alert alert-warning">
                        <strong>Analyse en cours: ${taskStatus.progress}%</strong><br>
                        ${taskStatus.message}
                    </div>
                    <div class="progress">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                            role="progressbar" 
                            style="width: ${taskStatus.progress}%" 
                            aria-valuenow="${taskStatus.progress}" 
                            aria-valuemin="0" 
                            aria-valuemax="100">
                            ${taskStatus.progress}%
                        </div>
                    </div>
                `;
                
                // Vérifier si la tâche est terminée
                if (taskStatus.status === 'completed') {
                    // Récupérer les résultats
                    fetchAnalysisResults();
                } else {
                    // Continuer le polling
                    setTimeout(checkStatus, pollInterval);
                    
                    // Ajuster l'intervalle de polling en fonction de la progression
                    if (taskStatus.progress > 90) {
                        pollInterval = 1000; // 1 seconde
                    } else if (taskStatus.progress > 50) {
                        pollInterval = 3000; // 3 secondes
                    }
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                analysisResults.innerHTML = `
                    <div class="alert alert-danger">
                        <strong>Erreur!</strong> Impossible de récupérer l'état de l'analyse: ${error.message}
                    </div>
                `;
                spinner.classList.add('d-none');
                button.disabled = false;
            });
    }
    
    // Démarrer le polling
    checkStatus();
}

// Fonction pour récupérer les résultats d'analyse
function fetchAnalysisResults() {
    const spinner = document.getElementById('analysisSpinner');
    const button = document.getElementById('runAnalysisBtn');
    const analysisResults = document.getElementById('analysisResults');
    
    fetch('/api/analysis/results/latest')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(results => {
            // Afficher les résultats
            displayAnalysisResults(results);
        })
        .catch(error => {
            console.error('Erreur:', error);
            analysisResults.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Erreur!</strong> Impossible de récupérer les résultats de l'analyse: ${error.message}
                </div>
            `;
        })
        .finally(() => {
            // Masquer le spinner et réactiver le bouton
            spinner.classList.add('d-none');
            button.disabled = false;
        });
}

// Fonction pour afficher les résultats d'analyse
function displayAnalysisResults(results) {
    const analysisResults = document.getElementById('analysisResults');
    
    let productsHtml = '';
    results.top_products.forEach(product => {
        let trendBadge = '';
        if (product.trend_direction === 'Up') {
            trendBadge = '<span class="badge bg-success">↑ En hausse</span>';
        } else if (product.trend_direction === 'Down') {
            trendBadge = '<span class="badge bg-danger">↓ En baisse</span>';
        } else {
            trendBadge = '<span class="badge bg-secondary">→ Stable</span>';
        }
        
        let competitionBadge = '';
        if (product.competition_level === 'Low') {
            competitionBadge = '<span class="badge bg-success">Faible</span>';
        } else if (product.competition_level === 'Medium') {
            competitionBadge = '<span class="badge bg-warning text-dark">Moyenne</span>';
        } else {
            competitionBadge = '<span class="badge bg-danger">Élevée</span>';
        }
        
        productsHtml += `
            <div class="card mb-3">
                <div class="card-body">
                    <h5 class="card-title">${product.name}</h5>
                    <div class="row mb-2">
                        <div class="col-md-4">
                            <strong>Prix fournisseur:</strong> ${product.supplier_price.toFixed(2)} €
                        </div>
                        <div class="col-md-4">
                            <strong>Prix recommandé:</strong> ${product.recommended_price.toFixed(2)} €
                        </div>
                        <div class="col-md-4">
                            <strong>Marge potentielle:</strong> ${product.potential_margin_percent.toFixed(1)}%
                        </div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-md-4">
                            <strong>Tendance:</strong> ${trendBadge}
                        </div>
                        <div class="col-md-4">
                            <strong>Concurrence:</strong> ${competitionBadge}
                        </div>
                        <div class="col-md-4">
                            <strong>Score:</strong> ${product.recommendation_score.toFixed(1)}/10
                        </div>
                    </div>
                    <p class="card-text text-muted">${product.justification}</p>
                    <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                        <button class="btn btn-sm btn-outline-primary">Ajouter à la boutique</button>
                        <button class="btn btn-sm btn-outline-secondary">Analyser davantage</button>
                    </div>
                </div>
            </div>
        `;
    });
    
    const date = new Date(results.created_at).toLocaleString();
    
    analysisResults.innerHTML = `
        <div class="alert alert-success mb-3">
            <strong>Analyse complétée!</strong> ${results.top_products.length} produits prometteurs identifiés
        </div>
        <div class="card mb-3">
            <div class="card-header bg-light">
                <div class="d-flex justify-content-between align-items-center">
                    <span>Résultats de l'analyse du ${date}</span>
                    <span class="badge bg-info">${results.source_urls.length} URLs analysées</span>
                </div>
            </div>
            <div class="card-body">
                ${productsHtml}
            </div>
        </div>
    `;
}
EOF
fi

# Créer le fichier de configuration Nginx
echo -e "${GREEN}Création du fichier de configuration Nginx...${NC}"
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
    }
}
EOF

# Créer un lien symbolique pour activer la configuration
echo -e "${GREEN}Activation de la configuration...${NC}"
ln -sf /etc/nginx/sites-available/dropship-dashboard /etc/nginx/sites-enabled/

# Supprimer la configuration par défaut
rm -f /etc/nginx/sites-enabled/default

# Vérifier la configuration
echo -e "${GREEN}Vérification de la configuration Nginx...${NC}"
nginx -t

# Redémarrer Nginx
echo -e "${GREEN}Redémarrage de Nginx...${NC}"
systemctl restart nginx
systemctl enable nginx

echo -e "${GREEN}Déploiement terminé!${NC}"
echo -e "Le dashboard est accessible à l'adresse: ${YELLOW}http://$(hostname -I | awk '{print $1}')${NC}"
echo -e "L'API est accessible à l'adresse: ${YELLOW}http://$(hostname -I | awk '{print $1}')${NC}/api/"

exit 0
