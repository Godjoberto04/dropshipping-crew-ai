# Guide technique du module TrendsAnalyzer pour développeurs

Ce document fournit des informations techniques détaillées sur le module `TrendsAnalyzer` pour les développeurs qui souhaitent étendre ses fonctionnalités, le personnaliser ou l'intégrer dans d'autres composants du projet dropshipping-crew-ai.

## Table des matières

1. [Architecture du module](#architecture-du-module)
2. [Structure des données](#structure-des-données)
3. [Algorithmes clés](#algorithmes-clés)
4. [Extension du module](#extension-du-module)
5. [Intégration avec d'autres modules](#intégration-avec-dautres-modules)
6. [Optimisation des performances](#optimisation-des-performances)
7. [Tests et validation](#tests-et-validation)
8. [Bonnes pratiques de développement](#bonnes-pratiques-de-développement)

## Architecture du module

Le module `TrendsAnalyzer` est conçu selon les principes de programmation orientée objet et repose sur plusieurs composants clés :

### Structure des fichiers

```
data_sources/
├── trends/
│   ├── __init__.py
│   └── trends_analyzer.py
```

### Flux de traitement des données

1. **Collecte** : Interrogation de l'API Google Trends via PyTrends
2. **Transformation** : Conversion des données brutes en métriques analytiques
3. **Analyse** : Calcul de scores et indicateurs de tendance
4. **Interprétation** : Génération de conclusions et recommandations

### Classes et méthodes principales

La classe principale `TrendsAnalyzer` encapsule toute la logique d'analyse et expose les méthodes publiques suivantes :

```python
# Méthodes publiques principales
analyze_keywords()      # Analyse de base des mots-clés
analyze_product()       # Analyse complète d'un produit
compare_products()      # Comparaison de plusieurs produits
get_rising_products()   # Identification des produits en tendance

# Méthodes privées importantes
_calculate_trend_metrics()    # Calcul des métriques de tendance
_calculate_trend_score()      # Calcul du score de tendance global
_detect_seasonality()         # Détection de saisonnalité
_generate_summary()           # Génération de résumés
_generate_product_conclusion() # Génération de conclusions pour produits
```

## Structure des données

### Entrées

Les entrées principales du module sont des mots-clés et paramètres d'analyse spécifiés par l'utilisateur :

```python
# Exemples d'entrées
keywords = ["écouteurs bluetooth", "écouteurs sans fil"]
timeframe = "medium_term"  # ou "now 3-m" format PyTrends
geo = "FR"
category = 0
```

### Sorties

Les sorties sont des structures de données imbriquées contenant les résultats d'analyse :

#### Exemple de sortie `analyze_keywords()`

```python
{
    'interest_over_time': pandas.DataFrame,  # Évolution de l'intérêt au fil du temps
    'related_queries': {                     # Requêtes associées
        'écouteurs bluetooth': {
            'top': pandas.DataFrame,        # Requêtes principales
            'rising': pandas.DataFrame      # Requêtes en augmentation
        }
    },
    'related_topics': {                      # Sujets associés
        'écouteurs bluetooth': {
            'top': pandas.DataFrame,
            'rising': pandas.DataFrame
        }
    },
    'interest_by_region': pandas.DataFrame,  # Intérêt par région
    'trend_metrics': {                       # Métriques calculées
        'écouteurs bluetooth': {
            'current_interest': 75.0,        # Intérêt actuel (0-100)
            'average_interest': 65.2,        # Intérêt moyen
            'growth_rate': 15.3,             # Taux de croissance (%)
            'volatility': 8.7,               # Volatilité (écart-type)
            'momentum': 12.5,                # Momentum (%)
            'is_growing': True,              # En croissance ?
            'is_seasonal': False,            # Saisonnier ?
            'seasonality_score': 0.0,        # Score de saisonnalité (0-100)
            'trend_score': 78.6              # Score global (0-100)
        }
    },
    'summary': {                             # Résumé de l'analyse
        'top_keyword': 'écouteurs bluetooth',
        'avg_trend_score': 78.6,
        'trending_keywords': ['écouteurs bluetooth'],
        'conclusion': 'Texte de conclusion...'
    }
}
```

#### Exemple de sortie `analyze_product()`

```python
{
    'product_name': 'Écouteurs sans fil',
    'keywords': ['Écouteurs sans fil', 'écouteurs bluetooth', 'écouteurs true wireless'],
    'analysis_by_timeframe': {
        'short_term': { ... },  # Résultats de analyze_keywords()
        'medium_term': { ... },
        'long_term': { ... }
    },
    'related_keywords_analysis': {
        'écouteurs bluetooth': { ... },  # Résultats de analyze_keywords()
        'écouteurs true wireless': { ... }
    },
    'overall_trend_score': 82.3,         # Score global (0-100)
    'is_trending': True,                 # En tendance ?
    'seasonality': {
        'is_seasonal': False,
        'pattern': 'none',
        'peak_periods': []
    },
    'conclusion': 'Texte de conclusion...'
}
```

## Algorithmes clés

### Calcul du score de tendance

Le score de tendance est calculé en pondérant plusieurs métriques :

```python
def _calculate_trend_score(
    self, 
    current_interest, 
    growth_rate, 
    volatility, 
    momentum,
    average_interest=None
):
    """
    Calcule un score de tendance global (0-100)
    
    Pondération des facteurs :
    - current_interest: 30%
    - growth_rate: 30% 
    - volatility (inversée): 10%
    - momentum: 30%
    """
    # Normalisation des valeurs
    current_score = min(100, current_interest)
    
    # Conversion du taux de croissance en score
    growth_score = 50  # Score neutre par défaut
    if growth_rate > 100:
        growth_score = 100
    elif growth_rate > 50:
        growth_score = 90
    elif growth_rate > 25:
        growth_score = 80
    elif growth_rate > 10:
        growth_score = 70
    elif growth_rate > 0:
        growth_score = 60
    elif growth_rate > -10:
        growth_score = 40
    elif growth_rate > -25:
        growth_score = 30
    elif growth_rate > -50:
        growth_score = 20
    else:
        growth_score = 10
    
    # Calcul inversé pour la volatilité (moins = mieux)
    volatility_score = max(0, 100 - volatility)
    
    # Conversion du momentum en score
    momentum_score = 50  # Score neutre par défaut
    if momentum > 50:
        momentum_score = 100
    elif momentum > 25:
        momentum_score = 90
    elif momentum > 10:
        momentum_score = 80
    elif momentum > 0:
        momentum_score = 70
    elif momentum > -10:
        momentum_score = 40
    elif momentum > -25:
        momentum_score = 30
    else:
        momentum_score = 20
    
    # Calcul de la moyenne pondérée
    trend_score = (
        (current_score * 0.3) +
        (growth_score * 0.3) +
        (volatility_score * 0.1) +
        (momentum_score * 0.3)
    )
    
    return trend_score
```

### Détection de saisonnalité

L'algorithme de détection de saisonnalité utilise l'autocorrélation pour identifier les patterns récurrents :

```python
def _detect_seasonality(self, results_by_timeframe):
    """
    Détecte les patterns saisonniers dans les données.
    
    Recherche des corrélations sur plusieurs périodes :
    - Annuelle (52 semaines)
    - Semestrielle (26 semaines)
    - Trimestrielle (13 semaines)
    """
    # Extraction des données d'intérêt sur la période longue
    long_term_results = results_by_timeframe.get('long_term', {})
    if 'error' in long_term_results or 'interest_over_time' not in long_term_results:
        return {'is_seasonal': False, 'pattern': 'unknown', 'peak_periods': []}
    
    interest_df = long_term_results.get('interest_over_time')
    if interest_df.empty or len(interest_df) < 52:  # Besoin d'au moins un an de données
        return {'is_seasonal': False, 'pattern': 'insufficient_data', 'peak_periods': []}
    
    # Récupérer les données pour le premier mot-clé
    first_keyword = interest_df.columns[0]
    time_series = interest_df[first_keyword].dropna()
    
    # Calcul des autocorrélations pour différents décalages
    annual_corr = self._calculate_autocorrelation(time_series, 52)
    semiannual_corr = self._calculate_autocorrelation(time_series, 26)
    quarterly_corr = self._calculate_autocorrelation(time_series, 13)
    
    # Seuils de détection
    annual_threshold = 0.5
    semiannual_threshold = 0.4
    quarterly_threshold = 0.3
    
    # Détermination du pattern de saisonnalité
    pattern = 'none'
    is_seasonal = False
    peak_periods = []
    
    if annual_corr > annual_threshold:
        pattern = 'annual'
        is_seasonal = True
        peak_periods = self._find_peak_periods(time_series)
    elif semiannual_corr > semiannual_threshold:
        pattern = 'semiannual'
        is_seasonal = True
    elif quarterly_corr > quarterly_threshold:
        pattern = 'quarterly'
        is_seasonal = True
    
    return {
        'is_seasonal': is_seasonal,
        'pattern': pattern,
        'peak_periods': peak_periods,
        'annual_correlation': annual_corr,
        'semiannual_correlation': semiannual_corr,
        'quarterly_correlation': quarterly_corr
    }

def _calculate_autocorrelation(self, series, lag):
    """
    Calcule l'autocorrélation d'une série temporelle avec un décalage donné.
    
    Args:
        series: Série temporelle pandas
        lag: Décalage (en périodes)
        
    Returns:
        Coefficient de corrélation
    """
    if len(series) <= lag:
        return 0.0
        
    # Créer des séries décalées
    original = series[lag:].reset_index(drop=True)
    shifted = series[:-lag].reset_index(drop=True)
    
    # Calculer la corrélation
    correlation = original.corr(shifted)
    
    return correlation if not np.isnan(correlation) else 0.0

def _find_peak_periods(self, time_series):
    """
    Identifie les périodes de pic dans une série temporelle annuelle.
    
    Args:
        time_series: Série temporelle pandas
        
    Returns:
        Liste des mois avec pics d'intérêt
    """
    # Conversion en DataFrame avec index de date
    if not isinstance(time_series.index, pd.DatetimeIndex):
        return []
    
    # Agréger par mois et calculer la moyenne
    monthly_avg = time_series.groupby(time_series.index.month).mean()
    
    # Déterminer le seuil de pic (par exemple, top 25%)
    threshold = monthly_avg.quantile(0.75)
    
    # Identifier les mois dépassant le seuil
    peak_months = monthly_avg[monthly_avg >= threshold].index.tolist()
    
    # Convertir les numéros de mois en noms
    month_names = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }
    
    return [month_names[m] for m in peak_months]
```

### Génération de conclusions

L'algorithme de génération de conclusions produit des recommandations exploitables à partir des données d'analyse :

```python
def _generate_product_conclusion(self, results_by_timeframe):
    """
    Génère une conclusion pour un produit basée sur l'ensemble des analyses.
    """
    # Calcul des métriques globales
    overall_score = self._calculate_overall_trend_score(results_by_timeframe)
    is_trending = self._is_product_trending(results_by_timeframe)
    seasonality = self._detect_seasonality(results_by_timeframe)
    
    # Interprétation du score global
    if overall_score >= 80:
        potential = "très élevé"
    elif overall_score >= 70:
        potential = "élevé"
    elif overall_score >= 60:
        potential = "bon"
    elif overall_score >= 45:
        potential = "modéré"
    else:
        potential = "faible"
    
    # Construction de la conclusion
    conclusion = f"Le produit présente un potentiel {potential} avec un score de tendance de {overall_score:.1f}/100. "
    
    # Ajout d'informations sur la tendance
    if is_trending:
        conclusion += "Il montre actuellement une tendance à la hausse significative. "
    else:
        conclusion += "Il ne montre pas de tendance à la hausse significative actuellement. "
    
    # Ajout d'informations sur la saisonnalité
    if seasonality['is_seasonal']:
        if seasonality['pattern'] == 'annual':
            conclusion += "Le produit présente une forte saisonnalité annuelle. "
            if seasonality['peak_periods']:
                peak_months = ', '.join(seasonality['peak_periods'])
                conclusion += f"Les pics d'intérêt se manifestent généralement en {peak_months}. "
        elif seasonality['pattern'] == 'semiannual':
            conclusion += "Le produit présente une saisonnalité semestrielle. "
        else:
            conclusion += "Le produit présente une saisonnalité trimestrielle. "
    else:
        conclusion += "Le produit ne présente pas de saisonnalité marquée. "
    
    # Recommandations
    conclusion += "\n\nRecommandations pour le dropshipping : "
    
    if overall_score >= 70:
        if seasonality['is_seasonal']:
            conclusion += "Ce produit est recommandé, mais planifiez vos stocks et campagnes marketing en fonction de la saisonnalité identifiée. "
        else:
            conclusion += "Ce produit est fortement recommandé pour le dropshipping avec un potentiel de vente stable tout au long de l'année. "
    elif overall_score >= 50:
        conclusion += "Ce produit peut être envisagé pour le dropshipping, mais avec une surveillance régulière des tendances. "
    else:
        conclusion += "Ce produit n'est pas recommandé pour le dropshipping actuellement. "
    
    return conclusion
```
