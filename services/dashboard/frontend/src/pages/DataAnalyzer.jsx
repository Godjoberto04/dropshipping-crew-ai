import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { dataAnalyzerApi } from '../services/api';

const DataAnalyzer = () => {
  const [products, setProducts] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('products');
  const [analysisForm, setAnalysisForm] = useState({
    niche: '',
    maxProducts: 10,
    includeCompetition: true,
  });

  // Simulation des données
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Dans un premier temps, nous simulons les données
        // À remplacer par un vrai appel API quand disponible
        // const productsResponse = await dataAnalyzerApi.getProducts();
        // const trendsResponse = await dataAnalyzerApi.getTrends();
        
        const simulatedProducts = [
          { id: 1, name: 'Montre Connectée Pro', score: 87, trend: 'up', niche: 'Électronique', price: 89.99, margin: 42 },
          { id: 2, name: 'Support Téléphone Voiture', score: 78, trend: 'stable', niche: 'Accessoires Auto', price: 19.99, margin: 65 },
          { id: 3, name: 'Écouteurs Sans Fil TWS', score: 92, trend: 'up', niche: 'Électronique', price: 59.99, margin: 48 },
          { id: 4, name: 'Organisateur de Câbles', score: 76, trend: 'up', niche: 'Maison', price: 12.99, margin: 72 },
          { id: 5, name: 'Peluche LED Interactive', score: 81, trend: 'up', niche: 'Enfants', price: 29.99, margin: 55 },
        ];
        
        const simulatedTrends = [
          { id: 1, keyword: 'montre connectée', growth: 142, volume: 24500, competition: 'moyenne' },
          { id: 2, keyword: 'écouteurs bluetooth', growth: 118, volume: 32100, competition: 'élevée' },
          { id: 3, keyword: 'accessoire téléphone', growth: 87, volume: 18200, competition: 'moyenne' },
          { id: 4, keyword: 'gadget tech', growth: 65, volume: 9800, competition: 'faible' },
          { id: 5, keyword: 'accessoire voiture', growth: 54, volume: 14300, competition: 'moyenne' },
        ];
        
        setProducts(simulatedProducts);
        setTrends(simulatedTrends);
      } catch (error) {
        console.error('Error fetching data analyzer data:', error);
        toast.error('Erreur lors de la récupération des données d\'analyse');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const handleStartAnalysis = (e) => {
    e.preventDefault();
    toast.info(`Analyse démarrée pour la niche: ${analysisForm.niche}`);
    // En production, on appellerait dataAnalyzerApi.startAnalysis(analysisForm);
  };

  const renderProductsTab = () => (
    <div className="mt-4">
      <div className="flex flex-col">
        <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
            <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Produit</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tendance</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Niche</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prix</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Marge</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {products.map((product) => (
                    <tr key={product.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{product.name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${product.score > 80 ? 'bg-green-100' : product.score > 60 ? 'bg-yellow-100' : 'bg-red-100'}`}>
                              <span className={`text-sm font-medium ${product.score > 80 ? 'text-green-800' : product.score > 60 ? 'text-yellow-800' : 'text-red-800'}`}>{product.score}</span>
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          product.trend === 'up' ? 'bg-green-100 text-green-800' : 
                          product.trend === 'down' ? 'bg-red-100 text-red-800' : 
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {product.trend === 'up' ? 'En hausse' : 
                           product.trend === 'down' ? 'En baisse' : 
                           'Stable'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{product.niche}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{product.price.toFixed(2)} €</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{product.margin}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTrendsTab = () => (
    <div className="mt-4">
      <div className="flex flex-col">
        <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
            <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mot-clé</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Croissance</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Volume</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Compétition</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {trends.map((trend) => (
                    <tr key={trend.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{trend.keyword}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className="text-sm text-gray-900">+{trend.growth}%</span>
                          <span className="ml-2 flex-shrink-0 h-4 w-4">
                            <svg className="h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                            </svg>
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trend.volume.toLocaleString()}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          trend.competition === 'élevée' ? 'bg-red-100 text-red-800' : 
                          trend.competition === 'moyenne' ? 'bg-yellow-100 text-yellow-800' : 
                          'bg-green-100 text-green-800'
                        }`}>
                          {trend.competition}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAnalysisTab = () => (
    <div className="mt-4 bg-white shadow overflow-hidden sm:rounded-lg">
      <div className="px-4 py-5 sm:px-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Lancer une nouvelle analyse</h3>
        <p className="mt-1 max-w-2xl text-sm text-gray-500">
          Entrez les paramètres pour analyser une niche ou un produit spécifique
        </p>
      </div>
      <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
        <form onSubmit={handleStartAnalysis}>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label htmlFor="niche" className="block text-sm font-medium text-gray-700">Niche ou Mot-clé</label>
              <input
                type="text"
                name="niche"
                id="niche"
                className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                value={analysisForm.niche}
                onChange={(e) => setAnalysisForm({ ...analysisForm, niche: e.target.value })}
                required
              />
            </div>
            <div>
              <label htmlFor="maxProducts" className="block text-sm font-medium text-gray-700">Nombre max de produits</label>
              <input
                type="number"
                name="maxProducts"
                id="maxProducts"
                className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                value={analysisForm.maxProducts}
                onChange={(e) => setAnalysisForm({ ...analysisForm, maxProducts: parseInt(e.target.value) })}
                min="1"
                max="50"
              />
            </div>
          </div>
          
          <div className="mt-4">
            <div className="flex items-start">
              <div className="flex items-center h-5">
                <input
                  id="includeCompetition"
                  name="includeCompetition"
                  type="checkbox"
                  className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                  checked={analysisForm.includeCompetition}
                  onChange={(e) => setAnalysisForm({ ...analysisForm, includeCompetition: e.target.checked })}
                />
              </div>
              <div className="ml-3 text-sm">
                <label htmlFor="includeCompetition" className="font-medium text-gray-700">Inclure analyse de la concurrence</label>
                <p className="text-gray-500">Analyse des concurrents principaux et de leurs stratégies marketing</p>
              </div>
            </div>
          </div>
          
          <div className="mt-6">
            <button
              type="submit"
              className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Lancer l'analyse
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900">Data Analyzer</h1>
      <p className="mt-1 text-sm text-gray-500">
        Analyse des produits à fort potentiel et des tendances du marché
      </p>

      <div className="mt-6">
        <div className="sm:hidden">
          <label htmlFor="tabs" className="sr-only">Sélectionnez un onglet</label>
          <select
            id="tabs"
            name="tabs"
            className="block w-full focus:ring-primary-500 focus:border-primary-500 border-gray-300 rounded-md"
            value={activeTab}
            onChange={(e) => setActiveTab(e.target.value)}
          >
            <option value="products">Produits</option>
            <option value="trends">Tendances</option>
            <option value="analysis">Nouvelle analyse</option>
          </select>
        </div>
        <div className="hidden sm:block">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('products')}
                className={`${activeTab === 'products' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} w-1/4 py-4 px-1 text-center border-b-2 font-medium text-sm`}
              >
                Produits
              </button>
              <button
                onClick={() => setActiveTab('trends')}
                className={`${activeTab === 'trends' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} w-1/4 py-4 px-1 text-center border-b-2 font-medium text-sm`}
              >
                Tendances
              </button>
              <button
                onClick={() => setActiveTab('analysis')}
                className={`${activeTab === 'analysis' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} w-1/4 py-4 px-1 text-center border-b-2 font-medium text-sm`}
              >
                Nouvelle analyse
              </button>
            </nav>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
          </div>
        ) : (
          <div>
            {activeTab === 'products' && renderProductsTab()}
            {activeTab === 'trends' && renderTrendsTab()}
            {activeTab === 'analysis' && renderAnalysisTab()}
          </div>
        )}
      </div>
    </div>
  );
};

export default DataAnalyzer;
