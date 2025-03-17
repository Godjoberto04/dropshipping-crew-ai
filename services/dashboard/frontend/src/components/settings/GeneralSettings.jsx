import React from 'react';

const GeneralSettings = ({ config, updateConfig }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium leading-6 text-gray-900">Paramètres généraux</h3>
        <p className="mt-1 text-sm text-gray-500">Configuration générale du système</p>
      </div>

      <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
        <div className="sm:col-span-3">
          <label htmlFor="siteName" className="block text-sm font-medium text-gray-700">Nom du site</label>
          <input
            type="text"
            name="siteName"
            id="siteName"
            className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
            value={config.general.siteName}
            onChange={(e) => updateConfig('general', 'siteName', e.target.value)}
          />
        </div>

        <div className="sm:col-span-3">
          <label htmlFor="adminEmail" className="block text-sm font-medium text-gray-700">Email administrateur</label>
          <input
            type="email"
            name="adminEmail"
            id="adminEmail"
            className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
            value={config.general.adminEmail}
            onChange={(e) => updateConfig('general', 'adminEmail', e.target.value)}
          />
        </div>

        <div className="sm:col-span-3">
          <label htmlFor="language" className="block text-sm font-medium text-gray-700">Langue</label>
          <select
            id="language"
            name="language"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            value={config.general.language}
            onChange={(e) => updateConfig('general', 'language', e.target.value)}
          >
            <option value="fr">Français</option>
            <option value="en">English</option>
            <option value="es">Español</option>
            <option value="de">Deutsch</option>
          </select>
        </div>

        <div className="sm:col-span-3">
          <label htmlFor="timeZone" className="block text-sm font-medium text-gray-700">Fuseau horaire</label>
          <select
            id="timeZone"
            name="timeZone"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            value={config.general.timeZone}
            onChange={(e) => updateConfig('general', 'timeZone', e.target.value)}
          >
            <option value="Europe/Paris">Europe/Paris</option>
            <option value="Europe/London">Europe/London</option>
            <option value="America/New_York">America/New_York</option>
            <option value="Asia/Tokyo">Asia/Tokyo</option>
          </select>
        </div>
      </div>
    </div>
  );
};

export default GeneralSettings;
