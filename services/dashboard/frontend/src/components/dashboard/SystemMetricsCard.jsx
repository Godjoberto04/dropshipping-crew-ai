import React from 'react';

const SystemMetricsCard = ({ systemStatus }) => {
  return (
    <div className="bg-white overflow-hidden shadow rounded-lg divide-y divide-gray-200">
      <div className="px-4 py-5 sm:px-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">État du système</h3>
        <p className="mt-1 max-w-2xl text-sm text-gray-500">
          Ressources et métriques système
        </p>
      </div>
      <div className="px-4 py-5 sm:p-6">
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <div>
            <h4 className="text-sm font-medium text-gray-500">CPU</h4>
            <div className="mt-1 relative pt-1">
              <div className="overflow-hidden h-2 text-xs flex rounded bg-gray-200">
                <div
                  style={{ width: `${systemStatus.cpu}%` }}
                  className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${
                    systemStatus.cpu > 80 ? 'bg-red-500' : systemStatus.cpu > 60 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                ></div>
              </div>
              <span className="text-xs font-semibold inline-block text-gray-600 mt-1">
                {systemStatus.cpu}%
              </span>
            </div>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-500">Mémoire</h4>
            <div className="mt-1 relative pt-1">
              <div className="overflow-hidden h-2 text-xs flex rounded bg-gray-200">
                <div
                  style={{ width: `${systemStatus.memory}%` }}
                  className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${
                    systemStatus.memory > 80 ? 'bg-red-500' : systemStatus.memory > 60 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                ></div>
              </div>
              <span className="text-xs font-semibold inline-block text-gray-600 mt-1">
                {systemStatus.memory}%
              </span>
            </div>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-500">Disque</h4>
            <div className="mt-1 relative pt-1">
              <div className="overflow-hidden h-2 text-xs flex rounded bg-gray-200">
                <div
                  style={{ width: `${systemStatus.disk}%` }}
                  className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${
                    systemStatus.disk > 80 ? 'bg-red-500' : systemStatus.disk > 60 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                ></div>
              </div>
              <span className="text-xs font-semibold inline-block text-gray-600 mt-1">
                {systemStatus.disk}%
              </span>
            </div>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-500">Uptime</h4>
            <p className="mt-1 text-sm text-gray-900">{systemStatus.uptime}</p>
          </div>
        </div>
      </div>
      <div className="px-4 py-4 sm:px-6 bg-gray-50">
        <div className="grid grid-cols-2 gap-5 sm:grid-cols-4">
          <div className="text-center">
            <p className="text-sm font-medium text-gray-500">Agents actifs</p>
            <p className="mt-1 text-3xl font-semibold text-gray-900">
              {systemStatus.activeAgents}/{systemStatus.totalAgents}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-500">Boutiques</p>
            <p className="mt-1 text-3xl font-semibold text-gray-900">
              {systemStatus.activeShops}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-500">Commandes totales</p>
            <p className="mt-1 text-3xl font-semibold text-gray-900">
              {systemStatus.totalOrders}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-500">Commandes en attente</p>
            <p className="mt-1 text-3xl font-semibold text-gray-900">
              {systemStatus.pendingOrders}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemMetricsCard;
