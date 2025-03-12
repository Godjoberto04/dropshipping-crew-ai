// Fonction pour mettre à jour le statut des agents
function updateAgentsStatus(services) {
    const agentsStatus = document.getElementById('agentsStatus');
    if (!agentsStatus) return;
    
    // Liste des agents avec statut mis à jour
    const agents = [
        { 
            id: 'data_analyzer', 
            name: 'Data Analyzer', 
            icon: 'bi-graph-up', 
            description: 'Analyse les marchés et identifie les produits à fort potentiel',
            status: 'online',
            version: '1.0.0'
        },
        { 
            id: 'website_builder', 
            name: 'Website Builder', 
            icon: 'bi-code-square', 
            description: 'Crée et gère la boutique Shopify',
            status: 'online',
            version: '1.0.0'
        },
        { 
            id: 'content_generator', 
            name: 'Content Generator', 
            icon: 'bi-pencil-square', 
            description: 'Génère du contenu optimisé SEO',
            status: 'online',
            version: '0.1.0'
        },
        { 
            id: 'order_manager', 
            name: 'Order Manager', 
            icon: 'bi-cart-check', 
            description: 'Gère les commandes et les expéditions',
            status: 'offline',
            version: null
        },
        { 
            id: 'site_updater', 
            name: 'Site Updater', 
            icon: 'bi-arrow-repeat', 
            description: 'Met à jour les prix et les stocks',
            status: 'offline',
            version: null
        }
    ];
    
    agentsStatus.innerHTML = '';
    
    agents.forEach(agent => {
        // Utiliser le statut fourni par l'agent lui-même au lieu de services
        const service = services[agent.id.toLowerCase()] || { status: agent.status, version: agent.version };
        
        let statusClass = 'bg-danger';
        let statusText = 'Non implémenté';
        
        if (agent.status === 'online') {
            statusClass = 'bg-success';
            statusText = 'Actif';
        } else if (agent.status === 'partial') {
            statusClass = 'bg-warning';
            statusText = 'Partiellement implémenté';
        }
        
        const version = agent.version ? `v${agent.version}` : '';
        
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
    // Pour cette mise à jour, utilisons des valeurs qui reflètent l'activité du projet
    
    // Métriques des produits
    updateMetric('Produits Analysés', 34, 100, 34);
    updateMetric('Produits en Boutique', 12, 50, 24);
    updateMetric('Commandes', 0, 100, 0);
    updateMetric('Chiffre d\'Affaires', '0€', 100, 0);
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
    
    // Simulation d'une requête API (à remplacer par un vrai appel)
    setTimeout(() => {
        // Code de simulation pour la démo
        const mockTaskId = "task_" + Math.random().toString(36).substring(2, 15);
        pollTaskStatus(mockTaskId);
    }, 2000);
}

// Fonction pour configurer une boutique
function configureStore() {
    const storeNameElement = document.getElementById('storeName');
    const storeThemeElement = document.getElementById('storeTheme');
    const primaryColorElement = document.getElementById('primaryColor');
    const secondaryColorElement = document.getElementById('secondaryColor');
    
    if (!storeNameElement) return;
    
    const storeName = storeNameElement.value;
    const storeTheme = storeThemeElement ? storeThemeElement.value : 'dawn';
    const primaryColor = primaryColorElement ? primaryColorElement.value : '#3b82f6';
    const secondaryColor = secondaryColorElement ? secondaryColorElement.value : '#10b981';
    
    // Validation de base
    if (!storeName.trim()) {
        alert('Veuillez entrer un nom pour la boutique');
        return;
    }
    
    // Afficher le spinner et désactiver le bouton
    const spinner = document.getElementById('storeSpinner');
    const button = document.getElementById('configureStoreBtn');
    if (spinner) spinner.classList.remove('d-none');
    if (button) button.disabled = true;
    
    // Simuler une réponse après un délai
    setTimeout(() => {
        // Simuler la fin de l'opération
        if (spinner) spinner.classList.add('d-none');
        if (button) button.disabled = false;
        
        // Afficher un message de succès
        alert(`Boutique "${storeName}" configurée avec succès!`);
    }, 3000);
}

// Fonction pour générer du contenu
function generateContent() {
    const productNameElement = document.getElementById('productName');
    const productFeaturesElement = document.getElementById('productFeatures');
    const contentToneElement = document.getElementById('contentTone');
    const contentNicheElement = document.getElementById('contentNiche');
    const seoOptimizeElement = document.getElementById('seoOptimize');
    
    if (!productNameElement || !productFeaturesElement) return;
    
    const productName = productNameElement.value;
    const productFeatures = productFeaturesElement.value;
    const contentTone = contentToneElement ? contentToneElement.value : 'persuasif';
    const contentNiche = contentNicheElement ? contentNicheElement.value : 'electronics';
    const seoOptimize = seoOptimizeElement ? seoOptimizeElement.checked : true;
    
    // Validation de base
    if (!productName.trim()) {
        alert('Veuillez entrer un nom de produit');
        return;
    }
    
    // Préparer les données
    const features = productFeatures.split('\n').filter(feature => feature.trim() !== '');
    const requestData = { 
        action: "generate_product_description",
        product_data: {
            name: productName,
            features: features,
            price: "99.99",
            brand: "TechBrand"
        },
        tone: contentTone,
        niche: contentNiche,
        seo_optimize: seoOptimize,
        language: "fr"
    };
    
    // Afficher le spinner
    const spinner = document.getElementById('contentSpinner');
    const button = document.getElementById('generateContentBtn');
    if (spinner) spinner.classList.remove('d-none');
    if (button) button.disabled = true;
    
    // Mise à jour de l'UI pour indiquer que la génération est en cours
    const contentResults = document.getElementById('contentResults');
    if (contentResults) {
        contentResults.innerHTML = `
            <div class="alert alert-warning">
                <div class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                    <div>
                        <strong>Génération en cours...</strong><br>
                        Génération d'une description optimisée pour "${productName}". Cette opération peut prendre quelques instants.
                    </div>
                </div>
            </div>
        `;
    }
    
    // Simuler une requête API (à remplacer par un vrai appel dans l'implémentation réelle)
    setTimeout(() => {
        if (spinner) spinner.classList.add('d-none');
        if (button) button.disabled = false;
        
        // Simuler un résultat
        displayContentResults({
            description: generateSampleDescription(productName, features, contentTone, contentNiche),
            seo_metadata: {
                meta_description: `Découvrez notre ${productName} de haute qualité. ${features[0] || ''}. Livraison rapide et garantie satisfaction.`,
                title_tag: `${productName} - Achetez en ligne`,
                keywords: [productName.toLowerCase(), contentNiche, 'achat en ligne', 'haute qualité']
            },
            raw_description: "Description brute non optimisée"
        });
    }, 3000);
}