document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des composants
    initSidebar();
    initNavigation();
    
    // Charger le statut initial du système
    fetchSystemStatus();
    
    // Configurer le timer de rafraîchissement automatique
    let refreshCounter = 30;
    const refreshTimer = document.getElementById('statusRefreshTimer');
    
    setInterval(() => {
        refreshCounter--;
        if (refreshCounter <= 0) {
            refreshCounter = 30;
            fetchSystemStatus();
        }
        refreshTimer.textContent = refreshCounter + 's';
    }, 1000);
    
    // Configurer le bouton de rafraîchissement manuel
    document.getElementById('refreshStatus').addEventListener('click', function(e) {
        e.preventDefault();
        refreshCounter = 30;
        fetchSystemStatus();
    });
    
    // Configurer le slider de marge
    const minMarginSlider = document.getElementById('minMargin');
    const minMarginValue = document.getElementById('minMarginValue');
    if (minMarginSlider && minMarginValue) {
        minMarginSlider.addEventListener('input', function() {
            minMarginValue.textContent = this.value + '%';
        });
    }
    
    // Configurer le formulaire d'analyse
    const analysisForm = document.getElementById('analysisForm');
    if (analysisForm) {
        analysisForm.addEventListener('submit', function(e) {
            e.preventDefault();
            runAnalysis();
        });
    }
});

// Initialiser la barre latérale
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    
    if (sidebarToggle && sidebar && content) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('sidebar-collapsed');
            content.classList.toggle('content-expanded');
        });
        
        // Sidebar responsive sur mobile
        if (window.innerWidth <= 768) {
            sidebar.classList.add('sidebar-collapsed');
            content.classList.add('content-expanded');
        }
    }
}

// Initialiser la navigation
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link[data-target]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Retirer la classe active de tous les liens
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Ajouter la classe active au lien cliqué
            this.classList.add('active');
            
            // Masquer toutes les sections
            const sections = document.querySelectorAll('.section');
            sections.forEach(s => s.classList.remove('active'));
            
            // Afficher la section correspondante
            const targetSection = document.getElementById(this.dataset.target);
            if (targetSection) {
                targetSection.classList.add('active');
            }
            
            // Fermer le sidebar sur mobile après une navigation
            if (window.innerWidth <= 768) {
                const sidebar = document.getElementById('sidebar');
                if (sidebar) sidebar.classList.add('sidebar-collapsed');
            }
        });
    });
}

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
            updateStatusCards(data.services);
            updateSystemPerformance(data.system);
            updateAgentsStatus(data.services);
            
            // Mettre à jour le timestamp de dernière mise à jour
            const lastUpdated = document.getElementById('lastUpdated');
            if (lastUpdated) {
                const now = new Date();
                lastUpdated.textContent = `Dernière mise à jour: ${now.toLocaleTimeString()}`;
            }
            
            // Mettre à jour les métriques du dashboard
            updateDashboardMetrics();
        })
        .catch(error => {
            console.error('Erreur:', error);
            // Afficher une erreur à l'utilisateur
            const servicesStatus = document.getElementById('servicesStatus');
            if (servicesStatus) {
                servicesStatus.innerHTML = `
                    <div class="col-12">
                        <div class="alert alert-danger">
                            Impossible de récupérer le statut du système. L'API semble inaccessible.
                        </div>
                    </div>
                `;
            }
        });
}

// Fonction pour mettre à jour les cartes de statut
function updateStatusCards(services) {
    const servicesStatus = document.getElementById('servicesStatus');
    if (!servicesStatus) return;
    
    servicesStatus.innerHTML = '';
    
    for (const [service, info] of Object.entries(services)) {
        let statusClass = 'status-offline';
        let statusText = 'Hors ligne';
        let statusIcon = 'bi-x-circle';
        
        if (info.status === 'online') {
            statusClass = 'status-online';
            statusText = 'En ligne';
            statusIcon = 'bi-check-circle';
        } else if (info.status === 'partial') {
            statusClass = 'status-partial';
            statusText = 'Partiellement implémenté';
            statusIcon = 'bi-exclamation-circle';
        }
        
        const version = info.version ? `v${info.version}` : '';
        
        servicesStatus.innerHTML += `
            <div class="col-md-6 mb-3">
                <div class="card status-card ${statusClass}">
                    <div class="card-body">
                        <div class="d-flex align-items-center">
                            <div class="me-3">
                                <i class="bi ${statusIcon} fs-3"></i>
                            </div>
                            <div>
                                <h5 class="card-title mb-1">${service.charAt(0).toUpperCase() + service.slice(1).replace('_', ' ')}</h5>
                                <p class="card-text mb-0">${statusText} ${version}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}

// Fonction pour mettre à jour les performances du système
function updateSystemPerformance(system) {
    if (!system) return;
    
    // Mettre à jour les valeurs CPU
    const cpuValue = document.getElementById('cpuValue');
    const cpuBar = document.querySelector('.progress-bar:nth-child(1)');
    if (cpuValue && cpuBar) {
        cpuValue.textContent = `${system.cpu_usage.toFixed(1)}%`;
        cpuBar.style.width = `${system.cpu_usage}%`;
        cpuBar.setAttribute('aria-valuenow', system.cpu_usage);
        cpuBar.textContent = `${system.cpu_usage.toFixed(1)}%`;
    }
    
    // Mettre à jour les valeurs mémoire
    const memoryValue = document.getElementById('memoryValue');
    const memoryBar = document.querySelector('.progress-bar:nth-child(2)');
    if (memoryValue && memoryBar) {
        memoryValue.textContent = `${system.memory_usage.toFixed(1)}%`;
        memoryBar.style.width = `${system.memory_usage}%`;
        memoryBar.setAttribute('aria-valuenow', system.memory_usage);
        memoryBar.textContent = `${system.memory_usage.toFixed(1)}%`;
    }
    
    // Mettre à jour les valeurs disque
    const diskValue = document.getElementById('diskValue');
    const diskBar = document.querySelector('.progress-bar:nth-child(3)');
    if (diskValue && diskBar) {
        diskValue.textContent = `${system.disk_usage.toFixed(1)}%`;
        diskBar.style.width = `${system.disk_usage}%`;
        diskBar.setAttribute('aria-valuenow', system.disk_usage);
        diskBar.textContent = `${system.disk_usage.toFixed(1)}%`;
    }
}

// Fonction pour mettre à jour le statut des agents
function updateAgentsStatus(services) {
    const agentsStatus = document.getElementById('agentsStatus');
    if (!agentsStatus) return;
    
    // Liste des agents
    const agents = [
        { id: 'data_analyzer', name: 'Data Analyzer', icon: 'bi-graph-up', description: 'Analyse les marchés et identifie les produits à fort potentiel' },
        { id: 'website_builder', name: 'Website Builder', icon: 'bi-code-square', description: 'Crée et gère la boutique Shopify' },
        { id: 'content_generator', name: 'Content Generator', icon: 'bi-pencil-square', description: 'Génère du contenu optimisé SEO' },
        { id: 'order_manager', name: 'Order Manager', icon: 'bi-cart-check', description: 'Gère les commandes et les expéditions' },
        { id: 'site_updater', name: 'Site Updater', icon: 'bi-arrow-repeat', description: 'Met à jour les prix et les stocks' }
    ];
    
    agentsStatus.innerHTML = '';
    
    agents.forEach(agent => {
        const service = services[agent.id.toLowerCase()] || { status: 'offline', version: null };
        
        let statusClass = 'bg-danger';
        let statusText = 'Non implémenté';
        
        if (service.status === 'online') {
            statusClass = 'bg-success';
            statusText = 'Actif';
        } else if (service.status === 'partial') {
            statusClass = 'bg-warning';
            statusText = 'Partiellement implémenté';
        }
        
        const version = service.version ? `v${service.version}` : '';
        
        agentsStatus.innerHTML += `
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <div class="position-relative d-inline-block mb-3">
                            <i class="bi ${agent.icon} agent-icon"></i>
                            <span class="agent-status-badge ${statusClass}"></span>
                        </div>
                        <h5 class="card-title">${agent.name}</h5>
                        <p class="card-text text-muted">${agent.description}</p>
                        <div class="mt-3">
                            <span class="badge ${statusClass}">${statusText}</span>
                            ${version ? `<span class="badge bg-secondary ms-2">${version}</span>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
}

// Fonction pour mettre à jour les métriques du dashboard
function updateDashboardMetrics() {
    // Dans une implémentation réelle, ces données proviendraient de l'API
    // Pour l'instant, nous utilisons des valeurs fictives
    
    // Métriques des produits
    updateMetric('Produits Analysés', 0, 100, 0);
    updateMetric('Produits en Boutique', 0, 50, 0);
    updateMetric('Commandes', 0, 100, 0);
    updateMetric('Chiffre d\'Affaires', '0€', 100, 0);
    
    // Dans une implémentation future, vous pourriez ajouter ici des appels à l'API
    // pour récupérer les vraies données et mettre à jour les métriques
}

// Fonction utilitaire pour mettre à jour une métrique
function updateMetric(label, value, max, percentage) {
    const metricElements = document.querySelectorAll('.metric-label');
    
    for (let i = 0; i < metricElements.length; i++) {
        if (metricElements[i].textContent === label) {
            const valueElement = metricElements[i].previousElementSibling;
            const progressBar = metricElements[i].nextElementSibling.querySelector('.progress-bar');
            
            if (valueElement) valueElement.textContent = value;
            if (progressBar) {
                progressBar.style.width = `${percentage}%`;
                progressBar.setAttribute('aria-valuenow', percentage);
            }
            
            break;
        }
    }
}

// Fonction pour lancer une analyse
function runAnalysis() {
    const urlsElement = document.getElementById('urls');
    const marketSegmentElement = document.getElementById('marketSegment');
    const minMarginElement = document.getElementById('minMargin');
    
    if (!urlsElement) return;
    
    const urlsText = urlsElement.value;
    const marketSegment = marketSegmentElement ? marketSegmentElement.value : '';
    const minMargin = minMarginElement ? parseFloat(minMarginElement.value) : 30.0;
    
    // Validation de base
    if (!urlsText.trim()) {
        alert('Veuillez entrer au moins une URL à analyser');
        return;
    }
    
    // Préparer les données
    const urls = urlsText.split('\n').filter(url => url.trim() !== '');
    const requestData = { 
        urls: urls,
        market_segment: marketSegment,
        min_margin: minMargin
    };
    
    // Afficher le spinner
    const spinner = document.getElementById('analysisSpinner');
    const button = document.getElementById('runAnalysisBtn');
    if (spinner) spinner.classList.remove('d-none');
    if (button) button.disabled = true;
    
    // Mise à jour de l'UI pour indiquer que l'analyse est en cours
    const analysisResults = document.getElementById('analysisResults');
    if (analysisResults) {
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
    }
    
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
        if (analysisResults) {
            analysisResults.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Erreur!</strong> Impossible de lancer l'analyse: ${error.message}
                </div>
            `;
        }
        if (spinner) spinner.classList.add('d-none');
        if (button) button.disabled = false;
    });
}

// Fonction pour vérifier l'état d'une tâche périodiquement
function pollTaskStatus(taskId) {
    const spinner = document.getElementById('analysisSpinner');
    const button = document.getElementById('runAnalysisBtn');
    const analysisResults = document.getElementById('analysisResults');
    
    if (!analysisResults) return;
    
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
                if (spinner) spinner.classList.add('d-none');
                if (button) button.disabled = false;
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
    
    if (!analysisResults) return;
    
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
            
            // Mettre à jour la métrique des produits analysés
            updateMetric('Produits Analysés', results.top_products.length, 100, 
                Math.min(results.top_products.length, 100));
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
            if (spinner) spinner.classList.add('d-none');
            if (button) button.disabled = false;
        });
}

// Fonction pour afficher les résultats d'analyse
function displayAnalysisResults(results) {
    const analysisResults = document.getElementById('analysisResults');
    if (!analysisResults || !results.top_products) return;
    
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
            <div class="card mb-3 product-card">
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
    
    const date = new Date(results.created_at || Date.now()).toLocaleString();
    
    analysisResults.innerHTML = `
        <div class="alert alert-success mb-3">
            <strong>Analyse complétée!</strong> ${results.top_products.length} produits prometteurs identifiés
        </div>
        <div class="card mb-3">
            <div class="card-header bg-light">
                <div class="d-flex justify-content-between align-items-center">
                    <span>Résultats de l'analyse du ${date}</span>
                    <span class="badge bg-info">${results.source_urls ? results.source_urls.length : 0} URLs analysées</span>
                </div>
            </div>
            <div class="card-body">
                ${productsHtml}
            </div>
        </div>
    `;
}
