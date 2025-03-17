import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import DashboardLayout from './components/layout/DashboardLayout';
import Login from './pages/Login';
import Overview from './pages/Overview';
import DataAnalyzer from './pages/DataAnalyzer';
import WebsiteBuilder from './pages/WebsiteBuilder';
import ContentGenerator from './pages/ContentGenerator';
import OrderManager from './pages/OrderManager';
import SiteUpdater from './pages/SiteUpdater';
import ShopifyStores from './pages/ShopifyStores';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

import { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';

const App = () => {
  const { isAuthenticated, checkAuth } = useAuth();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <>
      <ToastContainer position="top-right" autoClose={3000} />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Overview />} />
          <Route path="data-analyzer" element={<DataAnalyzer />} />
          <Route path="website-builder" element={<WebsiteBuilder />} />
          <Route path="content-generator" element={<ContentGenerator />} />
          <Route path="order-manager" element={<OrderManager />} />
          <Route path="site-updater" element={<SiteUpdater />} />
          <Route path="shopify-stores" element={<ShopifyStores />} />
          <Route path="settings" element={<Settings />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </>
  );
};

export default App;
