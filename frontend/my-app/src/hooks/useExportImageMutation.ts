import { useMutation, useQueryClient, UseMutationResult } from '@tanstack/react-query';
import { apiClient, ExportFormat, ExportSize, RateLimitError } from '../services/apiClient';
import { useOptimisticRateLimitUpdate } from './useRateLimitsQuery';
import { createQueryErrorHandler } from '../utils/errorUtils';

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
  
  /**
   * Optional timestamp for cache busting.
   * This is not sent to the server, just used to force React Query to treat 
   * identical requests as different mutations.
   */
  _timestamp?: number;
}

// Define a more specific return type for the hook that includes reset
type ExportImageMutationResult = UseMutationResult<Blob, Error, ExportImageParams> & {
  reset: () => void; // Explicitly include the reset function type
};

/**
 * Hook for exporting images in different formats
 * Handles rate limit optimistic updates and error handling
 * The hook returns the Blob directly without triggering downloads automatically
 * 
 * @returns Mutation object with mutate, status, and reset functions
 */
export function useExportImageMutation(): ExportImageMutationResult {
  const queryClient = useQueryClient();
  const { decrementLimit } = useOptimisticRateLimitUpdate();
  const errorHandler = createQueryErrorHandler({
    title: 'Export Failed',
    defaultMessage: 'Failed to export image. Please try again.',
  });

  // Get the mutation result object which includes 'reset'
  const mutationResult = useMutation<Blob, Error, ExportImageParams>({
    mutationFn: async ({ imageIdentifier, format, size, svgParams, bucket, _timestamp }: ExportImageParams) => {
      // Apply optimistic update for the unified export_action rate limit
      decrementLimit('export_action');
      
      try {
        // Call the API to process the export
        const blob = await apiClient.exportImage(
          imageIdentifier,
          format,
          size,
          svgParams,
          bucket,
          _timestamp
        );
        
        return blob;
      } catch (error) {
        // If there's an error, ensure rate limits are refreshed
        await queryClient.fetchQuery({ queryKey: ['rateLimits'] });
        throw error;
      }
    },
    
    onSuccess: async () => {
      // Simply refresh rate limits to get the accurate count
      // No automatic download handling - leave that to the component
      await queryClient.fetchQuery({ queryKey: ['rateLimits'] });
    },
    
    onError: (error) => {
      // Use the error handler to display appropriate error messages
      errorHandler(error);
    },
    
    onSettled: async () => {
      console.log('[useExportImageMutation] Mutation settled, refreshing rate limits.');
      // Always ensure we have the latest rate limits data
      await queryClient.fetchQuery({ queryKey: ['rateLimits'] });
    }
  });

  // Return the mutation result object along with its reset function
  return {
    ...mutationResult,
    // reset is already part of mutationResult, but explicitly returning it makes it clearer
    reset: mutationResult.reset
  };
}

/**
 * Helper function to trigger a file download from a blob
 * 
 * @param blob - The blob to download
 * @param filename - The filename to use for the download
 */
export function downloadBlob(blob: Blob, filename: string): void {
  // Create an object URL from the blob
  const objectUrl = URL.createObjectURL(blob);
  
  // Create and trigger a download link
  const downloadLink = document.createElement('a');
  downloadLink.href = objectUrl;
  downloadLink.download = filename;
  downloadLink.style.display = 'none';
  
  // Append to body, click, and remove
  document.body.appendChild(downloadLink);
  downloadLink.click();
  
  // Clean up
  setTimeout(() => {
    document.body.removeChild(downloadLink);
    URL.revokeObjectURL(objectUrl);
  }, 300);
} 