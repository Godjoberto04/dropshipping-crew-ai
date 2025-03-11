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
    
    // Configurer le formulaire de configuration de la boutique
    const storeForm = document.getElementById('storeForm');
    if (storeForm) {
        storeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            configureStore();
        });
    }
    
    // Configurer le formulaire de génération de contenu
    const contentForm = document.getElementById('contentForm');
    if (contentForm) {
        contentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            generateContent();
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
    
    // Mettre à jour le statut des services pour refléter l'état actuel du projet
    const updatedServices = {
        ...services,
        data_analyzer: { status: 'online', version: '1.0.0' },
        website_builder: { status: 'online', version: '1.0.0' },
        content_generator: { status: 'online', version: '0.1.0' },
        order_manager: { status: 'offline', version: null },
        site_updater: { status: 'offline', version: null }
    };
    
    for (const [service, info] of Object.entries(updatedServices)) {
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