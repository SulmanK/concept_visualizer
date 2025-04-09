import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, ExportFormat, ExportSize, RateLimitError } from '../services/apiClient';
import { useOptimisticRateLimitUpdate } from './useRateLimitsQuery';
import { createQueryErrorHandler } from './useErrorHandling';

export interface ExportImageParams {
  /**
   * Storage path identifier for the image (e.g., user_id/.../image.png)
   */
  imageIdentifier: string;
  
  /**
   * Target format for export
   */
  format: ExportFormat;
  
  /**
   * Target size for export
   */
  size: ExportSize;
  
  /**
   * Optional parameters for SVG conversion (when format is 'svg')
   */
  svgParams?: Record<string, any>;
  
  /**
   * Storage bucket where the image is stored
   * (either 'concept-images' or 'palette-images')
   */
  bucket?: string;
}

/**
 * Hook for exporting images in different formats
 * Handles rate limit optimistic updates and error handling
 */
export function useExportImageMutation() {
  const queryClient = useQueryClient();
  const { decrementLimit } = useOptimisticRateLimitUpdate();
  const errorHandler = createQueryErrorHandler({
    title: 'Export Failed',
    defaultMessage: 'Failed to export image. Please try again.',
  });

  return useMutation({
    mutationFn: async ({ imageIdentifier, format, size, svgParams, bucket }: ExportImageParams) => {
      // Apply optimistic update based on format
      // SVG conversions are more intensive, so we use the svg_conversion rate limit
      if (format === 'svg') {
        decrementLimit('svg_conversion');
      } else {
        // For PNG/JPG, use a new rate limit category
        decrementLimit('image_export');
      }
      
      try {
        // Call the API to process the export
        const blob = await apiClient.exportImage(
          imageIdentifier,
          format,
          size,
          svgParams,
          bucket
        );
        
        return blob;
      } catch (error) {
        // If there's an error, ensure rate limits are refreshed
        await queryClient.fetchQuery({ queryKey: ['rateLimits'] });
        throw error;
      }
    },
    
    onSuccess: async (blob, { format }) => {
      // Create an object URL from the blob
      const objectUrl = URL.createObjectURL(blob);
      
      // Trigger the download
      const downloadLink = document.createElement('a');
      downloadLink.href = objectUrl;
      downloadLink.download = `exported_image.${format}`; // The component will override this
      
      // Use setTimeout to ensure the browser has time to process
      setTimeout(() => {
        // Append to body, click, and remove
        document.body.appendChild(downloadLink);
        downloadLink.click();
        
        // Clean up
        setTimeout(() => {
          document.body.removeChild(downloadLink);
          URL.revokeObjectURL(objectUrl);
        }, 300);
      }, 100);
      
      // Refresh rate limits to get the accurate count
      await queryClient.fetchQuery({ queryKey: ['rateLimits'] });
    },
    
    onError: (error) => {
      // Use the error handler to display appropriate error messages
      errorHandler(error);
    },
    
    onSettled: async () => {
      // Always ensure we have the latest rate limits data
      await queryClient.fetchQuery({ queryKey: ['rateLimits'] });
    }
  });
} 