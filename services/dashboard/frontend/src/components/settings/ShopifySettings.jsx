import React from 'react';

const ShopifySettings = ({ config, updateConfig }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium leading-6 text-gray-900">Paramètres Shopify</h3>
        <p className="mt-1 text-sm text-gray-500">Configuration de l'intégration avec Shopify</p>
      </div>

      <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
        <div className="sm:col-span-3">
          <label htmlFor="shopifyApiKey" className="block text-sm font-medium text-gray-700">Clé API</label>
          <input
            type="password"
            name="shopifyApiKey"
            id="shopifyApiKey"
            className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
            value={config.shopify.apiKey}
            onChange={(e) => updateConfig('shopify', 'apiKey', e.target.value)}
          />
        </div>

        <div className="sm:col-span-3">
          <label htmlFor="shopifyApiSecret" className="block text-sm font-medium text-gray-700">Secret API</label>
          <input
            type="password"
            name="shopifyApiSecret"
            id="shopifyApiSecret"
            className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
            value={config.shopify.apiSecret}
            onChange={(e) => updateConfig('shopify', 'apiSecret', e.target.value)}
          />
        </div>

        <div className="sm:col-span-3">
          <label htmlFor="shopifyStoreDomain" className="block text-sm font-medium text-gray-700">Domaine de la boutique</label>
          <input
            type="text"
            name="shopifyStoreDomain"
            id="shopifyStoreDomain"
            className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
            value={config.shopify.storeDomain}
            onChange={(e) => updateConfig('shopify', 'storeDomain', e.target.value)}
          />
        </div>

        <div className="sm:col-span-3">
          <label htmlFor="shopifyAccessToken" className="block text-sm font-medium text-gray-700">Token d'accès</label>
          <input
            type="password"
            name="shopifyAccessToken"
            id="shopifyAccessToken"
            className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
            value={config.shopify.accessToken}
            onChange={(e) => updateConfig('shopify', 'accessToken', e.target.value)}
          />
        </div>

        <div className="sm:col-span-6">
          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Vérifier la connexion
          </button>
        </div>
      </div>
    </div>
  );
};

export default ShopifySettings;
