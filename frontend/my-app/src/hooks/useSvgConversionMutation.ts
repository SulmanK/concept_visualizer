import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/apiClient';
import { AppEvent, eventService } from '../services/eventService';
import { useOptimisticRateLimitUpdate } from './useRateLimitsQuery';

type SVGConversionParams = {
  imageData: string;
  maxSize: number;
  colorMode?: 'binary' | 'color' | 'grayscale';
  hierarchical?: boolean;
  filterSpeckleSize?: number;
  cornerThreshold?: number;
  lengthThreshold?: number;
  spliceThreshold?: number;
  pathPrecision?: number;
  colorQuantizationSteps?: number;
};

interface SVGConversionResponse {
  success: boolean;
  message?: string;
  svg_data: string;
}

/**
 * Hook for converting images to SVG format
 * Handles rate limit optimistic updates and error handling
 */
export function useSvgConversionMutation() {
  const queryClient = useQueryClient();
  const { decrementLimit } = useOptimisticRateLimitUpdate();

  return useMutation<string, Error, SVGConversionParams>({
    mutationFn: async ({ 
      imageData, 
      maxSize, 
      colorMode = 'color',
      hierarchical = true,
      filterSpeckleSize = 4,
      cornerThreshold = 60.0,
      lengthThreshold = 4.0,
      spliceThreshold = 45.0,
      pathPrecision = 8,
      colorQuantizationSteps = 16
    }) => {
      // Apply optimistic update BEFORE making the API call
      decrementLimit('svg_conversion');
      
      // Create a controller for timeout handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout
      
      try {
        // First convert the image to a data URL if it's not already
        let imageDataToSend = imageData;
        if (!imageData.startsWith('data:') && !imageData.startsWith('blob:')) {
          // Fetch the image and convert to data URL
          const response = await fetch(imageData);
          const blob = await response.blob();
          imageDataToSend = await new Promise<string>((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result as string);
            reader.readAsDataURL(blob);
          });
        }
        
        // Make the API call
        const { data } = await apiClient.post<SVGConversionResponse>('svg/convert-to-svg', {
          image_data: imageDataToSend,
          max_size: maxSize,
          color_mode: colorMode,
          hierarchical,
          filter_speckle_size: filterSpeckleSize,
          corner_threshold: cornerThreshold,
          length_threshold: lengthThreshold,
          splice_threshold: spliceThreshold,
          path_precision: pathPrecision,
          color_quantization_steps: colorQuantizationSteps
        }, { signal: controller.signal });
        
        // Clear the timeout
        clearTimeout(timeoutId);
        
        // The apiClient.post has already processed the headers and updated the rate limit cache
        // Directly invalidate and refetch the rate limits query to ensure UI is updated
        // with the correct values from the server
        if (data.success && data.svg_data) {
          // Remove event emission - rely on React Query instead
          // eventService.emit(AppEvent.SVG_CONVERTED);
          
          // Force an immediate refetch to get the latest rate limits
          await queryClient.fetchQuery({
            queryKey: ['rateLimits'],
          });
        }
        
        if (!data.success) {
          throw new Error(data.message || 'SVG conversion failed');
        }
        
        // Check if the SVG data is valid
        const svgData = data.svg_data.trim();
        if (!svgData.startsWith('<?xml') && !svgData.startsWith('<svg')) {
          throw new Error('Received invalid SVG data');
        }
        
        // For safer handling, create a Blob and use an Object URL
        const blob = new Blob([svgData], { type: 'image/svg+xml' });
        const objectUrl = URL.createObjectURL(blob);
        
        return objectUrl;
      } catch (error) {
        // Clear the timeout to prevent memory leaks
        clearTimeout(timeoutId);
        
        // Reset the optimistic update by refreshing rate limits
        await queryClient.fetchQuery({ 
          queryKey: ['rateLimits'],
        });
        
        // Rethrow the error to be handled by the mutation error handler
        throw error;
      }
    },
    onSettled: async () => {
      // Always ensure we have the latest rate limits data when the mutation settles
      // by forcing a refetch rather than just invalidating
      await queryClient.fetchQuery({ queryKey: ['rateLimits'] });
    },
    onError: (error) => {
      console.error('SVG conversion failed:', error);
      // The component using this hook will handle the error display
    }
  });
} 