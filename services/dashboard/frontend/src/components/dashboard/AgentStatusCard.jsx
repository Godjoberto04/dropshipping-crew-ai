import React from 'react';

const AgentStatusCard = ({ agent, data }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      case 'inactive':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const renderMetrics = (metrics) => {
    return Object.entries(metrics).map(([key, value]) => (
      <div key={key} className="flex justify-between py-1">
        <span className="text-gray-500">
          {key
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, (str) => str.toUpperCase())
            .replace(/([A-Z])/g, (match) => match.toLowerCase())}
        </span>
        <span className="font-medium">{value}</span>
      </div>
    ));
  };

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
        <h3 className="text-lg leading-6 font-medium text-gray-900">{agent}</h3>
        <div className={`px-2 py-1 rounded-full ${getStatusColor(data.status)}`}>
          <span className="text-xs font-medium">
            {data.status === 'active' ? 'Actif' : 
             data.status === 'warning' ? 'Avertissement' : 
             data.status === 'error' ? 'Erreur' : 'Inactif'}
          </span>
        </div>
      </div>
      <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-500">Dernière activité</h4>
            <p className="mt-1 text-sm text-gray-900">{formatDate(data.lastActivity)}</p>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-500">Métriques</h4>
            <div className="mt-2 text-sm">
              {renderMetrics(data.metrics)}
            </div>
          </div>
        </div>
      </div>
      <div className="border-t border-gray-200 px-4 py-4 sm:px-6">
        <button
          type="button"
          className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          Voir les détails
        </button>
      </div>
    </div>
  );
};

export default AgentStatusCard;
