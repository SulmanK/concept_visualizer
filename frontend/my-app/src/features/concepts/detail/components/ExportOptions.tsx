import React, { useState } from 'react';

export interface ExportOptionsProps {
  /**
   * URL of the image to export
   */
  imageUrl: string;
  
  /**
   * Title/name of the concept
   */
  conceptTitle: string;
  
  /**
   * Variation name
   */
  variationName?: string;
  
  /**
   * Callback when the download button is clicked
   */
  onDownload?: (format: string, size: string) => void;
}

type ExportFormat = 'png' | 'svg' | 'jpg';
type ExportSize = 'small' | 'medium' | 'large' | 'original';

const sizeMap = {
  small: '256 x 256 px',
  medium: '512 x 512 px',
  large: '1024 x 1024 px',
  original: 'Max Quality'
};

/**
 * Component that allows users to export a concept in different formats and sizes
 */
export const ExportOptions: React.FC<ExportOptionsProps> = ({
  imageUrl,
  conceptTitle,
  variationName,
  onDownload
}) => {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('png');
  const [selectedSize, setSelectedSize] = useState<ExportSize>('medium');
  
  const handleDownload = () => {
    if (onDownload) {
      onDownload(selectedFormat, selectedSize);
    } else {
      // Default download behavior if no callback provided
      const a = document.createElement('a');
      a.href = imageUrl;
      a.download = `${conceptTitle}${variationName ? `-${variationName}` : ''}.${selectedFormat}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  // Format info for tooltips
  const formatInfo = {
    png: { title: 'Transparent Background', tag: 'Recommended', desc: 'Best for web, digital use' },
    svg: { title: 'Vector Format', tag: 'Scalable', desc: 'Best for printing, scaling' },
    jpg: { title: 'With Background', tag: 'Smaller Size', desc: 'Best for photos, email' }
  };
  
  return (
    <div className="flex flex-col">
      <div className="space-y-4">
        {/* Format selection - keeping this on its own line for better readability */}
        <div>
          <h4 className="text-sm font-semibold text-indigo-700 mb-2">Format</h4>
          <div className="flex gap-3">
            {Object.entries(formatInfo).map(([format, info]) => (
              <button 
                key={format}
                className={`flex-1 border rounded-lg p-3 hover:shadow-md transition-all cursor-pointer text-center
                  ${selectedFormat === format ? 'border-indigo-400 bg-indigo-50 shadow-sm' : 'border-indigo-200 hover:border-indigo-300'}`}
                onClick={() => setSelectedFormat(format as ExportFormat)}
                title={info.desc}
              >
                <div className="text-indigo-600 font-bold text-md">.{format.toUpperCase()}</div>
                <div className="text-xs text-gray-500 mt-1">{info.title}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Size selection */}
        <div>
          <h4 className="text-sm font-semibold text-indigo-700 mb-2">Size</h4>
          <div className="grid grid-cols-4 gap-3">
            {Object.entries(sizeMap).map(([size, label]) => (
              <button 
                key={size}
                className={`border rounded-lg p-2 hover:shadow-md transition-all cursor-pointer text-center
                  ${selectedSize === size ? 'border-indigo-400 bg-indigo-50 shadow-sm' : 'border-indigo-200 hover:border-indigo-300'}`}
                onClick={() => setSelectedSize(size as ExportSize)}
              >
                <div className={`font-medium ${selectedSize === size ? 'text-indigo-700' : 'text-indigo-600'}`}>
                  {size.charAt(0).toUpperCase() + size.slice(1)}
                </div>
                <div className="text-xs text-gray-500">{label}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
      
      {/* Download controls */}
      <div className="mt-5 pt-5 border-t border-indigo-100 flex flex-wrap justify-between items-center gap-3">
        <div className="text-sm text-gray-600">
          <span className="font-medium">Selected:</span> {selectedFormat.toUpperCase()}, {sizeMap[selectedSize]}
        </div>
        
        <div className="flex gap-3">
          <button 
            className="px-4 py-2 border border-indigo-200 text-indigo-600 font-medium rounded-lg hover:bg-indigo-50 transition-colors"
            onClick={() => window.open(imageUrl, '_blank')}
          >
            Preview
          </button>
          <button 
            className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-indigo-400 text-white font-medium rounded-lg shadow-sm hover:shadow-md transition-all flex items-center"
            onClick={handleDownload}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            Download
          </button>
        </div>
      </div>
    </div>
  );
}; 