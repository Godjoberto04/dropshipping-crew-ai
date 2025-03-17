import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { systemApi } from '../services/api';

// Import des composants de paramètres
import GeneralSettings from '../components/settings/GeneralSettings';
import ShopifySettings from '../components/settings/ShopifySettings';
import ClaudeSettings from '../components/settings/ClaudeSettings';
import DropshippingSettings from '../components/settings/DropshippingSettings';
import AutomationSettings from '../components/settings/AutomationSettings';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('general');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState({
    general: {
      siteName: 'Dropshipping Crew AI',
      adminEmail: 'admin@example.com',
      language: 'fr',
      timeZone: 'Europe/Paris',
    },
    shopify: {
      apiKey: '••••••••••••••••',
      apiSecret: '••••••••••••••••',
      storeDomain: 'mystore.myshopify.com',
      accessToken: '••••••••••••••••',
    },
    claude: {
      apiKey: '••••••••••••••••',
      modelVersion: 'claude-3-opus',
      maxTokens: 4096,
    },
    dropshipping: {
      defaultSupplier: 'AliExpress',
      suppliers: [
        { name: 'AliExpress', active: true },
        { name: 'CJ Dropshipping', active: true },
        { name: 'DHGate', active: false },
      ],
      autoOrderThreshold: 3,
      minMarginPercent: 40,
    },
    automation: {
      updateFrequency: 'daily',
      priceUpdateStrategy: 'competitive',
      contentUpdateFrequency: 'weekly',
      marketAnalysisFrequency: 'weekly',
      autoPublishProducts: true,
    },
  });

  useEffect(() => {
    const fetchConfig = async () => {
      setLoading(true);
      try {
        // En production, on utiliserait l'API réelle
        // const response = await systemApi.getConfiguration();
        // setConfig(response.data);
        
        // Pour le moment, on utilise les données simulées
        setTimeout(() => {
          setLoading(false);
        }, 800);
      } catch (error) {
        console.error('Error fetching configuration:', error);
        toast.error('Erreur lors de la récupération de la configuration');
        setLoading(false);
      }
    };
    
    fetchConfig();
  }, []);

  const handleSaveConfig = async () => {
    setSaving(true);
    try {
      // En production, on utiliserait l'API réelle
      // await systemApi.updateConfiguration(config);
      
      // Simulation de la sauvegarde
      setTimeout(() => {
        toast.success('Configuration enregistrée avec succès');
        setSaving(false);
      }, 1000);
    } catch (error) {
      console.error('Error saving configuration:', error);
      toast.error('Erreur lors de l\'enregistrement de la configuration');
      setSaving(false);
    }
  };

  const updateConfig = (section, field, value) => {
    setConfig({
      ...config,
      [section]: {
        ...config[section],
        [field]: value,
      },
    });
  };

  // Composant pour le contenu de l'onglet actif
  const TabContent = () => {
    switch (activeTab) {
      case 'general':
        return <GeneralSettings config={config} updateConfig={updateConfig} />;
      case 'shopify':
        return <ShopifySettings config={config} updateConfig={updateConfig} />;
      case 'claude':
        return <ClaudeSettings config={config} updateConfig={updateConfig} />;
      case 'dropshipping':
        return <DropshippingSettings config={config} updateConfig={updateConfig} />;
      case 'automation':
        return <AutomationSettings config={config} updateConfig={updateConfig} />;
      default:
        return <GeneralSettings config={config} updateConfig={updateConfig} />;
    }
  };

  return (
    <div>
      <div className="pb-5 border-b border-gray-200 sm:flex sm:items-center sm:justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Paramètres</h1>
        <div className="mt-3 sm:mt-0 sm:ml-4">
          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            onClick={handleSaveConfig}
            disabled={saving}
          >
            {saving ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Enregistrement...
              </>
            ) : 'Enregistrer les modifications'}
          </button>
        </div>
      </div>

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
            <option value="general">Général</option>
            <option value="shopify">Shopify</option>
            <option value="claude">Claude (IA)</option>
            <option value="dropshipping">Dropshipping</option>
            <option value="automation">Automatisation</option>
          </select>
        </div>
        <div className="hidden sm:block">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('general')}
                className={`${activeTab === 'general' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Général
              </button>
              <button
                onClick={() => setActiveTab('shopify')}
                className={`${activeTab === 'shopify' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Shopify
              </button>
              <button
                onClick={() => setActiveTab('claude')}
                className={`${activeTab === 'claude' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Claude (IA)
              </button>
              <button
                onClick={() => setActiveTab('dropshipping')}
                className={`${activeTab === 'dropshipping' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Dropshipping
              </button>
              <button
                onClick={() => setActiveTab('automation')}
                className={`${activeTab === 'automation' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Automatisation
              </button>
            </nav>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
          </div>
        ) : (
          <div className="mt-6 p-4 bg-white rounded-lg shadow">
            <TabContent />
          </div>
        )}
      </div>
    </div>
  );
};

export default Settings;
