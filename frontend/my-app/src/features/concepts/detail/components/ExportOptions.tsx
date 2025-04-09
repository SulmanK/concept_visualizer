import React, { useState, useEffect, useRef } from 'react';
import { ErrorMessage } from '../../../../components/ui';
import { RateLimitError, ExportFormat, ExportSize } from '../../../../services/apiClient';
import { useExportImageMutation } from '../../../../hooks/useExportImageMutation';
import { extractStoragePathFromUrl } from '../../../../utils/url';
import './ExportOptions.css';

export interface ExportOptionsProps {
  /**
   * URL of the image to process and download
   */
  imageUrl: string | undefined;
  
  /**
   * Storage path of the image (if available)
   * Will be extracted from imageUrl if not provided
   */
  storagePath?: string;
  
  /**
   * Title/name of the concept
   */
  conceptTitle: string;
  
  /**
   * Variation name
   */
  variationName?: string;
  
  /**
   * Indicates if this is a palette variation (vs an original concept)
   * Used to determine which storage bucket to use
   */
  isPaletteVariation?: boolean;
  
  /**
   * Callback when the download button is clicked
   */
  onDownload?: (format: ExportFormat, size: ExportSize) => void;
}

const sizeMap = {
  small: '256px',
  medium: '512px',
  large: '1024px',
  original: 'Max Quality'
};

/**
 * Component that allows users to export a concept in different formats and sizes
 */
export const ExportOptions: React.FC<ExportOptionsProps> = ({
  imageUrl,
  storagePath,
  conceptTitle,
  variationName = '',
  isPaletteVariation = false,
  onDownload
}) => {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('png');
  const [selectedSize, setSelectedSize] = useState<ExportSize>('medium');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isPreviewing, setIsPreviewing] = useState<boolean>(false);
  
  // References to track blob URLs for cleanup
  const revokedUrlsRef = useRef<Set<string>>(new Set());
  
  // Use our new export mutation hook
  const { 
    mutate: exportImage, 
    isPending: isExporting,
    error: exportError
  } = useExportImageMutation();
  
  // Use another instance of the export mutation hook specifically for previews
  const {
    mutate: previewImage,
    isPending: isPreviewExporting,
    error: previewError
  } = useExportImageMutation();
  
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
  
  // Update error message when export fails
  useEffect(() => {
    if (exportError) {
      const error = exportError as Error;
      // Format a user-friendly error message
      if (error instanceof RateLimitError) {
        setErrorMessage(`Export limit reached: ${error.getUserFriendlyMessage()}`);
      } else {
        setErrorMessage(`Failed to export image: ${error.message}`);
      }
    } else if (previewError) {
      const error = previewError as Error;
      // Format a user-friendly error message for preview errors
      if (error instanceof RateLimitError) {
        setErrorMessage(`Preview limit reached: ${error.getUserFriendlyMessage()}`);
      } else {
        setErrorMessage(`Failed to generate preview: ${error.message}`);
      }
    } else {
      setErrorMessage('');
    }
  }, [exportError, previewError]);
  
  // Clear error on format or size change
  useEffect(() => {
    setErrorMessage('');
  }, [selectedFormat, selectedSize]);
  
  // Clean up any blob URLs when component unmounts or preview changes
  useEffect(() => {
    return () => {
      if (previewUrl && previewUrl.startsWith('blob:')) {
        safeRevokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);
  
  // Helper function to determine which bucket to use
  const determineStorageBucket = (): string => {
    // If isPaletteVariation is explicitly set, use that
    if (isPaletteVariation) {
      return 'palette-images';
    }
    
    // Otherwise try to infer from the path or URL
    if (storagePath && storagePath.includes('palette')) {
      return 'palette-images';
    }
    
    // Check if the URL contains palette indicators
    if (imageUrl && (
      imageUrl.includes('palette-images') || 
      imageUrl.includes('palette') ||
      (variationName && variationName.toLowerCase().includes('palette'))
    )) {
      return 'palette-images';
    }
    
    // Default to concept-images bucket
    return 'concept-images';
  };
  
  // Handle preview button click
  const handlePreview = async () => {
    // Check if we have a valid imageUrl
    if (!imageUrl) {
      setErrorMessage('No image URL available for preview');
      return;
    }
    
    // Set previewing state
    setIsPreviewing(true);
    setErrorMessage('');
    
    try {
      // Extract storage path from URL if not provided
      const imagePath = storagePath || extractStoragePathFromUrl(imageUrl);
      
      if (!imagePath) {
        setErrorMessage('Could not determine storage path for image');
        setIsPreviewing(false);
        return;
      }
      
      // Determine which bucket the image is in
      const bucket = determineStorageBucket();
      console.log(`Using bucket "${bucket}" for preview of image: ${imagePath}`);
      
      // Use the preview mutation to generate the preview
      previewImage({
        imageIdentifier: imagePath,
        format: selectedFormat,
        size: selectedSize,
        svgParams: selectedFormat === 'svg' ? {
          color_mode: 'color',
          hierarchical: true
        } : undefined,
        bucket: bucket // Pass the bucket information
      }, {
        onSuccess: (blob) => {
          console.log('Preview generated successfully, creating blob URL');
          // Create URL for preview
          const url = URL.createObjectURL(blob);
          
          // Open in new tab
          window.open(url, '_blank');
          
          // Clean up blob URL after a delay
          setTimeout(() => {
            safeRevokeObjectURL(url);
            setIsPreviewing(false);
          }, 1000);
        },
        onError: (error) => {
          console.error('Preview generation failed:', error);
          setIsPreviewing(false);
        },
        onSettled: () => {
          // Reset the state regardless of success or failure
          setTimeout(() => {
            setIsPreviewing(false);
          }, 500);
        }
      });
    } catch (error) {
      console.error('Error creating preview:', error);
      setErrorMessage(`Failed to create preview: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setIsPreviewing(false);
    }
  };
  
  // Handle download button click
  const handleDownloadClick = () => {
    // Check if we have a valid imageUrl
    if (!imageUrl) {
      setErrorMessage('No image URL available for download');
      return;
    }
    
    try {
      // Extract storage path from URL if not provided
      const imagePath = storagePath || extractStoragePathFromUrl(imageUrl);
      
      if (!imagePath) {
        setErrorMessage('Could not determine storage path for image');
        return;
      }
      
      // Determine which bucket the image is in
      const bucket = determineStorageBucket();
      console.log(`Using bucket "${bucket}" for image: ${imagePath}`);
      
      // Create a filename for the download
      const filename = `${conceptTitle}${variationName ? `-${variationName}` : ''}-${selectedSize}.${selectedFormat}`;
      
      // Use the export mutation to download the file
      exportImage({
        imageIdentifier: imagePath,
        format: selectedFormat,
        size: selectedSize,
        svgParams: selectedFormat === 'svg' ? {
          color_mode: 'color',
          hierarchical: true
        } : undefined,
        bucket: bucket // Pass the bucket information
      }, {
        onSuccess: (blob) => {
          // Create a download link
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          a.style.display = 'none';
          
          // Trigger the download
          document.body.appendChild(a);
          a.click();
          
          // Clean up
          setTimeout(() => {
            document.body.removeChild(a);
            safeRevokeObjectURL(url);
          }, 300);
        }
      });
      
      // Also try the parent's onDownload as a secondary approach (if provided)
      if (onDownload) {
        onDownload(selectedFormat, selectedSize);
      }
    } catch (error) {
      console.error('Error initiating download:', error);
      setErrorMessage(`Failed to initiate download: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };
  
  return (
    <div className="export-options">
      <div className="export-options-body">
        <div className="export-format-section">
          <div className="export-section-title">Format</div>
          <div className="export-format-buttons">
            <button 
              className={`format-button ${selectedFormat === 'png' ? 'selected' : ''}`}
              onClick={() => setSelectedFormat('png')}
            >
              PNG
            </button>
            <button 
              className={`format-button ${selectedFormat === 'jpg' ? 'selected' : ''}`}
              onClick={() => setSelectedFormat('jpg')}
            >
              JPG
            </button>
            <button 
              className={`format-button ${selectedFormat === 'svg' ? 'selected' : ''}`}
              onClick={() => setSelectedFormat('svg')}
            >
              SVG
            </button>
          </div>
        </div>
        
        <div className="export-size-section">
          <div className="export-section-title">Size</div>
          <div className="export-size-buttons">
            <button 
              className={`size-button ${selectedSize === 'small' ? 'selected' : ''}`}
              onClick={() => setSelectedSize('small')}
            >
              <span className="size-label">256px</span>
            </button>
            <button 
              className={`size-button ${selectedSize === 'medium' ? 'selected' : ''}`}
              onClick={() => setSelectedSize('medium')}
            >
              <span className="size-label">512px</span>
            </button>
            <button 
              className={`size-button ${selectedSize === 'large' ? 'selected' : ''}`}
              onClick={() => setSelectedSize('large')}
            >
              <span className="size-label">1024px</span>
            </button>
            <button 
              className={`size-button ${selectedSize === 'original' ? 'selected' : ''}`}
              onClick={() => setSelectedSize('original')}
            >
              <span className="size-label">Max Quality</span>
            </button>
          </div>
        </div>
        
        {errorMessage && (
          <div className="export-error-message">
            <ErrorMessage message={errorMessage} />
          </div>
        )}
        
        <div className="export-actions">
          <button 
            className="preview-button" 
            onClick={handlePreview}
            disabled={isPreviewExporting || isPreviewing || !imageUrl}
          >
            {isPreviewExporting || isPreviewing ? 'Previewing...' : 'Preview'}
          </button>
          <button 
            className="download-button"
            onClick={handleDownloadClick}
            disabled={isExporting || !imageUrl}
          >
            {isExporting ? 'Exporting...' : 'Download'}
          </button>
        </div>
      </div>
    </div>
  );
}; 