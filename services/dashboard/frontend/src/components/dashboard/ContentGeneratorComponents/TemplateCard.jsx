import React from 'react';
import { Tag, BookOpen, FileText } from 'lucide-react';

const TemplateCard = ({ template, onSelect }) => {
  return (
    <div 
      className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => onSelect(template)}
    >
      <div className="flex items-center mb-3">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
          template.type === 'product' ? 'bg-blue-100 text-blue-600' : 
          template.type === 'category' ? 'bg-green-100 text-green-600' : 
          'bg-purple-100 text-purple-600'
        }`}>
          {template.type === 'product' ? <Tag size={18} /> : 
           template.type === 'category' ? <BookOpen size={18} /> : 
           <FileText size={18} />}
        </div>
        <div className="ml-3">
          <h3 className="font-medium text-gray-800">{template.name}</h3>
          <p className="text-xs text-gray-500">{template.type} • {template.language}</p>
        </div>
      </div>
      <p className="text-sm text-gray-600 line-clamp-2">{template.description}</p>
      <div className="mt-3 flex items-center">
        <span className="text-xs px-2 py-1 bg-gray-100 rounded-full text-gray-600 mr-2">{template.tone}</span>
        {template.optimizedSEO && 
          <span className="text-xs px-2 py-1 bg-green-100 rounded-full text-green-600">SEO</span>
        }
      </div>
    </div>
  );
};

export default TemplateCard;