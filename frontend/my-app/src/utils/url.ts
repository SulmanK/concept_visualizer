/**
 * URL utility functions
 */
import { logger } from './logger';

/**
 * Extract the storage path from a URL
 * This function extracts the storage path from a Supabase URL
 * 
 * @param url The URL to extract the storage path from
 * @returns The storage path or null if not found
 */
export function extractStoragePathFromUrl(url: string | undefined): string | null {
  if (!url) return null;
  
  logger.debug('Extracting storage path from URL:', url);
  
  try {
    // Format: https://[project-id].supabase.co/storage/v1/object/public/concept-images/[user-id]/[image-id].png
    // Or: https://[project-id].supabase.co/storage/v1/object/sign/palette-images/[user-id]/[image-id].png
    const urlObj = new URL(url);
    
    // Check if it's a storage URL (public, authenticated, or signed)
    if (
      urlObj.pathname.includes('/storage/v1/object/public/') ||
      urlObj.pathname.includes('/storage/v1/object/authenticated/') ||
      urlObj.pathname.includes('/storage/v1/object/sign/')
    ) {
      // Try to get the path after 'concept-images/'
      let parts = urlObj.pathname.split('concept-images/');
      if (parts.length > 1) {
        logger.debug('Extracted storage path (concept-images):', parts[1]);
        return parts[1]; // This should be user-id/image-id.png
      }
      
      // Try to get the path after 'palette-images/'
      parts = urlObj.pathname.split('palette-images/');
      if (parts.length > 1) {
        logger.debug('Extracted storage path (palette-images):', parts[1]);
        return parts[1]; // This should be user-id/image-id.png
      }
      
      // Look for the URL parameter for signed URLs
      if (urlObj.pathname.includes('/storage/v1/object/sign/')) {
        const urlParam = urlObj.searchParams.get('url');
        if (urlParam) {
          logger.debug('Found URL parameter in signed URL:', urlParam);
          // The URL parameter contains the path within the bucket
          // Format is usually: bucket-name/user-id/image-id.png
          // We just need the user-id/image-id.png part
          
          // Try to get the part after the bucket name
          const bucketParts = urlParam.split('/');
          if (bucketParts.length > 1) {
            const path = bucketParts.slice(1).join('/');
            logger.debug('Extracted storage path from signed URL param:', path);
            return path;
          }
        }
      }
    }
    
    // Check for direct storage paths
    if (url.includes('/')) {
      // Try to find a pattern like [user-id]/[image-id].png
      const matches = url.match(/([a-f0-9-]+\/[a-f0-9-]+\.[a-z]+)(\?.*)?$/i);
      if (matches && matches[1]) {
        logger.debug('Extracted storage path (pattern match):', matches[1]);
        return matches[1];
      }
    }
    
    // If we couldn't extract a path, return null
    logger.debug('Could not extract storage path from URL');
    return null;
  } catch (error) {
    logger.error('Error extracting storage path from URL:', error);
    return null;
  }
} 