import { useQuery, useMutation, useQueryClient, UseQueryResult } from '@tanstack/react-query';
import { 
  fetchRecentConcepts, 
  fetchConceptDetail, 
  fetchConceptById, 
  ConceptData, 
  supabase,
  getSignedImageUrl
} from '../services/supabaseClient';
import { getBucketName } from '../services/configService';
import { useErrorHandling } from './useErrorHandling';
import { createQueryErrorHandler } from '../utils/errorUtils';

/**
 * Custom hook to fetch and cache recent concepts with standardized error handling
 * @returns Query result with array of concept data
 */
export function useRecentConcepts(
  userId: string | undefined, 
  limit: number = 10
): UseQueryResult<ConceptData[], Error> {
  // Set up error handling
  const errorHandler = useErrorHandling();
  const { onQueryError } = createQueryErrorHandler(errorHandler);
  
  const queryClient = useQueryClient();
  const queryKey = ['concepts', 'recent', userId, limit];
  
  // Log existing cache data for debugging
  const existingData = queryClient.getQueryData(queryKey);
  console.log(`[useRecentConcepts] Query key: ${JSON.stringify(queryKey)}`);
  console.log(`[useRecentConcepts] Cache exists: ${!!existingData}`, { 
    timestamp: new Date().toISOString(),
    dataCount: existingData ? (existingData as ConceptData[]).length : 0 
  });
  
  return useQuery<ConceptData[], Error>({
    queryKey,
    queryFn: async () => {
      if (!userId) return [];
      
      const fetchStartTime = new Date().toISOString();
      console.log(`[useRecentConcepts] Fetching concepts for user: ${userId}`, {
        timestamp: fetchStartTime,
        queryKey: JSON.stringify(queryKey)
      });
      
      const concepts = await fetchRecentConcepts(userId, limit);
      
      const fetchEndTime = new Date().toISOString();
      console.log(`[useRecentConcepts] Fetched ${concepts.length} concepts`, {
        timestamp: fetchEndTime,
        conceptIds: concepts.map(c => c.id).join(', '),
        fetchTime: new Date(fetchEndTime).getTime() - new Date(fetchStartTime).getTime() + 'ms'
      });
      
      // Optimize by batch processing instead of one by one
      return batchProcessConceptsUrls(concepts);
    },
    enabled: !!userId, // Only run the query if we have a userId
    // Removed overriding staleTime to use the global configuration
    onError: onQueryError, // Use standardized error handling
  });
}

/**
 * Custom hook to fetch and cache a specific concept with standardized error handling
 */
export function useConceptDetail(
  conceptId: string | undefined, 
  userId: string | undefined
): UseQueryResult<ConceptData | null, Error> {
  // Set up error handling
  const errorHandler = useErrorHandling();
  const { onQueryError } = createQueryErrorHandler(errorHandler);
  
  const queryClient = useQueryClient();
  const queryKey = ['concepts', 'detail', conceptId, userId];
  
  // Log existing cache data for debugging
  const existingData = queryClient.getQueryData(queryKey);
  console.log(`[useConceptDetail] Query key: ${JSON.stringify(queryKey)}`);
  console.log(`[useConceptDetail] Cache exists: ${!!existingData}`, {
    timestamp: new Date().toISOString(),
    conceptId: existingData ? (existingData as ConceptData).id : null,
    lastUpdated: existingData ? (existingData as ConceptData).updated_at : null
  });
  
  return useQuery<ConceptData | null, Error>({
    queryKey,
    queryFn: async () => {
      if (!conceptId || !userId) return null;
      
      const fetchStartTime = new Date().toISOString();
      console.log(`[useConceptDetail] Fetching concept: ${conceptId}`, {
        timestamp: fetchStartTime,
        queryKey: JSON.stringify(queryKey)
      });
      
      const concept = await fetchConceptDetail(conceptId, userId);
      
      const fetchEndTime = new Date().toISOString();
      if (!concept) {
        console.log(`[useConceptDetail] Concept not found: ${conceptId}`, {
          timestamp: fetchEndTime
        });
        return null;
      }
      
      console.log(`[useConceptDetail] Fetched concept:`, {
        timestamp: fetchEndTime,
        conceptId: concept.id,
        lastUpdated: concept.updated_at,
        variationsCount: concept.color_variations?.length || 0,
        fetchTime: new Date(fetchEndTime).getTime() - new Date(fetchStartTime).getTime() + 'ms'
      });
      
      // Process URLs in batch
      const [processedConcept] = await batchProcessConceptsUrls([concept]);
      return processedConcept;
    },
    enabled: !!conceptId && !!userId, // Only run if we have both IDs
    // Force refetch when parameters change to avoid stale data problems
    refetchOnMount: true,
    // Use shorter stale time to ensure we get fresh data
    staleTime: 1000, // Only consider data fresh for 1 second
    // Force refetch on window focus
    refetchOnWindowFocus: true,
    onError: onQueryError, // Use standardized error handling
  });
}

/**
 * Process all concepts and their variations to get signed URLs in batch operations
 * This is more efficient than processing them one by one
 */
async function batchProcessConceptsUrls(concepts: ConceptData[]): Promise<ConceptData[]> {
  if (!concepts.length) return [];
  
  console.log(`[batchProcessUrls] Batch processing ${concepts.length} concepts`);
  
  // Step 1: Collect all paths that need signed URLs
  const conceptPaths: { path: string, type: 'concept' | 'palette', conceptIndex: number, variationIndex?: number }[] = [];
  
  // Collect all image paths first
  concepts.forEach((concept, conceptIndex) => {
    // Add concept image if needed
    if (concept.image_path && (!concept.image_url || !concept.image_url.includes('token='))) {
      conceptPaths.push({ 
        path: concept.image_path, 
        type: 'concept', 
        conceptIndex 
      });
    }
    
    // Add variation images if needed
    concept.color_variations?.forEach((variation, variationIndex) => {
      if (variation.image_path && (!variation.image_url || !variation.image_url.includes('token='))) {
        conceptPaths.push({ 
          path: variation.image_path, 
          type: 'palette', 
          conceptIndex,
          variationIndex 
        });
      }
    });
  });
  
  console.log(`[batchProcessUrls] Found ${conceptPaths.length} images needing signed URLs`);
  
  // Step 2: Get signed URLs in batch operations
  const conceptBucket = getBucketName('concept');
  const paletteBucket = getBucketName('palette');
  
  // Process concept images
  const conceptImages = conceptPaths.filter(p => p.type === 'concept');
  if (conceptImages.length) {
    console.log(`[batchProcessUrls] Requesting ${conceptImages.length} signed concept URLs`);
    try {
      // Batch request signed URLs for concept images
      const { data: conceptUrlsData } = await supabase.storage
        .from(conceptBucket)
        .createSignedUrls(
          conceptImages.map(p => p.path),
          3600 // 1 hour expiration
        );
      
      // Apply the signed URLs
      if (conceptUrlsData) {
        console.log(`[batchProcessUrls] Successfully got ${conceptUrlsData.length} concept signed URLs`);
        conceptUrlsData.forEach((signedUrl, i) => {
          const { conceptIndex } = conceptImages[i];
          if (signedUrl.signedUrl) {
            concepts[conceptIndex].image_url = signedUrl.signedUrl;
            // For backward compatibility
            concepts[conceptIndex].base_image_url = signedUrl.signedUrl;
          }
        });
      }
    } catch (error) {
      console.error('[batchProcessUrls] Error getting batch signed URLs for concepts:', error);
      // Fall back to individual URL generation
      conceptImages.forEach(({ path, conceptIndex }) => {
        try {
          const url = getSignedImageUrl(path, 'concept');
          concepts[conceptIndex].image_url = url;
          concepts[conceptIndex].base_image_url = url;
        } catch (e) {
          console.error(`[batchProcessUrls] Error generating fallback URL for ${path}:`, e);
        }
      });
    }
  }
  
  // Process palette variation images
  const paletteImages = conceptPaths.filter(p => p.type === 'palette');
  if (paletteImages.length) {
    console.log(`[batchProcessUrls] Requesting ${paletteImages.length} signed palette URLs`);
    try {
      // Batch request signed URLs for palette images
      const { data: paletteUrlsData } = await supabase.storage
        .from(paletteBucket)
        .createSignedUrls(
          paletteImages.map(p => p.path),
          3600 // 1 hour expiration
        );
      
      // Apply the signed URLs
      if (paletteUrlsData) {
        console.log(`[batchProcessUrls] Successfully got ${paletteUrlsData.length} palette signed URLs`);
        paletteUrlsData.forEach((signedUrl, i) => {
          const { conceptIndex, variationIndex } = paletteImages[i];
          if (signedUrl.signedUrl && typeof variationIndex === 'number' && concepts[conceptIndex].color_variations) {
            concepts[conceptIndex].color_variations![variationIndex].image_url = signedUrl.signedUrl;
          }
        });
      }
    } catch (error) {
      console.error('[batchProcessUrls] Error getting batch signed URLs for palettes:', error);
      // Fall back to individual URL generation
      paletteImages.forEach(({ path, conceptIndex, variationIndex }) => {
        try {
          if (typeof variationIndex === 'number' && concepts[conceptIndex].color_variations) {
            const url = getSignedImageUrl(path, 'palette');
            concepts[conceptIndex].color_variations![variationIndex].image_url = url;
          }
        } catch (e) {
          console.error(`[batchProcessUrls] Error generating fallback URL for ${path}:`, e);
        }
      });
    }
  }
  
  console.log(`[batchProcessUrls] Completed batch processing ${concepts.length} concepts`);
  return concepts;
} 