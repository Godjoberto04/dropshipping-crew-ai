import React from 'react';
import { Search, Tag } from 'lucide-react';

const SEOMetadataPanel = ({ metadata }) => {
  if (!metadata) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="flex items-center mb-4 pb-2 border-b border-gray-100">
        <Search className="h-5 w-5 text-blue-500 mr-2" />
        <h3 className="font-medium text-lg text-gray-800">SEO Metadata</h3>
      </div>
      
      <div className="space-y-4">
        {metadata.meta_description && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Meta Description</h4>
            <p className="text-sm p-3 bg-gray-50 rounded border border-gray-200">
              {metadata.meta_description}
            </p>
          </div>
        )}
        
        {metadata.title_tag && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Title Tag</h4>
            <p className="text-sm p-3 bg-gray-50 rounded border border-gray-200">
              {metadata.title_tag}
            </p>
          </div>
        )}
        
        {metadata.keywords && metadata.keywords.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Keywords</h4>
            <div className="flex flex-wrap gap-2">
              {metadata.keywords.map((keyword, index) => (
                <span 
                  key={index}
                  className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  <Tag className="h-3 w-3 mr-1" />
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SEOMetadataPanel;