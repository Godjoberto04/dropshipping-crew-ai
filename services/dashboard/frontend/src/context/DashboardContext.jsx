import React, { createContext, useContext, useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { useApiService } from '../services/api';

const DashboardContext = createContext();

export const useDashboard = () => useContext(DashboardContext);

export const DashboardProvider = ({ children }) => {
  const api = useApiService();
  const [systemStatus, setSystemStatus] = useState({});
  const [agentStatuses, setAgentStatuses] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchSystemStatus = async () => {
    try {
      setLoading(true);
      // Dans un premier temps, nous simulons les données
      // À remplacer par un vrai appel API quand disponible
      // const response = await api.get('/system/status');
      
      const simulatedStatus = {
        cpu: Math.floor(Math.random() * 70) + 10,
        memory: Math.floor(Math.random() * 70) + 10,
        disk: Math.floor(Math.random() * 30) + 60,
        uptime: '5d 12h 34m',
        activeAgents: 5,
        totalAgents: 5,
        activeShops: 1,
        totalOrders: 26,
        pendingOrders: 3,
        lastIncident: '2025-03-15T16:45:00Z'
      };
      
      setSystemStatus(simulatedStatus);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      console.error('Error fetching system status:', err);
      setError('Failed to fetch system status');
      toast.error('Impossible de récupérer le statut du système');
    } finally {
      setLoading(false);
    }
  };

  const fetchAgentStatuses = async () => {
    try {
      setLoading(true);
      // Simulation des données des agents
      // À remplacer par un vrai appel API quand disponible
      // const response = await api.get('/agents/status');
      
      const simulatedAgentStatuses = {
        'data-analyzer': {
          status: 'active',
          lastActivity: '2025-03-17T08:45:12Z',
          metrics: {
            analyzedProducts: 234,
            trendingNiches: 5,
            pendingAnalyses: 0
          }
        },
        'website-builder': {
          status: 'active',
          lastActivity: '2025-03-17T07:32:05Z',
          metrics: {
            siteUpdates: 12,
            pagesCreated: 18,
            templatesUsed: 3
          }
        },
        'content-generator': {
          status: 'active',
          lastActivity: '2025-03-17T09:05:45Z',
          metrics: {
            generatedDescriptions: 156,
            seoOptimizations: 42,
            qualityScore: 92
          }
        },
        'order-manager': {
          status: 'active',
          lastActivity: '2025-03-17T10:11:30Z',
          metrics: {
            processedOrders: 26,
            pendingOrders: 3,
            supplierIssues: 0
          }
        },
        'site-updater': {
          status: 'active',
          lastActivity: '2025-03-17T08:20:15Z',
          metrics: {
            abTests: 3,
            priceUpdates: 18,
            productRotations: 5,
            performanceIndex: 87
          }
        }
      };
      
      setAgentStatuses(simulatedAgentStatuses);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      console.error('Error fetching agent statuses:', err);
      setError('Failed to fetch agent statuses');
      toast.error('Impossible de récupérer le statut des agents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSystemStatus();
    fetchAgentStatuses();
    
    // Mise à jour périodique des données
    const intervalId = setInterval(() => {
      fetchSystemStatus();
      fetchAgentStatuses();
    }, 60000); // Mise à jour toutes les minutes
    
    return () => clearInterval(intervalId);
  }, []);

  return (
    <DashboardContext.Provider
      value={{
        systemStatus,
        agentStatuses,
        loading,
        error,
        lastUpdated,
        refreshData: () => {
          fetchSystemStatus();
          fetchAgentStatuses();
        }
      }}
    >
      {children}
    </DashboardContext.Provider>
  );
};
