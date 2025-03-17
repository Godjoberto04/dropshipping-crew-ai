import React from 'react';
import { CheckCircle, AlertTriangle, Edit, Eye } from 'lucide-react';

// Themes Tab Component
export const ThemesTab = ({ themeData }) => {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <h2 className="text-xl font-semibold mb-6">Theme Management</h2>
        
        {/* Current Active Theme */}
        <div className="mb-8">
          <h3 className="text-lg font-medium mb-4 border-b pb-2">Active Theme</h3>
          <div className="flex flex-col md:flex-row md:items-start gap-6">
            {themeData?.previewImage && (
              <img 
                src={themeData.previewImage} 
                alt="Active theme preview" 
                className="w-full md:w-1/3 rounded-lg shadow-sm border border-gray-200 object-cover"
              />
            )}
            <div className="flex-1">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="text-xl font-medium">{themeData?.name || 'Default Theme'}</h4>
                  <p className="text-sm text-gray-600 mt-1">Version: {themeData?.version || '1.0'}</p>
                </div>
                <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded">Active</span>
              </div>
              
              <div className="mt-4">
                <p className="text-gray-700">{themeData?.description || 'No description available'}</p>
              </div>
              
              <div className="mt-6 space-y-3">
                <h5 className="font-medium">Theme Features:</h5>
                <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                  {themeData?.features?.map((feature, index) => (
                    <li key={index} className="flex items-center">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                      <span>{feature}</span>
                    </li>
                  ))}
                  {(!themeData?.features || themeData?.features.length === 0) && (
                    <li className="text-gray-500">No features listed</li>
                  )}
                </ul>
              </div>
              
              <div className="mt-6 flex flex-wrap gap-3">
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Customize Theme
                </button>
                <button className="px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 transition-colors">
                  Edit Code
                </button>
                <button className="px-4 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors">
                  Preview
                </button>
              </div>
            </div>
          </div>
        </div>
        
        {/* Available Themes */}
        <div>
          <h3 className="text-lg font-medium mb-4 border-b pb-2">Available Themes</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {themeData?.availableThemes?.map((theme, index) => (
              <div key={index} className="border rounded-lg overflow-hidden shadow-sm">
                {theme.previewImage && (
                  <img 
                    src={theme.previewImage} 
                    alt={`${theme.name} preview`} 
                    className="w-full h-48 object-cover"
                  />
                )}
                <div className="p-4">
                  <h4 className="font-medium">{theme.name}</h4>
                  <p className="text-sm text-gray-600 mt-1">Version: {theme.version}</p>
                  <p className="text-sm text-gray-700 mt-2 line-clamp-2">{theme.description}</p>
                  <div className="mt-4 flex justify-between">
                    <button className="text-sm text-blue-600 hover:text-blue-800">Preview</button>
                    <button className="text-sm bg-blue-50 text-blue-700 px-3 py-1 rounded hover:bg-blue-100">
                      Activate
                    </button>
                  </div>
                </div>
              </div>
            ))}
            {(!themeData?.availableThemes || themeData?.availableThemes.length === 0) && (
              <p className="text-gray-500 col-span-full">No additional themes available</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Collections Tab Component
export const CollectionsTab = ({ collectionsData }) => {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Collections</h2>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center">
            <span className="mr-2">+</span> Add Collection
          </button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Collection Name
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Products
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Updated
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {collectionsData?.map((collection, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {collection.image && (
                        <img className="h-10 w-10 rounded-full mr-3 object-cover" src={collection.image} alt="" />
                      )}
                      <div>
                        <div className="text-sm font-medium text-gray-900">{collection.name}</div>
                        <div className="text-sm text-gray-500">{collection.handle}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{collection.type}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{collection.productCount}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      collection.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {collection.active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(collection.updatedAt).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button className="text-blue-600 hover:text-blue-900 mr-3">Edit</button>
                    <button className="text-gray-600 hover:text-gray-900">View</button>
                  </td>
                </tr>
              ))}
              {(!collectionsData || collectionsData.length === 0) && (
                <tr>
                  <td colSpan="6" className="px-6 py-4 text-center text-sm text-gray-500">
                    No collections found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Pages Tab Component
export const PagesTab = ({ pageData }) => {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Pages</h2>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center">
            <span className="mr-2">+</span> Add Page
          </button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Page Title
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  URL
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Visibility
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Updated
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {pageData?.map((page, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{page.title}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{page.handle}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      page.visible ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {page.visible ? 'Visible' : 'Hidden'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(page.updatedAt).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button className="text-blue-600 hover:text-blue-900 mr-3">Edit</button>
                    <button className="text-green-600 hover:text-green-900 mr-3">View</button>
                    <button className="text-red-600 hover:text-red-900">Delete</button>
                  </td>
                </tr>
              ))}
              {(!pageData || pageData.length === 0) && (
                <tr>
                  <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500">
                    No pages found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Settings Tab Component
export const SettingsTab = ({ storeData }) => {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <h2 className="text-xl font-semibold mb-6">Store Settings</h2>
        
        <div className="mb-8">
          <h3 className="text-lg font-medium mb-4 border-b pb-2">General Settings</h3>
          <form className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Store Name</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  defaultValue={storeData?.name}
                  placeholder="Your store name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Contact Email</label>
                <input
                  type="email"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  defaultValue={storeData?.contactEmail}
                  placeholder="contact@yourdomain.com"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Store Currency</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  defaultValue={storeData?.currency}
                >
                  <option value="USD">US Dollar (USD)</option>
                  <option value="EUR">Euro (EUR)</option>
                  <option value="GBP">British Pound (GBP)</option>
                  <option value="CAD">Canadian Dollar (CAD)</option>
                  <option value="AUD">Australian Dollar (AUD)</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Time Zone</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  defaultValue={storeData?.timeZone}
                >
                  <option value="UTC">UTC</option>
                  <option value="America/New_York">Eastern Time (ET)</option>
                  <option value="America/Chicago">Central Time (CT)</option>
                  <option value="America/Denver">Mountain Time (MT)</option>
                  <option value="America/Los_Angeles">Pacific Time (PT)</option>
                  <option value="Europe/London">London</option>
                  <option value="Europe/Paris">Paris</option>
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Store Description</label>
              <textarea
                rows="3"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                defaultValue={storeData?.description}
                placeholder="A short description of your store"
              ></textarea>
            </div>
            
            <div className="pt-3">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 transition-colors"
              >
                Save General Settings
              </button>
            </div>
          </form>
        </div>
        
        <div className="mb-8">
          <h3 className="text-lg font-medium mb-4 border-b pb-2">SEO Settings</h3>
          <form className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Homepage Title</label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                defaultValue={storeData?.seo?.title}
                placeholder="Homepage title for search engines"
              />
              <p className="text-sm text-gray-500 mt-1">Recommended length: 50-60 characters</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Homepage Meta Description</label>
              <textarea
                rows="3"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                defaultValue={storeData?.seo?.description}
                placeholder="A brief description of your store for search engines"
              ></textarea>
              <p className="text-sm text-gray-500 mt-1">Recommended length: 150-160 characters</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">URL Structure</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                defaultValue={storeData?.seo?.urlStructure}
              >
                <option value="product-name">Product Name (e.g., blue-t-shirt)</option>
                <option value="product-id-name">Product ID + Name (e.g., 123-blue-t-shirt)</option>
                <option value="product-category-name">Category + Name (e.g., clothing-blue-t-shirt)</option>
              </select>
            </div>
            
            <div className="pt-3">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 transition-colors"
              >
                Save SEO Settings
              </button>
            </div>
          </form>
        </div>
        
        <div>
          <h3 className="text-lg font-medium mb-4 border-b pb-2">Social Media Integration</h3>
          <form className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Facebook Page URL</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  defaultValue={storeData?.social?.facebook}
                  placeholder="https://facebook.com/your-page"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Instagram Handle</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  defaultValue={storeData?.social?.instagram}
                  placeholder="@yourhandle"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Twitter Handle</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  defaultValue={storeData?.social?.twitter}
                  placeholder="@yourhandle"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Pinterest Username</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  defaultValue={storeData?.social?.pinterest}
                  placeholder="yourusername"
                />
              </div>
            </div>
            
            <div className="pt-3">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 transition-colors"
              >
                Save Social Media Settings
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
