// Fonction pour générer une description d'exemple (à des fins de démonstration)
function generateSampleDescription(productName, features, tone, niche) {
    let descIntro = '';
    let descBody = '';
    let descOutro = '';
    
    // Intro basée sur le ton
    if (tone === 'persuasif') {
        descIntro = `Découvrez le ${productName}, l'innovation qui va révolutionner votre quotidien. Ne cherchez plus, vous venez de trouver le produit qui répondra parfaitement à tous vos besoins.`;
    } else if (tone === 'informatif') {
        descIntro = `Le ${productName} est un produit conçu pour offrir des performances optimales. Voici les informations essentielles à connaître sur ce produit.`;
    } else if (tone === 'enjoué') {
        descIntro = `Wow! Le ${productName} est arrivé et il va vous faire sourire! Préparez-vous à être émerveillé par ce produit incroyable qui va illuminer votre quotidien.`;
    } else {
        descIntro = `Le ${productName} représente un excellent investissement pour les utilisateurs exigeants. Ce produit professionnel se distingue par sa qualité et ses fonctionnalités avancées.`;
    }
    
    // Corps basé sur les caractéristiques
    if (features && features.length > 0) {
        descBody = `<ul>`;
        features.forEach(feature => {
            descBody += `<li><strong>${feature}</strong> - `;
            
            // Ajouter une explication fictive pour chaque caractéristique
            if (feature.toLowerCase().includes('autonomie')) {
                descBody += `Profitez de longues heures d'utilisation sans vous soucier de recharger.`;
            } else if (feature.toLowerCase().includes('bruit')) {
                descBody += `Immergez-vous dans votre musique sans être dérangé par les bruits extérieurs.`;
            } else if (feature.toLowerCase().includes('eau') || feature.toLowerCase().includes('résistant')) {
                descBody += `Utilisez votre appareil en toute confiance, même dans des conditions humides.`;
            } else {
                descBody += `Une caractéristique essentielle qui améliore considérablement votre expérience.`;
            }
            descBody += `</li>`;
        });
        descBody += `</ul>`;
    }
    
    // Outro basé sur la niche
    if (niche === 'electronics') {
        descOutro = `Avec sa technologie de pointe et son design élégant, le ${productName} est un must-have pour tous les amateurs de technologie. Commandez dès maintenant et recevez-le en 48h avec notre livraison express!`;
    } else if (niche === 'fashion') {
        descOutro = `Ajoutez une touche d'élégance à votre style avec le ${productName}. Tendance, confortable et polyvalent, il deviendra rapidement votre indispensable mode. Livraison gratuite pour toute commande!`;
    } else if (niche === 'home') {
        descOutro = `Transformez votre espace de vie avec le ${productName}. Alliant esthétique et fonctionnalité, il s'intégrera parfaitement dans votre intérieur. Garantie satisfaction 30 jours!`;
    } else {
        descOutro = `Prenez soin de vous avec le ${productName}. Formulé avec les meilleurs ingrédients, il vous garantit des résultats exceptionnels. Livraison offerte dès 50€ d'achat!`;
    }
    
    return `${descIntro}<br><br>${descBody}<br>${descOutro}`;
}

// Fonction pour afficher les résultats de génération de contenu
function displayContentResults(results) {
    const contentResults = document.getElementById('contentResults');
    if (!contentResults) return;
    
    contentResults.innerHTML = `
        <div class="alert alert-success mb-3">
            <strong>Génération complétée!</strong> Description de produit créée avec succès.
        </div>
        
        <div class="card mb-4">
            <div class="card-header">
                <ul class="nav nav-tabs card-header-tabs" id="contentTabs" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="preview-tab" data-bs-toggle="tab" data-bs-target="#preview" type="button" role="tab" aria-controls="preview" aria-selected="true">Aperçu</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="seo-tab" data-bs-toggle="tab" data-bs-target="#seo" type="button" role="tab" aria-controls="seo" aria-selected="false">Métadonnées SEO</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="html-tab" data-bs-toggle="tab" data-bs-target="#html" type="button" role="tab" aria-controls="html" aria-selected="false">HTML</button>
                    </li>
                </ul>
            </div>
            <div class="card-body">
                <div class="tab-content" id="contentTabsContent">
                    <div class="tab-pane fade show active" id="preview" role="tabpanel" aria-labelledby="preview-tab">
                        <div class="content-preview p-3 border rounded">
                            ${results.description}
                        </div>
                    </div>
                    <div class="tab-pane fade" id="seo" role="tabpanel" aria-labelledby="seo-tab">
                        <div class="mb-3">
                            <label class="form-label"><strong>Meta Title</strong></label>
                            <input type="text" class="form-control" value="${results.seo_metadata.title_tag}" readonly>
                        </div>
                        <div class="mb-3">
                            <label class="form-label"><strong>Meta Description</strong></label>
                            <textarea class="form-control" rows="3" readonly>${results.seo_metadata.meta_description}</textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label"><strong>Mots-clés</strong></label>
                            <div>
                                ${results.seo_metadata.keywords.map(kw => `<span class="badge bg-secondary me-1">${kw}</span>`).join('')}
                            </div>
                        </div>
                    </div>
                    <div class="tab-pane fade" id="html" role="tabpanel" aria-labelledby="html-tab">
                        <pre class="bg-light p-3 rounded"><code>${results.description.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>
                    </div>
                </div>
            </div>
            <div class="card-footer bg-white d-flex justify-content-end">
                <button class="btn btn-primary me-2">Publier sur la boutique</button>
                <button class="btn btn-outline-secondary">Télécharger</button>
            </div>
        </div>
    `;
}

// Fonction pour vérifier l'état d'une tâche périodiquement
function pollTaskStatus(taskId) {
    const spinner = document.getElementById('analysisSpinner');
    const button = document.getElementById('runAnalysisBtn');
    const analysisResults = document.getElementById('analysisResults');
    
    if (!analysisResults) return;
    
    let pollInterval = 5000; // 5 secondes
    let progress = 0;
    
    // Fonction pour simuler l'avancement progressif
    function simulateProgress() {
        progress += 10;
        if (progress > 100) progress = 100;
        
        // Mettre à jour la barre de progression
        analysisResults.innerHTML = `
            <div class="alert alert-warning">
                <strong>Analyse en cours: ${progress}%</strong><br>
                ${getProgressMessage(progress)}
            </div>
            <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                    role="progressbar" 
                    style="width: ${progress}%" 
                    aria-valuenow="${progress}" 
                    aria-valuemin="0" 
                    aria-valuemax="100">
                    ${progress}%
                </div>
            </div>
        `;
        
        // Vérifier si la tâche est terminée
        if (progress >= 100) {
            // Simuler la récupération des résultats
            setTimeout(() => {
                simulateAnalysisResults();
                if (spinner) spinner.classList.add('d-none');
                if (button) button.disabled = false;
            }, 500);
        } else {
            // Continuer le polling
            setTimeout(simulateProgress, pollInterval);
            
            // Ajuster l'intervalle de polling en fonction de la progression
            if (progress > 90) {
                pollInterval = 1000; // 1 seconde
            } else if (progress > 50) {
                pollInterval = 2000; // 2 secondes
            }
        }
    }
    
    // Démarrer la simulation de progression
    simulateProgress();
}

// Obtenir un message basé sur la progression
function getProgressMessage(progress) {
    if (progress < 20) {
        return "Récupération des données des produits depuis les URLs fournies...";
    } else if (progress < 40) {
        return "Analyse des prix et des disponibilités...";
    } else if (progress < 60) {
        return "Évaluation des marges potentielles...";
    } else if (progress < 80) {
        return "Analyse de la concurrence et des tendances du marché...";
    } else {
        return "Finalisation de l'analyse et préparation des recommandations...";
    }
}

// Simuler des résultats d'analyse
function simulateAnalysisResults() {
    const analysisResults = document.getElementById('analysisResults');
    if (!analysisResults) return;
    
    // Générer des produits fictifs pour la démo
    const mockProducts = [
        {
            name: "Écouteurs Bluetooth Sans Fil",
            supplier_price: 24.99,
            recommended_price: 69.99,
            potential_margin_percent: 64.3,
            competition_level: "Medium",
            trend_direction: "Up",
            recommendation_score: 8.7,
            justification: "Forte demande dans le segment audio, tendance à la hausse sur Google Trends. Marge attractive et concurrence modérée."
        },
        {
            name: "Support de Téléphone pour Voiture",
            supplier_price: 3.49,
            recommended_price: 19.99,
            potential_margin_percent: 82.5,
            competition_level: "High",
            trend_direction: "Stable",
            recommendation_score: 7.2,
            justification: "Excellente marge mais concurrence élevée. Nécessite une différenciation par la qualité ou le marketing."
        },
        {
            name: "Chargeur sans fil 15W",
            supplier_price: 8.99,
            recommended_price: 29.99,
            potential_margin_percent: 70.0,
            competition_level: "Medium",
            trend_direction: "Up",
            recommendation_score: 8.4,
            justification: "Produit recherché avec l'adoption croissante des technologies sans fil. Bonne marge et tendance positive."
        }
    ];
    
    let productsHtml = '';
    mockProducts.forEach(product => {
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
    
    const date = new Date().toLocaleString();
    
    analysisResults.innerHTML = `
        <div class="alert alert-success mb-3">
            <strong>Analyse complétée!</strong> ${mockProducts.length} produits prometteurs identifiés
        </div>
        <div class="card mb-3">
            <div class="card-header bg-light">
                <div class="d-flex justify-content-between align-items-center">
                    <span>Résultats de l'analyse du ${date}</span>
                    <span class="badge bg-info">3 URLs analysées</span>
                </div>
            </div>
            <div class="card-body">
                ${productsHtml}
            </div>
        </div>
    `;
    
    // Mettre à jour la métrique des produits analysés sur le dashboard
    updateMetric('Produits Analysés', 37, 100, 37);
}