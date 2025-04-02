import React, { useState, useEffect } from 'react';

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

const sizePixels = {
  small: 256,
  medium: 512,
  large: 1024,
  original: 2048 // We'll use this as a maximum size for "original"
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
  const [processedImageUrl, setProcessedImageUrl] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [isAutoProcessing, setIsAutoProcessing] = useState<boolean>(false);
  
  // Process the image when format or size changes
  useEffect(() => {
    // Reset the processed URL when selections change
    setProcessedImageUrl('');
  }, [selectedFormat, selectedSize]);

  // Preprocess the image when format/size selection changes
  useEffect(() => {
    // Auto-process the image when selections change to prepare it for preview/download
    let isMounted = true;
    const preprocessImage = async () => {
      // Don't start auto-processing if there's already a manual processing happening
      // or if we already have a processed URL for the current selections
      if (!processedImageUrl && !isProcessing && isMounted) {
        setIsAutoProcessing(true);
        try {
          console.log('Auto-processing image with format:', selectedFormat, 'size:', selectedSize);
          const url = await processImage(imageUrl, selectedFormat, selectedSize);
          if (isMounted) {
            console.log('Auto-processing complete');
            setProcessedImageUrl(url);
          }
        } catch (error) {
          console.error('Error preprocessing image:', error);
        } finally {
          if (isMounted) {
            setIsAutoProcessing(false);
          }
        }
      }
    };
    
    preprocessImage();
    
    // Cleanup function to handle component unmount
    return () => {
      isMounted = false;
    };
  }, [selectedFormat, selectedSize, imageUrl, processedImageUrl, isProcessing]);

  // Helper function to process image for preview
  const processImageForPreview = async () => {
    setIsProcessing(true);
    try {
      const url = await processImage(imageUrl, selectedFormat, selectedSize);
      setProcessedImageUrl(url);
      return url;
    } catch (error) {
      console.error('Error processing image:', error);
      return null;
    } finally {
      setIsProcessing(false);
    }
  };
  
  // Function to process the image according to format and size
  const processImage = async (
    url: string, 
    format: ExportFormat, 
    size: ExportSize
  ): Promise<string> => {
    return new Promise((resolve, reject) => {
      // Handle SVG format separately with server-side conversion
      if (format === 'svg') {
        // For SVG we need to use our backend conversion API
        handleSvgConversion(url, size)
          .then(resolve)
          .catch(error => {
            console.warn('SVG conversion failed, using PNG fallback:', error);
            // Fallback to PNG if SVG conversion fails
            processToPng(url, size)
              .then(resolve)
              .catch(reject);
          });
        return;
      }

      // For PNG and JPG, use canvas
      const img = new Image();
      img.crossOrigin = 'anonymous';  // Enable CORS if the image is from a different domain
      
      img.onload = () => {
        try {
          // Create a canvas to perform the conversion
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          
          if (!ctx) {
            reject(new Error('Could not get canvas context'));
            return;
          }
          
          // Set the canvas size based on the selected size
          const targetSize = sizePixels[size];
          
          // Calculate new dimensions while preserving aspect ratio
          let newWidth = img.width;
          let newHeight = img.height;
          
          // Only resize if we're not using original size or if original is larger than max
          if (size !== 'original' || Math.max(img.width, img.height) > targetSize) {
            const aspectRatio = img.width / img.height;
            
            if (img.width > img.height) {
              newWidth = targetSize;
              newHeight = targetSize / aspectRatio;
            } else {
              newHeight = targetSize;
              newWidth = targetSize * aspectRatio;
            }
          }
          
          canvas.width = newWidth;
          canvas.height = newHeight;
          
          // For JPG, fill with white background
          if (format === 'jpg') {
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
          }
          
          // Draw the image on the canvas (this handles the resizing)
          ctx.drawImage(img, 0, 0, newWidth, newHeight);
          
          // Convert canvas to the desired format
          let mimeType = 'image/png';
          if (format === 'jpg') mimeType = 'image/jpeg';
          
          // Convert the canvas to a data URL with the appropriate format
          const dataUrl = canvas.toDataURL(mimeType, 0.9);
          resolve(dataUrl);
        } catch (err) {
          reject(err);
        }
      };
      
      img.onerror = () => {
        reject(new Error('Failed to load image'));
      };
      
      img.src = url;
    });
  };

  // Helper function for PNG processing (used as fallback)
  const processToPng = async (url: string, size: ExportSize): Promise<string> => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      
      img.onload = () => {
        try {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          
          if (!ctx) {
            reject(new Error('Could not get canvas context'));
            return;
          }
          
          const targetSize = sizePixels[size];
          
          let newWidth = img.width;
          let newHeight = img.height;
          
          if (size !== 'original' || Math.max(img.width, img.height) > targetSize) {
            const aspectRatio = img.width / img.height;
            
            if (img.width > img.height) {
              newWidth = targetSize;
              newHeight = targetSize / aspectRatio;
            } else {
              newHeight = targetSize;
              newWidth = targetSize * aspectRatio;
            }
          }
          
          canvas.width = newWidth;
          canvas.height = newHeight;
          
          ctx.drawImage(img, 0, 0, newWidth, newHeight);
          
          const dataUrl = canvas.toDataURL('image/png', 0.9);
          resolve(dataUrl);
        } catch (err) {
          reject(err);
        }
      };
      
      img.onerror = () => {
        reject(new Error('Failed to load image'));
      };
      
      img.src = url;
    });
  };

  // Function to handle SVG conversion via backend API
  const handleSvgConversion = async (url: string, size: ExportSize): Promise<string> => {
    try {
      // First convert the image to a data URL if it's not already
      let imageData = url;
      if (!url.startsWith('data:')) {
        // Fetch the image and convert to data URL
        const response = await fetch(url);
        const blob = await response.blob();
        imageData = await new Promise<string>((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve(reader.result as string);
          reader.readAsDataURL(blob);
        });
      }
      
      console.log('Making SVG conversion request to backend...');
      
      // Prepare the request to the backend - use the correct API path
      // The server has the route at /api/svg/convert-to-svg
      const apiUrl = '/api/svg/convert-to-svg';
      
      console.log('Sending SVG conversion request to:', apiUrl);
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_data: imageData,
          max_size: sizePixels[size],
          color_mode: 'color', 
          hierarchical: true,
          filter_speckle_size: 4,
          corner_threshold: 60.0,
          length_threshold: 4.0,
          splice_threshold: 45.0, 
          path_precision: 8,
          color_quantization_steps: 16
        }),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('SVG conversion API response error:', response.status, errorText);
        throw new Error(`SVG conversion failed: ${response.status} - ${errorText}`);
      }
      
      const data = await response.json();
      console.log('SVG conversion response:', data);
      
      if (!data.success) {
        throw new Error(data.message || 'SVG conversion failed');
      }
      
      // Create a data URL from the SVG data - make sure we sanitize the SVG content
      const svgData = data.svg_data.trim();
      
      // Check if the SVG data is valid
      if (!svgData.startsWith('<?xml') && !svgData.startsWith('<svg')) {
        console.warn('Received invalid SVG data, falling back to original image');
        return url;
      }
      
      // For safer handling, create a Blob and use an Object URL instead of base64
      const blob = new Blob([svgData], { type: 'image/svg+xml' });
      const objectUrl = URL.createObjectURL(blob);
      console.log('Created SVG object URL:', objectUrl);
      
      return objectUrl;
    } catch (error) {
      console.error('Error in SVG conversion:', error);
      throw error;
    }
  };
  
  const handlePreview = async () => {
    try {
      if (!processedImageUrl) {
        // Don't proceed until we have a processed image
        const url = await processImageForPreview();
        if (!url) {
          // If processing failed, fall back to the original URL
          window.open(imageUrl, '_blank');
          return;
        }
      }
      
      // Check if the URL is an SVG object URL
      if (processedImageUrl.startsWith('blob:') && selectedFormat === 'svg') {
        // For SVG, we might need to fetch the content and create a proper viewable HTML
        const response = await fetch(processedImageUrl);
        const svgText = await response.text();
        
        // Create a simple HTML document that can display the SVG properly
        const htmlContent = `
          <!DOCTYPE html>
          <html>
            <head>
              <title>SVG Preview - ${conceptTitle}</title>
              <style>
                body { margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f0f0; }
                .svg-container { max-width: 90%; max-height: 90%; background-color: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
              </style>
            </head>
            <body>
              <div class="svg-container">
                ${svgText}
              </div>
            </body>
          </html>
        `;
        
        // Create a blob URL for the HTML content
        const blob = new Blob([htmlContent], { type: 'text/html' });
        const htmlUrl = URL.createObjectURL(blob);
        
        // Open in a new tab
        window.open(htmlUrl, '_blank');
      } else {
        // For other formats, just open the processed image
        window.open(processedImageUrl, '_blank');
      }
    } catch (error) {
      console.error('Error previewing image:', error);
      // Fall back to original URL
      window.open(imageUrl, '_blank');
    }
  };
  
  const handleDownload = async () => {
    try {
      if (onDownload) {
        onDownload(selectedFormat, selectedSize);
        return;
      }
      
      // Set the file extension to use (SVG is now properly implemented)
      const fileExtension = selectedFormat; // Now we can use the format directly as extension
      
      if (!processedImageUrl) {
        // Start processing if not already done
        setIsProcessing(true);
        try {
          const url = await processImage(imageUrl, selectedFormat, selectedSize);
          setProcessedImageUrl(url);
          
          // Now proceed with the download using the processed URL
          await downloadProcessedImage(url, fileExtension);
        } catch (error) {
          console.error('Error processing image for download:', error);
          // Fallback to the original URL if processing failed
          await downloadProcessedImage(imageUrl, fileExtension);
        } finally {
          setIsProcessing(false);
        }
      } else {
        // Use the already processed image URL
        await downloadProcessedImage(processedImageUrl, fileExtension);
      }
    } catch (error) {
      console.error('Error during download:', error);
      // Show an error toast or notification here
    }
  };
  
  // Helper function to safely download the processed image
  const downloadProcessedImage = async (url: string, fileExtension: string) => {
    const filename = `${conceptTitle}${variationName ? `-${variationName}` : ''}.${fileExtension}`;
    
    try {
      // Handle SVG object URLs specially
      if (url.startsWith('blob:') && fileExtension === 'svg') {
        const response = await fetch(url);
        const svgText = await response.text();
        
        // Create a download for the raw SVG content
        const blob = new Blob([svgText], { type: 'image/svg+xml' });
        const downloadUrl = URL.createObjectURL(blob);
        
        // Create a link and trigger the download
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        // Add to body to ensure it works in all browsers
        document.body.appendChild(a);
        a.click();
        // Clean up
        setTimeout(() => {
          document.body.removeChild(a);
          URL.revokeObjectURL(downloadUrl);
        }, 100);
      } else if (url.startsWith('data:')) {
        // For data URLs (common with PNG/JPG formats)
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        // Clean up
        setTimeout(() => {
          document.body.removeChild(a);
        }, 100);
      } else {
        // For regular URLs, fetch first to ensure proper download
        const response = await fetch(url);
        const blob = await response.blob();
        const objectUrl = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = objectUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        // Clean up
        setTimeout(() => {
          document.body.removeChild(a);
          URL.revokeObjectURL(objectUrl);
        }, 100);
      }
      
      console.log(`Downloaded ${fileExtension.toUpperCase()} file: ${filename}`);
    } catch (error) {
      console.error('Error downloading the image:', error);
      throw error;
    }
  };

  // Format info for tooltips
  const formatInfo = {
    png: { title: 'Transparent Background', tag: 'Recommended', desc: 'Best for web, digital use' },
    svg: { 
      title: 'Vector Format', 
      tag: 'Server-Processed', 
      desc: 'True SVG conversion via server-side processing' 
    },
    jpg: { title: 'With Background', tag: 'Smaller Size', desc: 'Best for photos, email' }
  };
  
  return (
    <div className="flex flex-col">
      <div className="space-y-4">
        {/* Format selection - keeping this on its own line for better readability */}
        <div>
          <h4 className="text-sm font-semibold text-indigo-700 mb-3">Format</h4>
          <div className="flex gap-3">
            {Object.entries(formatInfo).map(([format, info]) => (
              <button 
                key={format}
                className={`flex-1 border rounded-lg p-3 hover:shadow-md transition-all cursor-pointer text-center
                  ${selectedFormat === format ? 'border-indigo-400 bg-indigo-50 shadow-sm' : 'border-indigo-200 hover:border-indigo-300'}
                  ${(isProcessing || isAutoProcessing) ? 'opacity-75 cursor-wait' : ''}`}
                onClick={() => setSelectedFormat(format as ExportFormat)}
                title={info.desc}
                disabled={isProcessing || isAutoProcessing}
              >
                <div className="text-indigo-600 font-bold text-md flex justify-center">.{format.toUpperCase()}</div>
                <div className="text-xs text-gray-500 mt-2">{info.title}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Size selection */}
        <div>
          <h4 className="text-sm font-semibold text-indigo-700 mb-3">Size</h4>
          <div className="grid grid-cols-4 gap-3">
            {Object.entries(sizeMap).map(([size, label]) => (
              <button 
                key={size}
                className={`border rounded-lg p-3 hover:shadow-md transition-all cursor-pointer text-center
                  ${selectedSize === size ? 'border-indigo-400 bg-indigo-50 shadow-sm' : 'border-indigo-200 hover:border-indigo-300'}
                  ${(isProcessing || isAutoProcessing) ? 'opacity-75 cursor-wait' : ''}`}
                onClick={() => setSelectedSize(size as ExportSize)}
                disabled={isProcessing || isAutoProcessing}
              >
                <div className={`font-medium flex justify-center ${selectedSize === size ? 'text-indigo-700' : 'text-indigo-600'}`}>
                  {size.charAt(0).toUpperCase() + size.slice(1)}
                </div>
                <div className="text-xs text-gray-500 mt-2">{label}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
      
      {/* Status indicator */}
      <div className="mt-4">
        {isAutoProcessing && (
          <div className="text-xs text-indigo-600 flex items-center">
            <svg className="animate-spin -ml-1 mr-1 h-3 w-3 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Preparing preview with selected options...
          </div>
        )}
        {!isAutoProcessing && processedImageUrl && (
          <div className="text-xs text-green-600 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            Ready to preview and download
          </div>
        )}
      </div>
      
      {/* Download controls */}
      <div className="mt-5 pt-5 border-t border-indigo-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div className="text-sm text-gray-600 mb-3 sm:mb-0">
          <span className="font-medium">Selected:</span> {selectedFormat.toUpperCase()}, {sizeMap[selectedSize]}
        </div>
        
        <div className="flex gap-3 w-full sm:w-auto justify-end">
          <button 
            className="px-4 py-2 min-w-[100px] border border-indigo-200 text-indigo-600 font-medium rounded-lg hover:bg-indigo-50 transition-colors flex justify-center items-center"
            onClick={handlePreview}
            disabled={isProcessing || isAutoProcessing}
          >
            {(isProcessing || isAutoProcessing) ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {isAutoProcessing ? 'Preparing' : 'Processing'}
              </span>
            ) : (
              <span>Preview</span>
            )}
          </button>
          <button 
            className="px-4 py-2 min-w-[120px] bg-gradient-to-r from-indigo-600 to-indigo-400 text-white font-medium rounded-lg shadow-sm hover:shadow-md transition-all flex justify-center items-center"
            onClick={handleDownload}
            disabled={isProcessing || isAutoProcessing}
          >
            {(isProcessing || isAutoProcessing) ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {isAutoProcessing ? 'Preparing' : 'Processing'}
              </span>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
                <span>Download</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}; 