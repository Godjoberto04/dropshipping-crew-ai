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

import { contentGeneratorApi } from '../services/api';
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

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch statistics and templates in parallel
        const [statsResponse, templatesResponse] = await Promise.all([
          contentGeneratorApi.getStatistics(),
          contentGeneratorApi.getTemplates()
        ]);
        
        setStatistics(statsResponse.data);
        setTemplates(templatesResponse.data);
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