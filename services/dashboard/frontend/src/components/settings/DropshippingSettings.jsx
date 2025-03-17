import React from 'react';

const DropshippingSettings = ({ config, updateConfig }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium leading-6 text-gray-900">Paramètres Dropshipping</h3>
        <p className="mt-1 text-sm text-gray-500">Configuration des fournisseurs et règles de dropshipping</p>
      </div>

      <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
        <div className="sm:col-span-3">
          <label htmlFor="defaultSupplier" className="block text-sm font-medium text-gray-700">Fournisseur par défaut</label>
          <select
            id="defaultSupplier"
            name="defaultSupplier"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            value={config.dropshipping.defaultSupplier}
            onChange={(e) => updateConfig('dropshipping', 'defaultSupplier', e.target.value)}
          >
            {config.dropshipping.suppliers.map(supplier => (
              <option key={supplier.name} value={supplier.name}>{supplier.name}</option>
            ))}
          </select>
        </div>

        <div className="sm:col-span-3">
          <label htmlFor="autoOrderThreshold" className="block text-sm font-medium text-gray-700">Seuil de commande auto</label>
          <input
            type="number"
            name="autoOrderThreshold"
            id="autoOrderThreshold"
            className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
            value={config.dropshipping.autoOrderThreshold}
            onChange={(e) => updateConfig('dropshipping', 'autoOrderThreshold', parseInt(e.target.value))}
            min="0"
            max="10"
          />
          <p className="mt-2 text-sm text-gray-500">Nombre de commandes avant déclenchement auto</p>
        </div>

        <div className="sm:col-span-3">
          <label htmlFor="minMarginPercent" className="block text-sm font-medium text-gray-700">Marge minimale (%)</label>
          <input
            type="number"
            name="minMarginPercent"
            id="minMarginPercent"
            className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
            value={config.dropshipping.minMarginPercent}
            onChange={(e) => updateConfig('dropshipping', 'minMarginPercent', parseInt(e.target.value))}
            min="0"
            max="100"
          />
        </div>

        <div className="sm:col-span-6">
          <p className="text-sm font-medium text-gray-700 mb-2">Fournisseurs actifs</p>
          <div className="mt-4 space-y-4">
            {config.dropshipping.suppliers.map((supplier, index) => (
              <div key={supplier.name} className="flex items-start">
                <div className="flex items-center h-5">
                  <input
                    id={`supplier-${supplier.name}`}
                    name={`supplier-${supplier.name}`}
                    type="checkbox"
                    className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                    checked={supplier.active}
                    onChange={(e) => {
                      const newSuppliers = [...config.dropshipping.suppliers];
                      newSuppliers[index] = {
                        ...newSuppliers[index],
                        active: e.target.checked,
                      };
                      updateConfig('dropshipping', 'suppliers', newSuppliers);
                    }}
                  />
                </div>
                <div className="ml-3 text-sm">
                  <label htmlFor={`supplier-${supplier.name}`} className="font-medium text-gray-700">{supplier.name}</label>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DropshippingSettings;
