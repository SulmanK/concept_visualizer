import React, { useState, useEffect, useCallback, useRef } from 'react';
import { ErrorMessage } from '../../../../components/ui';
import { RateLimitError } from '../../../../services/apiClient';
import { eventService, AppEvent } from '../../../../services/eventService';
import { useSvgConversionMutation } from '../../../../hooks/useSvgConversionMutation';
import { useOptimisticRateLimitUpdate } from '../../../../hooks/useRateLimitsQuery';

export interface ExportOptionsProps {
  /**
   * URL of the image to process and download
   */
  imageUrl: string | undefined;
  
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
  onDownload?: (format: ExportFormat, size: ExportSize) => void;
}

type ExportFormat = 'png' | 'jpg' | 'svg';
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
  variationName = '',
  onDownload
}) => {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('png');
  const [selectedSize, setSelectedSize] = useState<ExportSize>('medium');
  const [processedImageUrl, setProcessedImageUrl] = useState<string>('');
  const [isAutoProcessing, setIsAutoProcessing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>('');
  // Track already revoked blob URLs to prevent double revocation
  const revokedUrlsRef = useRef<Set<string>>(new Set());
  
  // Use React Query hooks for SVG conversion and rate limits
  const { decrementLimit } = useOptimisticRateLimitUpdate();
  const { 
    mutate: convertToSvg, 
    isPending: isSvgConverting,
    isError: isSvgError,
    error: svgError
  } = useSvgConversionMutation();
  
  // Safe URL revocation function to prevent revoking the same URL twice
  const safeRevokeObjectURL = (url: string) => {
    if (!url.startsWith('blob:')) return;
    
    if (!revokedUrlsRef.current.has(url)) {
      console.log('Revoking blob URL:', url);
      URL.revokeObjectURL(url);
      revokedUrlsRef.current.add(url);
    } else {
      console.log('URL already revoked, skipping:', url);
    }
  };
  
  // Function to reset the component state when something goes wrong
  const resetState = () => {
    console.log('Resetting component state');
    
    // Clean up any existing blob URL
    if (processedImageUrl && processedImageUrl.startsWith('blob:')) {
      safeRevokeObjectURL(processedImageUrl);
    }
    
    // Reset all state values
    setProcessedImageUrl('');
    setIsAutoProcessing(false);
  };
  
  // Handle case where imageUrl is undefined
  useEffect(() => {
    if (!imageUrl) {
      setErrorMessage('No image URL available for export. Please try again later.');
      resetState();
    } else {
      setErrorMessage('');
      console.log('ExportOptions: Processing Original image:', imageUrl.substring(0, 50) + '...');
    }
  }, [imageUrl]);

  // Add a dedicated effect to track and log imageUrl changes for debugging
  useEffect(() => {
    console.log(`ExportOptions: Processing ${variationName || 'original'} image:`, 
      imageUrl ? `${imageUrl.substring(0, 50)}...` : 'undefined');
    
    // Reset processed URL when image changes
    if (processedImageUrl) {
      // Clean up any blob URLs before resetting
      if (processedImageUrl.startsWith('blob:')) {
        console.log('Cleaning up blob URL on image change:', processedImageUrl);
        safeRevokeObjectURL(processedImageUrl);
      }
      setProcessedImageUrl('');
    }
  }, [imageUrl, variationName]);

  // Remove the auto-processing effect
  useEffect(() => {
    // Reset the processed URL when selections change or when the image URL changes
    if (processedImageUrl) {
      // Clean up any blob URLs before resetting
      if (processedImageUrl.startsWith('blob:')) {
        console.log('Cleaning up blob URL on format/size change:', processedImageUrl);
        safeRevokeObjectURL(processedImageUrl);
      }
      setProcessedImageUrl('');
    }
  }, [selectedFormat, selectedSize, imageUrl]);

  // Clear error on format or size change
  useEffect(() => {
    setErrorMessage('');
  }, [selectedFormat, selectedSize]);

  // Add error recovery mechanism - if there's an error in processing, reset after a timeout
  useEffect(() => {
    if (errorMessage && (isSvgConverting || isAutoProcessing)) {
      console.log('Error detected while processing, resetting state after delay');
      const timeoutId = setTimeout(() => {
        resetState();
      }, 2000); // Reset state after 2 seconds
      
      return () => clearTimeout(timeoutId);
    }
  }, [errorMessage, isSvgConverting, isAutoProcessing]);

  // Update the error message when SVG conversion fails
  useEffect(() => {
    if (isSvgError && svgError) {
      const errorMsg = svgError instanceof Error ? svgError.message : 'SVG conversion failed';
      // Set an appropriate error message
      if (errorMsg.includes('rate limit')) {
        setErrorMessage('SVG conversion limit reached. Please try again later or choose a different format.');
      } else if (errorMsg.includes('timed out')) {
        setErrorMessage('SVG conversion timed out. Please try again or choose a different format.');
      } else {
        setErrorMessage(`Failed to process image: ${errorMsg}`);
      }
    }
  }, [isSvgError, svgError]);

  const processImageForPreview = async () => {
    if (!imageUrl) {
      setErrorMessage('No image URL available for processing');
      resetState();
      return null;
    }
    
    // Don't start if already processing
    if (isSvgConverting || isAutoProcessing) {
      console.log('Already processing image, skipping new request');
      return processedImageUrl || null;
    }
    
    try {
      // Clear any previous errors
      setErrorMessage('');
      
      setIsAutoProcessing(true);
      // Process the image with the current format and size
      console.log('Processing image for preview');
      
      const result = await processImage(imageUrl, selectedFormat, selectedSize);
      
      setProcessedImageUrl(result || '');
      setIsAutoProcessing(false);
      return result;
    } catch (error) {
      console.error('Error processing image for preview:', error);
      setIsAutoProcessing(false);
      
      // Set an appropriate error message
      if (error instanceof Error) {
        // Check for rate limit errors
        if (error.name === 'RateLimitError' || error.message.includes('rate limit')) {
          setErrorMessage('SVG conversion limit reached. Please try again later or choose a different format.');
        } else if (error.message.includes('timed out')) {
          setErrorMessage('SVG conversion timed out. Please try again or choose a different format.');
          resetState(); // Ensure full reset on timeout
        } else {
          setErrorMessage(`Failed to process image: ${error.message}`);
        }
      } else {
        setErrorMessage('An unexpected error occurred');
      }
      
      return null;
    }
  };
  
  // Function to process the image according to format and size
  const processImage = async (
    url: string | undefined, 
    format: ExportFormat, 
    size: ExportSize
  ): Promise<string | null> => {
    if (!url) {
      setErrorMessage('No image URL available for processing');
      return null;
    }
    
    return new Promise((resolve, reject) => {
      // Handle SVG format separately with server-side conversion using React Query
      if (format === 'svg') {
        // For SVG we use our React Query mutation
        convertToSvg(
          {
            imageData: url,
            maxSize: sizePixels[size],
            colorMode: 'color',
            hierarchical: true,
            filterSpeckleSize: 4,
            cornerThreshold: 60.0,
            lengthThreshold: 4.0,
            spliceThreshold: 45.0,
            pathPrecision: 8,
            colorQuantizationSteps: 16
          },
          {
            onSuccess: (result) => {
              resolve(result);
            },
            onError: (error) => {
              console.warn('SVG conversion failed, using PNG fallback:', error);
              // Fallback to PNG if SVG conversion fails
              processToPng(url, size)
                .then(resolve)
                .catch(reject);
            }
          }
        );
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

  const handlePreview = async () => {
    if (!imageUrl) {
      setErrorMessage('No image URL available for preview');
      resetState();
      return;
    }
    
    try {
      console.log('Preview button clicked, processing image URL for size:', selectedSize);
      setIsAutoProcessing(true);
      
      // Always regenerate SVG preview instead of trying to reuse existing blob URL
      // Process the image if we don't have a processed version yet
      const url = await processImageForPreview();
      setIsAutoProcessing(false);
      
      if (!url) {
        // If processing failed, fall back to the original URL
        console.log('Image processing failed, falling back to original URL');
        window.open(imageUrl, '_blank');
        return;
      }
      
      openImagePreview(url);
    } catch (error) {
      console.error('Error previewing image:', error);
      setIsAutoProcessing(false);
      
      if (error instanceof Error) {
        setErrorMessage(`Preview failed: ${error.message}`);
      } else {
        setErrorMessage('Preview failed due to an unknown error');
      }
      
      // Reset state after a slight delay
      setTimeout(resetState, 1000);
      
      // Fall back to original URL
      window.open(imageUrl, '_blank');
    }
  };
  
  // Helper function to open image preview
  const openImagePreview = async (url: string) => {
    // Check if the URL is an SVG object URL
    if (url.startsWith('blob:') && selectedFormat === 'svg') {
      try {
        // For SVG, we might need to fetch the content and create a proper viewable HTML
        const response = await fetch(url);
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
        
        // Clean up the temporary blob URL after a delay
        setTimeout(() => {
          safeRevokeObjectURL(htmlUrl);
        }, 1000);
      } catch (error) {
        console.error('Error creating SVG preview:', error);
        window.open(url, '_blank');
      }
    } else {
      // For other formats, just open the processed image
      window.open(url, '_blank');
    }
  };
  
  // Clean up any blob URLs when component unmounts
  useEffect(() => {
    return () => {
      // Clean up blob URLs when the component unmounts
      if (processedImageUrl && processedImageUrl.startsWith('blob:')) {
        console.log('Cleaning up blob URL on unmount:', processedImageUrl);
        safeRevokeObjectURL(processedImageUrl);
      }
    };
  }, [processedImageUrl]);

  // Modified button click handler that bypasses the parent's onDownload if needed
  const handleDownloadClick = (e: React.MouseEvent) => {
    e.preventDefault(); // Prevent any default behavior
    e.stopPropagation(); // Stop propagation to parent elements
    console.log('Download button clicked, processing image for download');
    
    // Check if we have a valid image URL
    if (!imageUrl) {
      setErrorMessage('No image URL available for download');
      return;
    }
    
    // Force direct download immediately without using the parent's callback
    const forceDirectDownload = async () => {
      console.log('Forcing direct download...');
      const fileExtension = selectedFormat;
      setIsAutoProcessing(true);
      
      try {
        // Check if we already have a processed image for the current format and size
        let url: string | null = null;
        
        if (processedImageUrl && selectedFormat === 'svg' && processedImageUrl.startsWith('blob:')) {
          console.log('Using existing processed SVG URL for download:', processedImageUrl);
          url = processedImageUrl;
        } else {
          // Process the image if we don't have a processed version yet
          console.log('Processing latest image URL for download');
          
          // Add a timeout to prevent hanging
          const timeoutPromise = new Promise<null>((_, reject) => {
            setTimeout(() => reject(new Error('Image processing timed out after 20 seconds')), 20000);
          });
          
          // Race the image processing against the timeout
          try {
            url = await Promise.race([
              processImage(imageUrl, selectedFormat, selectedSize),
              timeoutPromise
            ]);
          } catch (processingError) {
            console.error('Error during image processing:', processingError);
            setErrorMessage(processingError instanceof Error ? 
              processingError.message : 'Failed to process image for download');
            url = null;
          }
        }
        
        if (url) {
          await downloadProcessedImage(url, fileExtension);
        } else {
          // Fallback to original URL if processing fails
          console.log('Image processing failed, falling back to original URL');
          await downloadProcessedImage(imageUrl, fileExtension);
        }
      } catch (error) {
        console.error('Error in direct download:', error);
        if (error instanceof Error) {
          setErrorMessage(`Download failed: ${error.message}`);
        } else {
          setErrorMessage('Download failed due to an unknown error');
        }
        
        // Reset state after a slight delay
        setTimeout(resetState, 1000);
      } finally {
        setIsAutoProcessing(false);
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
    const filename = `${conceptTitle}${variationName ? `-${variationName}` : ''}-${selectedSize}.${fileExtension}`;
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
                safeRevokeObjectURL(downloadUrl);
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
                safeRevokeObjectURL(downloadUrl);
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
    <div className="space-y-5">
      {/* Add an indicator to show which image is being processed */}
      <div className="p-3 bg-indigo-50 rounded-md border border-indigo-100 text-sm">
        <p className="font-medium text-indigo-700 mb-1">Currently processing:</p>
        <div className="flex items-center text-indigo-600">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
          </svg>
          <span className="truncate">{variationName || 'Original'} image</span>
        </div>
      </div>
      
      {/* Format and size selection options */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-4">
        {/* Error message */}
        {errorMessage && (
          <div className="mb-4">
            <ErrorMessage 
              message={errorMessage}
              type="generic"
              onDismiss={() => setErrorMessage('')}
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
                      ${(isSvgConverting || isAutoProcessing) ? 'opacity-75 cursor-wait' : ''}`}
                    onClick={() => setSelectedFormat(format as ExportFormat)}
                    title={info.desc}
                    disabled={isSvgConverting || isAutoProcessing}
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
                      ${(isSvgConverting || isAutoProcessing) ? 'opacity-75 cursor-wait' : ''}`}
                    onClick={() => setSelectedSize(size as ExportSize)}
                    disabled={isSvgConverting || isAutoProcessing}
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
                Processing image with selected settings...
              </div>
            )}
            {isSvgConverting && (
              <div className="text-xs text-indigo-600 flex items-center">
                <svg className="animate-spin -ml-1 mr-1 h-3 w-3 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Preparing download...
              </div>
            )}
            {!isAutoProcessing && !isSvgConverting && processedImageUrl && (
              <div className="text-xs text-green-600 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Ready for download
              </div>
            )}
            {!isAutoProcessing && !isSvgConverting && !processedImageUrl && (
              <div className="text-xs text-gray-600">
                Click preview or download to process the image
              </div>
            )}
          </div>
          
          {/* Download controls */}
          <div className="mt-4 pt-4 sm:mt-5 sm:pt-5 border-t border-indigo-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <div className="text-xs sm:text-sm text-gray-600 mb-2 sm:mb-0">
              <span className="font-medium">Selected:</span> {selectedFormat.toUpperCase()}, {sizeMap[selectedSize as ExportSize]}
            </div>
            
            <div className="flex gap-2 sm:gap-3 w-full sm:w-auto">
              <button 
                className="flex-1 sm:flex-none px-3 sm:px-4 py-2 min-w-[90px] sm:min-w-[100px] border border-indigo-200 text-indigo-600 font-medium rounded-lg hover:bg-indigo-50 transition-colors flex justify-center items-center"
                onClick={handlePreview}
                disabled={isSvgConverting || isAutoProcessing}
              >
                {(isSvgConverting || isAutoProcessing) ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-1 sm:mr-2 h-3 w-3 sm:h-4 sm:w-4 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span className="text-sm sm:text-base">Processing</span>
                  </span>
                ) : (
                  <span className="text-sm sm:text-base">Preview</span>
                )}
              </button>
              <button 
                className="flex-1 sm:flex-none px-3 sm:px-4 py-2 min-w-[90px] sm:min-w-[120px] bg-gradient-to-r from-indigo-600 to-indigo-400 text-white font-medium rounded-lg shadow-sm hover:shadow-md transition-all flex justify-center items-center"
                onClick={handleDownloadClick}
                disabled={isSvgConverting || isAutoProcessing}
                data-testid="download-button"
              >
                {(isSvgConverting || isAutoProcessing) ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-1 sm:mr-2 h-3 w-3 sm:h-4 sm:w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span className="text-sm sm:text-base">
                      {isSvgConverting ? 'Downloading' : 'Processing'}
                    </span>
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
    </div>
  );
}; 