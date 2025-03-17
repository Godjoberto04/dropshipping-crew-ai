import axios from 'axios';
import { useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

// Création d'une instance axios
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const useApiService = () => {
  const { logout } = useAuth();

  // Ajout du token d'authentification à chaque requête
  apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  });

  // Gestion des erreurs d'authentification
  apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response && (error.response.status === 401 || error.response.status === 403)) {
        logout();
      }
      return Promise.reject(error);
    }
  );

  const get = useCallback((url, config = {}) => {
    return apiClient.get(url, config);
  }, []);

  const post = useCallback((url, data, config = {}) => {
    return apiClient.post(url, data, config);
  }, []);

  const put = useCallback((url, data, config = {}) => {
    return apiClient.put(url, data, config);
  }, []);

  const del = useCallback((url, config = {}) => {
    return apiClient.delete(url, config);
  }, []);

  return { get, post, put, delete: del };
};

export const dataAnalyzerApi = {
  getProducts: () => apiClient.get('/data-analyzer/products'),
  getTrends: () => apiClient.get('/data-analyzer/trends'),
  getNiches: () => apiClient.get('/data-analyzer/niches'),
  getMarketAnalysis: (niche) => apiClient.get(`/data-analyzer/market-analysis/${niche}`),
  startAnalysis: (params) => apiClient.post('/data-analyzer/analyze', params),
};

export const websiteBuilderApi = {
  getSiteStatus: () => apiClient.get('/website-builder/status'),
  getPages: () => apiClient.get('/website-builder/pages'),
  getThemes: () => apiClient.get('/website-builder/themes'),
  updateSite: (updates) => apiClient.put('/website-builder/update', updates),
};

export const contentGeneratorApi = {
  getStatistics: () => apiClient.get('/content-generator/statistics'),
  getTemplates: () => apiClient.get('/content-generator/templates'),
  generateContent: (params) => apiClient.post('/content-generator/generate', params),
};

export const orderManagerApi = {
  getOrders: (status) => apiClient.get(`/order-manager/orders?status=${status}`),
  getSuppliers: () => apiClient.get('/order-manager/suppliers'),
  updateOrder: (orderId, updates) => apiClient.put(`/order-manager/orders/${orderId}`, updates),
};

export const siteUpdaterApi = {
  getMetrics: () => apiClient.get('/site-updater/metrics'),
  getAbTests: () => apiClient.get('/site-updater/ab-tests'),
  getPriceUpdates: () => apiClient.get('/site-updater/price-updates'),
  startOptimization: (type, params) => apiClient.post(`/site-updater/optimize/${type}`, params),
};

export const shopifyApi = {
  getStores: () => apiClient.get('/shopify/stores'),
  getStoreMetrics: (storeId) => apiClient.get(`/shopify/stores/${storeId}/metrics`),
  getProducts: (storeId) => apiClient.get(`/shopify/stores/${storeId}/products`),
};

export const systemApi = {
  getStatus: () => apiClient.get('/system/status'),
  getConfiguration: () => apiClient.get('/system/configuration'),
  updateConfiguration: (config) => apiClient.put('/system/configuration', config),
  getLogs: (service, level) => apiClient.get(`/system/logs?service=${service}&level=${level}`),
};
