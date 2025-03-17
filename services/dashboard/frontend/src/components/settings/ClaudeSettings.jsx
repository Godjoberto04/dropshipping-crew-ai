import React from 'react';

const ClaudeSettings = ({ config, updateConfig }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium leading-6 text-gray-900">Paramètres Claude (IA)</h3>
        <p className="mt-1 text-sm text-gray-500">Configuration de l'intégration avec l'API Claude d'Anthropic</p>
      </div>

      <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
        <div className="sm:col-span-6">
          <label htmlFor="claudeApiKey" className="block text-sm font-medium text-gray-700">Clé API Claude</label>
          <input
            type="password"
            name="claudeApiKey"
            id="claudeApiKey"
            className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
            value={config.claude.apiKey}
            onChange={(e) => updateConfig('claude', 'apiKey', e.target.value)}
          />
        </div>

        <div className="sm:col-span-3">
          <label htmlFor="claudeModelVersion" className="block text-sm font-medium text-gray-700">Version du modèle</label>
          <select
            id="claudeModelVersion"
            name="claudeModelVersion"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            value={config.claude.modelVersion}
            onChange={(e) => updateConfig('claude', 'modelVersion', e.target.value)}
          >
            <option value="claude-3-opus">Claude 3 Opus</option>
            <option value="claude-3-sonnet">Claude 3 Sonnet</option>
            <option value="claude-3-haiku">Claude 3 Haiku</option>
          </select>
        </div>

        <div className="sm:col-span-3">
          <label htmlFor="claudeMaxTokens" className="block text-sm font-medium text-gray-700">Nombre max de tokens</label>
          <input
            type="number"
            name="claudeMaxTokens"
            id="claudeMaxTokens"
            className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
            value={config.claude.maxTokens}
            onChange={(e) => updateConfig('claude', 'maxTokens', parseInt(e.target.value))}
            min="1024"
            max="100000"
            step="1024"
          />
        </div>

        <div className="sm:col-span-6">
          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Tester la connexion
          </button>
        </div>
      </div>
    </div>
  );
};

export default ClaudeSettings;
