import React, { useState, useEffect } from 'react';
import { getImageUrl } from '../../services/supabaseClient';

interface ConceptImageProps {
  path: string;
  isPalette?: boolean;
  alt: string;
  className?: string;
}

/**
 * Component for displaying concept images with signed URLs
 */
const ConceptImage: React.FC<ConceptImageProps> = ({ 
  path, 
  isPalette = false, 
  alt, 
  className 
}) => {
  const [imageUrl, setImageUrl] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    async function loadImageUrl() {
      if (!path) return;
      
      try {
        setIsLoading(true);
        
        // Get signed URL for the image
        const bucketType = isPalette ? 'palette' : 'concept';
        const signedUrl = await getImageUrl(path, bucketType);
        
        setImageUrl(signedUrl);
        setError(null);
      } catch (err) {
        console.error('Error getting image URL:', err);
        setError('Failed to load image');
      } finally {
        setIsLoading(false);
      }
    }
    
    loadImageUrl();
  }, [path, isPalette]);
  
  if (isLoading) {
    return <div className="image-placeholder">Loading...</div>;
  }
  
  if (error) {
    return <div className="image-error">{error}</div>;
  }
  
  return (
    <img 
      src={imageUrl} 
      alt={alt} 
      className={className}
      onError={(e) => {
        console.error('Error loading image:', path);
        setError('Failed to load image');
      }}
    />
  );
};

export default ConceptImage; 