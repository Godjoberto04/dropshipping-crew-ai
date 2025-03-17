import React from 'react';
import { Copy } from 'lucide-react';

const GeneratedContentPreview = ({ content, onCopy }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="flex justify-between items-center mb-4 pb-2 border-b border-gray-100">
        <h3 className="font-medium text-lg text-gray-800">Generated Content</h3>
        <button 
          className="text-gray-500 hover:text-gray-700 flex items-center text-sm"
          onClick={onCopy}
        >
          <Copy size={16} className="mr-1" />
          Copy to clipboard
        </button>
      </div>
      <div className="prose max-w-none prose-sm lg:prose-base">
        <div dangerouslySetInnerHTML={{ __html: content }} />
      </div>
    </div>
  );
};

export default GeneratedContentPreview;