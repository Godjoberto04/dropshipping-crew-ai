import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { 
  Layers, 
  Store, 
  Layout, 
  BarChart2, 
  Package, 
  Grid, 
  Settings, 
  RefreshCw, 
  Edit,
  Eye,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';

import { getShopifyStore, refreshThemeCache, updateTheme, createCollection } from '../services/api';
import { ThemesTab, CollectionsTab, PagesTab, SettingsTab } from '../components/dashboard/WebsiteBuilderComponents';

// Component for website builder dashboard
const WebsiteBuilder = () => {
  // State management
  const [storeData, setStoreData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [themeData, setThemeData] = useState(null);
  const [collectionsData, setCollectionsData] = useState([]);
  const [pageData, setPageData] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  // Fetch store data
  useEffect(() => {
    const fetchStoreData = async () => {
      try {
        setLoading(true);
        const data = await getShopifyStore();
        setStoreData(data.store);
        setThemeData(data.theme);
        setCollectionsData(data.collections);
        setPageData(data.pages);
      } catch (error) {
        console.error('Error fetching store data:', error);
        toast.error('Failed to load store data');
      } finally {
        setLoading(false);
      }
    };

    fetchStoreData();
  }, []);

  // Handle refresh of theme cache
  const handleRefreshThemeCache = async () => {
    try {
      setRefreshing(true);
      await refreshThemeCache();
      toast.success('Theme cache refreshed successfully');
      
      // Refresh theme data
      const data = await getShopifyStore();
      setThemeData(data.theme);
    } catch (error) {
      console.error('Error refreshing theme cache:', error);
      toast.error('Failed to refresh theme cache');
    } finally {
      setRefreshing(false);
    }
  };

  // Render loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-full w-full">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          <p className="text-gray-500">Loading store data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container px-6 mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-800">Website Builder</h1>
          <p className="text-gray-500">Manage your Shopify store and website appearance</p>
        </div>
        <div>
          <button
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 transition-colors"
            onClick={handleRefreshThemeCache}
            disabled={refreshing}
          >
            <RefreshCw size={18} className={`mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh Cache
          </button>
        </div>
      </div>

      {/* Store Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-5">
          <div className="flex items-center mb-4">
            <Store className="h-8 w-8 text-blue-600 mr-3" />
            <div>
              <h2 className="text-lg font-medium text-gray-700">Store Status</h2>
              <p className="text-sm text-gray-500">Current store operational status</p>
            </div>
          </div>
          <div className="flex items-center">
            <div className={`h-3 w-3 rounded-full mr-2 ${storeData?.isActive ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="font-medium">{storeData?.isActive ? 'Active' : 'Inactive'}</span>
          </div>
          <div className="mt-4">
            <p className="text-sm text-gray-600">URL: <a href={storeData?.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{storeData?.url}</a></p>
            <p className="text-sm text-gray-600 mt-1">Last updated: {new Date(storeData?.lastUpdated).toLocaleString()}</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-5">
          <div className="flex items-center mb-4">
            <Layout className="h-8 w-8 text-indigo-600 mr-3" />
            <div>
              <h2 className="text-lg font-medium text-gray-700">Active Theme</h2>
              <p className="text-sm text-gray-500">Current theme configuration</p>
            </div>
          </div>
          <div className="mt-2">
            <div className="flex items-start space-x-2">
              {themeData?.previewImage && (
                <img src={themeData.previewImage} alt="Theme preview" className="w-20 h-20 object-cover rounded border" />
              )}
              <div>
                <p className="font-medium">{themeData?.name || 'Default theme'}</p>
                <p className="text-sm text-gray-600 mt-1">Version: {themeData?.version || '1.0'}</p>
                <div className="flex mt-2">
                  <button className="text-sm flex items-center text-blue-600 hover:text-blue-800 mr-4">
                    <Edit size={14} className="mr-1" /> Customize
                  </button>
                  <button className="text-sm flex items-center text-blue-600 hover:text-blue-800">
                    <Eye size={14} className="mr-1" /> Preview
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-5">
          <div className="flex items-center mb-4">
            <BarChart2 className="h-8 w-8 text-green-600 mr-3" />
            <div>
              <h2 className="text-lg font-medium text-gray-700">Site Performance</h2>
              <p className="text-sm text-gray-500">Current site metrics</p>
            </div>
          </div>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between items-center text-sm mb-1">
                <span className="text-gray-600">Page Speed</span>
                <span className="font-medium">{storeData?.metrics?.pageSpeed || '0'}s</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-600 h-2 rounded-full" 
                  style={{ width: `${Math.min(100, 100 - (storeData?.metrics?.pageSpeed * 20 || 0))}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center text-sm mb-1">
                <span className="text-gray-600">Mobile Score</span>
                <span className="font-medium">{storeData?.metrics?.mobileScore || '0'}/100</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ width: `${storeData?.metrics?.mobileScore || 0}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center text-sm mb-1">
                <span className="text-gray-600">SEO Score</span>
                <span className="font-medium">{storeData?.metrics?.seoScore || '0'}/100</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-indigo-600 h-2 rounded-full" 
                  style={{ width: `${storeData?.metrics?.seoScore || 0}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs for Website Management */}
      <div className="border-b border-gray-200 mb-6">
        <ul className="flex flex-wrap -mb-px">
          <li className="mr-2">
            <button 
              className={`inline-block py-4 px-4 text-sm font-medium ${activeTab === 'overview' 
                ? 'text-blue-600 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300 border-b-2 border-transparent'}`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
          </li>
          <li className="mr-2">
            <button 
              className={`inline-block py-4 px-4 text-sm font-medium ${activeTab === 'themes' 
                ? 'text-blue-600 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300 border-b-2 border-transparent'}`}
              onClick={() => setActiveTab('themes')}
            >
              Themes
            </button>
          </li>
          <li className="mr-2">
            <button 
              className={`inline-block py-4 px-4 text-sm font-medium ${activeTab === 'collections' 
                ? 'text-blue-600 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300 border-b-2 border-transparent'}`}
              onClick={() => setActiveTab('collections')}
            >
              Collections
            </button>
          </li>
          <li className="mr-2">
            <button 
              className={`inline-block py-4 px-4 text-sm font-medium ${activeTab === 'pages' 
                ? 'text-blue-600 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300 border-b-2 border-transparent'}`}
              onClick={() => setActiveTab('pages')}
            >
              Pages
            </button>
          </li>
          <li>
            <button 
              className={`inline-block py-4 px-4 text-sm font-medium ${activeTab === 'settings' 
                ? 'text-blue-600 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300 border-b-2 border-transparent'}`}
              onClick={() => setActiveTab('settings')}
            >
              Settings
            </button>
          </li>
        </ul>
      </div>

      {/* Tab Content */}
      <div className="mb-8">
        {/* Overview Tab Content */}
        {activeTab === 'overview' && (
          <div>
            <div className="bg-white rounded-lg shadow">
              <div className="p-6">
                <h2 className="text-xl font-semibold mb-4">Store Health</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Left column */}
                  <div>
                    <h3 className="text-lg font-medium mb-3">Technical Status</h3>
                    <ul className="space-y-4">
                      <li className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2 mt-0.5" />
                        <div>
                          <p className="font-medium">SSL Certificate</p>
                          <p className="text-sm text-gray-600">Valid and secure</p>
                        </div>
                      </li>
                      <li className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2 mt-0.5" />
                        <div>
                          <p className="font-medium">Mobile Responsiveness</p>
                          <p className="text-sm text-gray-600">Fully responsive on all devices</p>
                        </div>
                      </li>
                      <li className="flex items-start">
                        <AlertTriangle className="h-5 w-5 text-yellow-500 mr-2 mt-0.5" />
                        <div>
                          <p className="font-medium">Image Optimization</p>
                          <p className="text-sm text-gray-600">12 images need optimization</p>
                        </div>
                      </li>
                      <li className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2 mt-0.5" />
                        <div>
                          <p className="font-medium">Checkout Process</p>
                          <p className="text-sm text-gray-600">Working correctly</p>
                        </div>
                      </li>
                    </ul>
                  </div>
                  
                  {/* Right column */}
                  <div>
                    <h3 className="text-lg font-medium mb-3">Content Status</h3>
                    <ul className="space-y-4">
                      <li className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2 mt-0.5" />
                        <div>
                          <p className="font-medium">Product Descriptions</p>
                          <p className="text-sm text-gray-600">All products have complete descriptions</p>
                        </div>
                      </li>
                      <li className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2 mt-0.5" />
                        <div>
                          <p className="font-medium">SEO Elements</p>
                          <p className="text-sm text-gray-600">Meta titles and descriptions are optimized</p>
                        </div>
                      </li>
                      <li className="flex items-start">
                        <AlertTriangle className="h-5 w-5 text-yellow-500 mr-2 mt-0.5" />
                        <div>
                          <p className="font-medium">Image Alt Tags</p>
                          <p className="text-sm text-gray-600">8 images missing alt tags</p>
                        </div>
                      </li>
                      <li className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2 mt-0.5" />
                        <div>
                          <p className="font-medium">Legal Pages</p>
                          <p className="text-sm text-gray-600">All required legal pages are present</p>
                        </div>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Recent Updates</h2>
                <div className="space-y-4">
                  {storeData?.recentUpdates?.map((update, index) => (
                    <div key={index} className="border-b border-gray-100 pb-3 last:border-0 last:pb-0">
                      <p className="font-medium">{update.title}</p>
                      <p className="text-sm text-gray-600 mt-1">{update.description}</p>
                      <p className="text-xs text-gray-500 mt-2">{new Date(update.date).toLocaleString()}</p>
                    </div>
                  ))}
                  {(!storeData?.recentUpdates || storeData?.recentUpdates.length === 0) && (
                    <p className="text-gray-500">No recent updates</p>
                  )}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Recommended Actions</h2>
                <ul className="space-y-3">
                  {storeData?.recommendedActions?.map((action, index) => (
                    <li key={index} className="flex items-start space-x-3 pb-3 border-b border-gray-100 last:border-0 last:pb-0">
                      <div className={`p-1.5 rounded-full ${action.priority === 'high' ? 'bg-red-100' : action.priority === 'medium' ? 'bg-yellow-100' : 'bg-blue-100'}`}>
                        <div className={`h-2 w-2 rounded-full ${action.priority === 'high' ? 'bg-red-500' : action.priority === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'}`}></div>
                      </div>
                      <div>
                        <p className="font-medium">{action.title}</p>
                        <p className="text-sm text-gray-600 mt-1">{action.description}</p>
                      </div>
                    </li>
                  ))}
                  {(!storeData?.recommendedActions || storeData?.recommendedActions.length === 0) && (
                    <p className="text-gray-500">No actions recommended at this time</p>
                  )}
                </ul>
              </div>
            </div>
          </div>
        )}
        
        {/* Themes Tab Content */}
        {activeTab === 'themes' && <ThemesTab themeData={themeData} />}
        
        {/* Collections Tab Content */}
        {activeTab === 'collections' && <CollectionsTab collectionsData={collectionsData} />}
        
        {/* Pages Tab Content */}
        {activeTab === 'pages' && <PagesTab pageData={pageData} />}
        
        {/* Settings Tab Content */}
        {activeTab === 'settings' && <SettingsTab storeData={storeData} />}
      </div>
    </div>
  );
};

export default WebsiteBuilder;
