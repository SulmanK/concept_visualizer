import React, { useState, useEffect, useCallback } from 'react';
import { ErrorMessage } from '../../../../components/ui';

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
  const [error, setError] = useState<{ message: string; type: string } | null>(null);
  
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

  // Clear error on format or size change
  useEffect(() => {
    setError(null);
  }, [selectedFormat, selectedSize]);

  const processImageForPreview = async () => {
    try {
      // Clear any previous errors
      setError(null);
      
      setIsAutoProcessing(true);
      const result = await processImage(imageUrl, selectedFormat, selectedSize);
      setProcessedImageUrl(result);
      setIsAutoProcessing(false);
      return result;
    } catch (error) {
      console.error('Error processing image for preview:', error);
      setIsAutoProcessing(false);
      
      // Set an appropriate error message
      if (error instanceof Error) {
        // Check for rate limit errors
        if (error.name === 'RateLimitError' || error.message.includes('rate limit')) {
          setError({
            message: 'SVG conversion limit reached. Please try again later or choose a different format.',
            type: 'rateLimit'
          });
        } else {
          setError({
            message: `Failed to process image: ${error.message}`,
            type: 'generic'
          });
        }
      } else {
        setError({
          message: 'An unexpected error occurred',
          type: 'generic'
        });
      }
      
      return null;
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
        // Handle rate limit errors (HTTP 429)
        if (response.status === 429) {
          // Try to parse the rate limit error details
          const errorData = await response.json().catch(() => ({}));
          
          // Get rate limit info from response if available
          let errorMessage = 'SVG conversion rate limit exceeded. Please try again later.';
          let rateLimitDetails = {
            limit: 20,
            current: 20,
            period: 'hour',
            resetAfterSeconds: 3600
          };
          
          if (errorData && errorData.detail) {
            // Extract rate limit details if available
            if (typeof errorData.detail === 'object') {
              const detail = errorData.detail;
              rateLimitDetails = {
                limit: detail.limit || 20,
                current: detail.current || 0,
                period: detail.period || 'hour',
                resetAfterSeconds: detail.reset_after_seconds || 3600
              };
              errorMessage = detail.message || errorMessage;
            } else {
              errorMessage = errorData.detail;
            }
          }
          
          // Set error in component state instead of creating dynamic component
          setError({
            message: `SVG conversion limit reached (${rateLimitDetails.current}/${rateLimitDetails.limit}). Please try again later or select a different format.`,
            type: 'rateLimit'
          });
          
          // Create a better error with rate limit info for logging
          const rateLimitError = new Error(errorMessage);
          Object.assign(rateLimitError, {
            status: 429,
            rateLimitInfo: rateLimitDetails,
            name: 'RateLimitError'
          });
          
          // No longer automatically switching to PNG format
          // Just throw the error and let the user decide what to do
          
          throw rateLimitError;
        }
        
        const errorText = await response.text();
        console.error('SVG conversion API response error:', response.status, errorText);
        
        // Set component error state
        setError({
          message: `SVG conversion failed (HTTP ${response.status}). Please try a different format.`,
          type: 'server'
        });
        
        throw new Error(`SVG conversion failed: ${response.status} - ${errorText}`);
      }
      
      const data = await response.json();
      console.log('SVG conversion response:', data);
      
      if (!data.success) {
        setError({
          message: data.message || 'SVG conversion failed. Please try a different format.',
          type: 'server'
        });
        throw new Error(data.message || 'SVG conversion failed');
      }
      
      // Create a data URL from the SVG data - make sure we sanitize the SVG content
      const svgData = data.svg_data.trim();
      
      // Check if the SVG data is valid
      if (!svgData.startsWith('<?xml') && !svgData.startsWith('<svg')) {
        console.warn('Received invalid SVG data, falling back to original image');
        setError({
          message: 'Received invalid SVG data. Please try a different format.',
          type: 'server'
        });
        return url;
      }
      
      // For safer handling, create a Blob and use an Object URL instead of base64
      const blob = new Blob([svgData], { type: 'image/svg+xml' });
      const objectUrl = URL.createObjectURL(blob);
      console.log('Created SVG object URL:', objectUrl);
      
      // Clear any previous errors if successful
      setError(null);
      
      return objectUrl;
    } catch (error) {
      console.error('Error in SVG conversion:', error);
      
      // If not already handled above, set a generic error
      if (!error.name || error.name !== 'RateLimitError') {
        setError({
          message: error instanceof Error ? error.message : 'SVG conversion failed. Please try again or select a different format.',
          type: 'generic'
        });
      }
      
      // Always return null to signal conversion failure
      return null;
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
  
  // Modified button click handler that bypasses the parent's onDownload if needed
  const handleDownloadClick = (e: React.MouseEvent) => {
    e.preventDefault(); // Prevent any default behavior
    e.stopPropagation(); // Stop propagation to parent elements
    console.log('Download button click intercepted');
    
    // Force direct download immediately without using the parent's callback
    const forceDirectDownload = async () => {
      console.log('Forcing direct download...');
      const fileExtension = selectedFormat;
      setIsProcessing(true);
      
      try {
        // If we already have a processed URL, use it
        if (processedImageUrl) {
          await downloadProcessedImage(processedImageUrl, fileExtension);
        } else {
          // Otherwise process the image first
          const url = await processImage(imageUrl, selectedFormat, selectedSize);
          if (url) {
            await downloadProcessedImage(url, fileExtension);
          } else {
            // Fallback to original URL if processing fails
            await downloadProcessedImage(imageUrl, fileExtension);
          }
        }
      } catch (error) {
        console.error('Error in direct download:', error);
      } finally {
        setIsProcessing(false);
      }
    };
    
    // Use direct download immediately (bypassing parent callback)
    forceDirectDownload();
    
    // Also try the parent's onDownload as a secondary approach (it might work better in some cases)
    if (onDownload) {
      console.log('Also calling parent onDownload as secondary approach');
      setTimeout(() => onDownload(selectedFormat, selectedSize), 500);
    }
  };
  
  // Helper function to safely download the processed image
  const downloadProcessedImage = async (url: string, fileExtension: string) => {
    console.log('downloadProcessedImage called with:', { url: url.substring(0, 30) + '...', fileExtension });
    const filename = `${conceptTitle}${variationName ? `-${variationName}` : ''}.${fileExtension}`;
    console.log('Download filename:', filename);
    
    try {
      const triggerDownload = (downloadUrl: string, name: string) => {
        console.log('Triggering download with URL:', downloadUrl.substring(0, 30) + '...');
        
        // Force download using browser-native approach
        try {
          // Create a link and trigger the download
          const a = document.createElement('a');
          a.href = downloadUrl;
          a.download = name;
          a.rel = 'noopener noreferrer'; // Security best practice
          a.style.display = 'none'; // Hide the element
          
          // Add to DOM, trigger click, and remove
          document.body.appendChild(a);
          
          console.log('Downloading with a.download method');
          
          // Use setTimeout to ensure the browser has time to process
          setTimeout(() => {
            const clickEvent = new MouseEvent('click', {
              view: window,
              bubbles: true,
              cancelable: true,
            });
            a.dispatchEvent(clickEvent);
            
            // Delay cleanup to ensure download starts
            setTimeout(() => {
              document.body.removeChild(a);
              if (downloadUrl.startsWith('blob:')) {
                URL.revokeObjectURL(downloadUrl);
              }
              console.log('Download click event completed and cleaned up');
            }, 300);
          }, 100);
        } catch (downloadError) {
          console.error('Error with download link approach:', downloadError);
          
          // Try an alternative method - iFrame download
          console.log('Attempting iframe download method');
          const iframe = document.createElement('iframe');
          iframe.style.display = 'none';
          document.body.appendChild(iframe);
          
          try {
            const iframeDoc = iframe.contentWindow?.document || iframe.contentDocument;
            if (iframeDoc) {
              iframeDoc.open();
              iframeDoc.write(`
                <html>
                <head>
                  <title>Downloading ${name}</title>
                </head>
                <body>
                  <a id="download" href="${downloadUrl}" download="${name}">Download</a>
                  <script>
                    document.getElementById('download').click();
                  </script>
                </body>
                </html>
              `);
              iframeDoc.close();
            }
            
            // Remove iframe after a delay
            setTimeout(() => {
              document.body.removeChild(iframe);
              if (downloadUrl.startsWith('blob:')) {
                URL.revokeObjectURL(downloadUrl);
              }
            }, 1000);
          } catch (iframeError) {
            console.error('Error with iframe download method:', iframeError);
            // If iframe method fails, try direct window.location approach as last resort
            window.open(downloadUrl, '_blank');
          }
        }
      };
      
      // Handle SVG object URLs specially
      if (url.startsWith('blob:') && fileExtension === 'svg') {
        console.log('Handling SVG blob URL');
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`Failed to fetch SVG: ${response.status} ${response.statusText}`);
        }
        const svgText = await response.text();
        
        // Create a download for the raw SVG content
        const blob = new Blob([svgText], { type: 'image/svg+xml' });
        const downloadUrl = URL.createObjectURL(blob);
        
        console.log('Created download URL for SVG:', downloadUrl);
        triggerDownload(downloadUrl, filename);
      } else if (url.startsWith('data:')) {
        console.log('Handling data URL');
        // For data URLs (common with PNG/JPG formats)
        triggerDownload(url, filename);
      } else {
        console.log('Handling regular URL');
        try {
          // For regular URLs, fetch first to ensure proper download
          const response = await fetch(url, { 
            method: 'GET',
            headers: {
              'Content-Type': 'application/octet-stream',
            },
            cache: 'no-store',
          });
          
          if (!response.ok) {
            throw new Error(`Failed to fetch: ${response.status} ${response.statusText}`);
          }
          
          const blob = await response.blob();
          const objectUrl = URL.createObjectURL(blob);
          
          console.log('Created object URL from fetched content:', objectUrl);
          triggerDownload(objectUrl, filename);
        } catch (fetchError) {
          console.error('Fetch error, trying direct download:', fetchError);
          // Fallback if fetch fails - try direct download
          triggerDownload(url, filename);
        }
      }
      
      console.log(`Downloaded ${fileExtension.toUpperCase()} file: ${filename}`);
    } catch (error) {
      console.error('Error downloading the image:', error);
      
      // Last resort fallback - open in new tab and let user save manually
      try {
        console.log('Attempting fallback: opening image in new tab');
        window.open(url, '_blank');
      } catch (fallbackError) {
        console.error('Even fallback failed:', fallbackError);
      }
      
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
    <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-4">
      {/* Error message */}
      {error && (
        <div className="mb-4">
          <ErrorMessage 
            message={error.message}
            type={error.type as any}
            onDismiss={() => setError(null)}
          />
        </div>
      )}

      <div className="flex flex-col">
        <div className="space-y-4">
          {/* Format selection - keeping this on its own line for better readability */}
          <div>
            <h4 className="text-sm font-semibold text-indigo-700 mb-3">Format</h4>
            <div className="flex flex-wrap gap-2 sm:gap-3">
              {Object.entries(formatInfo).map(([format, info]) => (
                <button 
                  key={format}
                  className={`flex-1 border rounded-lg p-2 sm:p-3 hover:shadow-md transition-all cursor-pointer text-center
                    ${selectedFormat === format ? 'border-indigo-400 bg-indigo-50 shadow-sm' : 'border-indigo-200 hover:border-indigo-300'}
                    ${(isProcessing || isAutoProcessing) ? 'opacity-75 cursor-wait' : ''}`}
                  onClick={() => setSelectedFormat(format as ExportFormat)}
                  title={info.desc}
                  disabled={isProcessing || isAutoProcessing}
                >
                  <div className="text-indigo-600 font-bold text-sm sm:text-md flex justify-center">.{format.toUpperCase()}</div>
                  <div className="text-xs text-gray-500 mt-1 sm:mt-2">{info.title}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Size selection */}
          <div>
            <h4 className="text-sm font-semibold text-indigo-700 mb-3">Size</h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3">
              {Object.entries(sizeMap).map(([size, label]) => (
                <button 
                  key={size}
                  className={`border rounded-lg p-2 sm:p-3 hover:shadow-md transition-all cursor-pointer text-center
                    ${selectedSize === size ? 'border-indigo-400 bg-indigo-50 shadow-sm' : 'border-indigo-200 hover:border-indigo-300'}
                    ${(isProcessing || isAutoProcessing) ? 'opacity-75 cursor-wait' : ''}`}
                  onClick={() => setSelectedSize(size as ExportSize)}
                  disabled={isProcessing || isAutoProcessing}
                >
                  <div className={`font-medium flex justify-center text-sm sm:text-base ${selectedSize === size ? 'text-indigo-700' : 'text-indigo-600'}`}>
                    {size.charAt(0).toUpperCase() + size.slice(1)}
                  </div>
                  <div className="text-xs text-gray-500 mt-1 sm:mt-2">{label}</div>
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
        <div className="mt-4 pt-4 sm:mt-5 sm:pt-5 border-t border-indigo-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div className="text-xs sm:text-sm text-gray-600 mb-2 sm:mb-0">
            <span className="font-medium">Selected:</span> {selectedFormat.toUpperCase()}, {sizeMap[selectedSize]}
          </div>
          
          <div className="flex gap-2 sm:gap-3 w-full sm:w-auto">
            <button 
              className="flex-1 sm:flex-none px-3 sm:px-4 py-2 min-w-[90px] sm:min-w-[100px] border border-indigo-200 text-indigo-600 font-medium rounded-lg hover:bg-indigo-50 transition-colors flex justify-center items-center"
              onClick={handlePreview}
              disabled={isProcessing || isAutoProcessing}
            >
              {(isProcessing || isAutoProcessing) ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-1 sm:mr-2 h-3 w-3 sm:h-4 sm:w-4 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="text-sm sm:text-base">{isAutoProcessing ? 'Preparing' : 'Processing'}</span>
                </span>
              ) : (
                <span className="text-sm sm:text-base">Preview</span>
              )}
            </button>
            <button 
              className="flex-1 sm:flex-none px-3 sm:px-4 py-2 min-w-[90px] sm:min-w-[120px] bg-gradient-to-r from-indigo-600 to-indigo-400 text-white font-medium rounded-lg shadow-sm hover:shadow-md transition-all flex justify-center items-center"
              onClick={handleDownloadClick}
              disabled={isProcessing || isAutoProcessing}
              data-testid="download-button"
            >
              {(isProcessing || isAutoProcessing) ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-1 sm:mr-2 h-3 w-3 sm:h-4 sm:w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="text-sm sm:text-base">{isAutoProcessing ? 'Preparing' : 'Processing'}</span>
                </span>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 sm:h-4 sm:w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm sm:text-base">Download</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}; 