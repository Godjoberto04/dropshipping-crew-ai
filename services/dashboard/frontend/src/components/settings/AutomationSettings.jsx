import React from 'react';

const AutomationSettings = ({ config, updateConfig }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium leading-6 text-gray-900">Paramètres d'automatisation</h3>
        <p className="mt-1 text-sm text-gray-500">Configuration des processus automatisés</p>
      </div>

      <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
        <div className="sm:col-span-3">
          <label htmlFor="updateFrequency" className="block text-sm font-medium text-gray-700">Fréquence des mises à jour</label>
          <select
            id="updateFrequency"
            name="updateFrequency"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            value={config.automation.updateFrequency}
            onChange={(e) => updateConfig('automation', 'updateFrequency', e.target.value)}
          >
            <option value="hourly">Toutes les heures</option>
            <option value="daily">Quotidienne</option>
            <option value="weekly">Hebdomadaire</option>
            <option value="monthly">Mensuelle</option>
          </select>
        </div>

        <div className="sm:col-span-3">
          <label htmlFor="priceUpdateStrategy" className="block text-sm font-medium text-gray-700">Stratégie de mise à jour des prix</label>
          <select
            id="priceUpdateStrategy"
            name="priceUpdateStrategy"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            value={config.automation.priceUpdateStrategy}
            onChange={(e) => updateConfig('automation', 'priceUpdateStrategy', e.target.value)}
          >
            <option value="fixed">Marge fixe</option>
            <option value="competitive">Compétitive</option>
            <option value="dynamic">Dynamique</option>
          </select>
        </div>

        <div className="sm:col-span-3">
          <label htmlFor="contentUpdateFrequency" className="block text-sm font-medium text-gray-700">Fréquence des mises à jour de contenu</label>
          <select
            id="contentUpdateFrequency"
            name="contentUpdateFrequency"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            value={config.automation.contentUpdateFrequency}
            onChange={(e) => updateConfig('automation', 'contentUpdateFrequency', e.target.value)}
          >
            <option value="daily">Quotidienne</option>
            <option value="weekly">Hebdomadaire</option>
            <option value="monthly">Mensuelle</option>
          </select>
        </div>

        <div className="sm:col-span-3">
          <label htmlFor="marketAnalysisFrequency" className="block text-sm font-medium text-gray-700">Fréquence des analyses de marché</label>
          <select
            id="marketAnalysisFrequency"
            name="marketAnalysisFrequency"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            value={config.automation.marketAnalysisFrequency}
            onChange={(e) => updateConfig('automation', 'marketAnalysisFrequency', e.target.value)}
          >
            <option value="daily">Quotidienne</option>
            <option value="weekly">Hebdomadaire</option>
            <option value="monthly">Mensuelle</option>
          </select>
        </div>

        <div className="sm:col-span-6">
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                id="autoPublishProducts"
                name="autoPublishProducts"
                type="checkbox"
                className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                checked={config.automation.autoPublishProducts}
                onChange={(e) => updateConfig('automation', 'autoPublishProducts', e.target.checked)}
              />
            </div>
            <div className="ml-3 text-sm">
              <label htmlFor="autoPublishProducts" className="font-medium text-gray-700">Publication automatique des produits</label>
              <p className="text-gray-500">Les nouveaux produits détectés par l'analyse de marché sont automatiquement publiés sur la boutique</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutomationSettings;
