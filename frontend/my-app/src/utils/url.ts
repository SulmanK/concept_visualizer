/**
 * URL utility functions
 */

/**
 * Extract the storage path from a URL
 * This function extracts the storage path from a Supabase URL
 * 
 * @param url The URL to extract the storage path from
 * @returns The storage path or null if not found
 */
export function extractStoragePathFromUrl(url: string | undefined): string | null {
  if (!url) return null;
  
  try {
    // Format: https://[project-id].supabase.co/storage/v1/object/public/concept-images/[user-id]/[image-id].png
    const urlObj = new URL(url);
    
    // Check if it's a storage URL
    if (
      urlObj.pathname.includes('/storage/v1/object/public/') ||
      urlObj.pathname.includes('/storage/v1/object/authenticated/')
    ) {
      // Get the path after 'concept-images/'
      const parts = urlObj.pathname.split('concept-images/');
      if (parts.length > 1) {
        return parts[1]; // This should be user-id/image-id.png
      }
    }
    
    // Check for direct storage paths
    if (url.includes('/')) {
      // Try to find a pattern like [user-id]/[image-id].png
      const matches = url.match(/([a-f0-9-]+\/[a-f0-9-]+\.[a-z]+)(\?.*)?$/i);
      if (matches && matches[1]) {
        return matches[1];
      }
    }
    
    // If we couldn't extract a path, return null
    return null;
  } catch (error) {
    console.error('Error extracting storage path from URL:', error);
    return null;
  }
} 