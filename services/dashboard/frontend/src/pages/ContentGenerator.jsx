import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { 
  FileText, 
  Settings, 
  Edit, 
  BarChart2, 
  RefreshCw, 
  Tag, 
  Search, 
  BookOpen,
  Check,
  AlertTriangle,
  HelpCircle,
  Copy,
  PlusCircle
} from 'lucide-react';

import { contentGeneratorApi, getContentGeneratorData } from '../services/api';
import TemplateCard from '../components/dashboard/ContentGeneratorComponents/TemplateCard';
import GeneratedContentPreview from '../components/dashboard/ContentGeneratorComponents/GeneratedContentPreview';
import ContentStatisticsCard from '../components/dashboard/ContentGeneratorComponents/ContentStatisticsCard';
import SEOMetadataPanel from '../components/dashboard/ContentGeneratorComponents/SEOMetadataPanel';

const ContentGenerator = () => {
  // State management
  const [activeTab, setActiveTab] = useState('generator');
  const [statistics, setStatistics] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [formData, setFormData] = useState({
    productName: '',
    productFeatures: '',
    price: '',
    brand: '',
    tone: 'persuasive',
    language: 'fr',
    niche: 'general',
    keywords: ''
  });
  const [contentHistory, setContentHistory] = useState([]);

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch statistics and templates in parallel
        const [statsResponse, templatesResponse, historyResponse] = await Promise.all([
          contentGeneratorApi.getStatistics(),
          contentGeneratorApi.getTemplates(),
          contentGeneratorApi.getContentHistory()
        ]);
        
        setStatistics(statsResponse.data);
        setTemplates(templatesResponse.data);
        setContentHistory(historyResponse?.data || []);
      } catch (error) {
        console.error('Error fetching content generator data:', error);
        toast.error('Failed to load content generator data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  // Handle template selection
  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
    toast.success(`Template selected: ${template.name}`);
    
    // Update form defaults based on template
    if (template.defaultTone) {
      setFormData(prev => ({ ...prev, tone: template.defaultTone }));
    }
    
    if (template.defaultNiche) {
      setFormData(prev => ({ ...prev, niche: template.defaultNiche }));
    }
    
    if (template.language) {
      setFormData(prev => ({ ...prev, language: template.language }));
    }
    
    // Switch back to generator tab
    setActiveTab('generator');
  };

  // Handle content generation
  const handleGenerateContent = async () => {
    // Validate form
    if (!formData.productName.trim()) {
      toast.error('Product name is required');
      return;
    }
    
    try {
      setGenerating(true);
      toast.loading('Generating content...', { id: 'generating' });

      // Parse features to array
      const features = formData.productFeatures
        .split('\n')
        .map(feature => feature.trim())
        .filter(feature => feature.length > 0);

      // Parse keywords to array
      const keywords = formData.keywords
        .split(',')
        .map(keyword => keyword.trim())
        .filter(keyword => keyword.length > 0);

      const params = {
        action: 'generate_product_description',
        product_data: {
          name: formData.productName,
          features: features,
          price: formData.price,
          brand: formData.brand
        },
        tone: formData.tone,
        language: formData.language,
        niche: formData.niche,
        template_key: selectedTemplate ? selectedTemplate.id : null,
        seo_optimize: true,
        keywords: keywords
      };

      const response = await contentGeneratorApi.generateContent(params);
      const result = response.data;
      
      // Convert markdown to HTML for display
      const markdownToHtml = (markdown) => {
        if (!markdown) return '';
        
        return markdown
          .replace(/## (.*)/g, '<h2>$1</h2>')
          .replace(/### (.*)/g, '<h3>$1</h3>')
          .replace(/\n\* (.*)/g, '<li>$1</li>')
          .replace(/\n\n/g, '</p><p>')
          .replace(/\*\*(.*)\*\*/g, '<strong>$1</strong>');
      };
      
      setGeneratedContent({
        html: markdownToHtml(result.description),
        markdown: result.description,
        seo: result.seo_metadata
      });
      
      toast.dismiss('generating');
      toast.success('Content generated successfully');
    } catch (error) {
      console.error('Error generating content:', error);
      toast.dismiss('generating');
      toast.error('Failed to generate content: ' + (error.message || 'Unknown error'));
    } finally {
      setGenerating(false);
    }
  };

  // Handle content copy
  const handleCopyContent = () => {
    if (generatedContent) {
      navigator.clipboard.writeText(generatedContent.markdown)
        .then(() => {
          toast.success('Content copied to clipboard');
        })
        .catch(() => {
          toast.error('Failed to copy content');
        });
    }
  };

  // Render loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-full w-full">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          <p className="text-gray-500">Loading content generator data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container px-6 mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-800">Content Generator</h1>
          <p className="text-gray-500">Generate optimized content for your e-commerce store</p>
        </div>
        <div>
          <button
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 transition-colors"
            onClick={() => setActiveTab(activeTab === 'templates' ? 'generator' : 'templates')}
          >
            {activeTab === 'templates' ? (
              <>
                <Edit size={18} className="mr-2" />
                Back to Generator
              </>
            ) : (
              <>
                <FileText size={18} className="mr-2" />
                Browse Templates
              </>
            )}
          </button>
        </div>
      </div>

      {/* Statistics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <ContentStatisticsCard
          icon={<FileText className="h-6 w-6 text-blue-600" />}
          title="Total Content"
          value={statistics?.totalGenerated || 0}
          description="Items generated"
        />

        <ContentStatisticsCard
          icon={<Tag className="h-6 w-6 text-green-600" />}
          title="Product Descriptions"
          value={statistics?.productDescriptions || 0}
          description="Descriptions created"
        />

        <ContentStatisticsCard
          icon={<Edit className="h-6 w-6 text-purple-600" />}
          title="SEO Optimizations"
          value={statistics?.seoOptimizations || 0}
          description="Content pieces improved"
        />

        <ContentStatisticsCard
          icon={<BarChart2 className="h-6 w-6 text-indigo-600" />}
          title="Avg. Quality Score"
          value={`${statistics?.avgQualityScore || 0}%`}
          description="Based on SEO metrics"
        />
      </div>

      {/* Tabs for Content Generator */}
      <div className="border-b border-gray-200 mb-6">
        <ul className="flex flex-wrap -mb-px">
          <li className="mr-2">
            <button 
              className={`inline-block py-4 px-4 text-sm font-medium ${activeTab === 'generator' 
                ? 'text-blue-600 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300 border-b-2 border-transparent'}`}
              onClick={() => setActiveTab('generator')}
            >
              Generator
            </button>
          </li>
          <li className="mr-2">
            <button 
              className={`inline-block py-4 px-4 text-sm font-medium ${activeTab === 'templates' 
                ? 'text-blue-600 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300 border-b-2 border-transparent'}`}
              onClick={() => setActiveTab('templates')}
            >
              Templates
            </button>
          </li>
          <li className="mr-2">
            <button 
              className={`inline-block py-4 px-4 text-sm font-medium ${activeTab === 'history' 
                ? 'text-blue-600 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300 border-b-2 border-transparent'}`}
              onClick={() => setActiveTab('history')}
            >
              History
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
        {/* Generator Tab Content */}
        {activeTab === 'generator' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Generator Form */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4">Generate Content</h2>
                
                {/* Template Selection */}
                <div className="mb-5">
                  <div className="flex justify-between items-center mb-2">
                    <label className="block text-sm font-medium text-gray-700">Selected Template</label>
                    <button 
                      className="text-xs text-blue-600 hover:text-blue-800"
                      onClick={() => setActiveTab('templates')}
                    >
                      Change
                    </button>
                  </div>
                  
                  {selectedTemplate ? (
                    <div className="bg-gray-50 p-3 rounded-md">
                      <div className="flex items-center">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          selectedTemplate.type === 'product' ? 'bg-blue-100 text-blue-600' : 
                          selectedTemplate.type === 'category' ? 'bg-green-100 text-green-600' : 
                          'bg-purple-100 text-purple-600'
                        }`}>
                          {selectedTemplate.type === 'product' ? <Tag size={14} /> : 
                           selectedTemplate.type === 'category' ? <BookOpen size={14} /> : 
                           <FileText size={14} />}
                        </div>
                        <div className="ml-3">
                          <h3 className="font-medium text-sm">{selectedTemplate.name}</h3>
                          <p className="text-xs text-gray-500">{selectedTemplate.type} • {selectedTemplate.language}</p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-gray-50 p-3 rounded-md text-center">
                      <p className="text-sm text-gray-500">No template selected</p>
                      <button 
                        className="mt-2 text-sm text-blue-600 hover:text-blue-800 flex items-center justify-center mx-auto"
                        onClick={() => setActiveTab('templates')}
                      >
                        <PlusCircle size={14} className="mr-1" />
                        Select Template
                      </button>
                    </div>
                  )}
                </div>

                {/* Product Info */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Product Name *
                  </label>
                  <input
                    type="text"
                    name="productName"
                    value={formData.productName}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., Professional Wireless Headphones"
                    required
                  />
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Product Features (one per line)
                  </label>
                  <textarea
                    name="productFeatures"
                    value={formData.productFeatures}
                    onChange={handleInputChange}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., 40-hour battery life&#10;Active noise cancellation&#10;Bluetooth 5.0 connectivity"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Price
                    </label>
                    <input
                      type="text"
                      name="price"
                      value={formData.price}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., 99.99"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Brand
                    </label>
                    <input
                      type="text"
                      name="brand"
                      value={formData.brand}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., TechSound"
                    />
                  </div>
                </div>