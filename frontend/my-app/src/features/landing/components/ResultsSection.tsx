import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { ConceptData } from '../../../services/supabaseClient';
import { SkeletonLoader } from '../../../components/ui/SkeletonLoader';
import { Button } from '../../../components/ui/Button';

interface ResultsSectionProps {
  conceptId: string;
  conceptData?: ConceptData | null;
  isLoading?: boolean;
  onExportSelected: (conceptId: string, variationId?: string | null) => void;
  onStartOver?: () => void;
}

/**
 * Results section showing the generated concept and its variations in a grid.
 * Optimized for both mobile and desktop viewing
 */
export const ResultsSection: React.FC<ResultsSectionProps> = ({
  conceptId,
  conceptData,
  isLoading = false,
  onExportSelected,
  onStartOver
}) => {
  // State to track the index of the selected variation (0 for original, 1+ for variations)
  const [selectedIndex, setSelectedIndex] = useState<number>(0);

  // Reset selection when concept data changes
  useEffect(() => {
    setSelectedIndex(0);
  }, [conceptData?.id]);

  // Create a combined array of the original image and variations for easier mapping
  const displayItems = useMemo(() => {
    if (!conceptData) return [];

    const items = [];
    
    // Add original concept image if available
    if (conceptData.image_url || conceptData.base_image_url) {
      // Get colors from the first color variation if available
      const originalColors = conceptData.color_variations?.[0]?.colors || [];
      
      items.push({
        id: 'original', // Special ID for the original
        name: 'Original',
        imageUrl: conceptData.image_url || conceptData.base_image_url || '',
        colors: Array.isArray(originalColors) ? originalColors : [],
      });
    }

    // Try color_variations as the primary source of variations
    const variationsData = conceptData.color_variations || [];
    
    // Use only array data
    const variations = Array.isArray(variationsData) ? variationsData : [];
    
    // Add variations
    variations.forEach((variation, index) => {
      if (!variation) return; // Skip if variation is null or undefined
      
      const variationColors = Array.isArray(variation.colors) 
        ? variation.colors 
        : [];
      
      items.push({
        id: variation.id || `variation-${index}`,
        name: variation.palette_name || `Variation ${index + 1}`,
        imageUrl: variation.image_url || '',
        colors: variationColors,
      });
    });

    return items;
  }, [conceptData]);

  const handleExportClick = useCallback(() => {
    if (!conceptData || selectedIndex < 0 || selectedIndex >= displayItems.length) {
      return;
    }

    const selectedItem = displayItems[selectedIndex];
    const variationId = selectedItem.id === 'original' ? null : selectedItem.id;

    onExportSelected(conceptId, variationId);
  }, [selectedIndex, displayItems, conceptId, conceptData, onExportSelected]);

  // Handle the Start Over button click
  const handleStartOver = useCallback(() => {
    if (onStartOver) {
      onStartOver();
    }
  }, [onStartOver]);

  // Render skeleton loader when loading
  if (isLoading) {
    return (
      <div className="mb-8 sm:mb-16">
        <div className="bg-white shadow-lg border border-indigo-100 p-4 sm:p-6 md:p-8 mb-4 sm:mb-8 relative overflow-hidden rounded-xl">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 sm:mb-6">
            <h2 className="text-lg sm:text-xl font-semibold text-indigo-900 mb-3 sm:mb-0">
              <SkeletonLoader type="text" width="180px" height="24px" />
            </h2>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <SkeletonLoader type="image" height="150px" className="mb-2" />
                <SkeletonLoader type="text" height="16px" width="80%" />
              </div>
            ))}
          </div>
          <div className="flex justify-end mt-6">
            <SkeletonLoader type="button" width="150px" height="40px" />
          </div>
        </div>
      </div>
    );
  }

  // Render nothing if no concept and not loading
  if (!conceptData && !isLoading) {
    return null;
  }

  return (
    <div className="mb-8 sm:mb-16">
      <div className="bg-white shadow-lg border border-indigo-100 p-4 sm:p-6 md:p-8 mb-4 sm:mb-8 relative overflow-hidden rounded-xl">
        <div className="relative z-10">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 sm:mb-6">
            <div className="flex items-center space-x-2">
              <h2 className="text-lg sm:text-xl font-semibold text-indigo-900">
                Generated Concept & Variations
              </h2>
              <span className="text-sm text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">
                {displayItems.length} {displayItems.length === 1 ? 'result' : 'results'}
              </span>
            </div>
            {onStartOver && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleStartOver}
                className="mt-2 sm:mt-0"
              >
                <svg className="w-4 h-4 mr-1" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M4 4V9H4.58152M19.9381 11C19.446 7.05369 16.0796 4 12 4C8.64262 4 5.76829 6.06817 4.58152 9M4.58152 9H9M20 20V15H19.4185M19.4185 15C18.2317 17.9318 15.3574 20 12 20C7.92038 20 4.55399 16.9463 4.06189 13M19.4185 15H15" 
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Start Over
              </Button>
            )}
          </div>
          
          {/* Grid for images */}
          {displayItems.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 sm:gap-4">
              {displayItems.map((item, index) => (
                <div
                  key={item.id}
                  className={`
                    border-2 rounded-lg overflow-hidden cursor-pointer transition-all duration-200
                    hover:shadow-lg hover:border-indigo-500
                    ${selectedIndex === index ? 'border-indigo-500 ring-2 ring-indigo-200 shadow-lg' : 'border-indigo-100'}
                  `}
                  onClick={() => setSelectedIndex(index)}
                  title={`Select ${item.name}`}
                >
                  <div className="aspect-square bg-indigo-50 flex items-center justify-center p-2">
                    <img
                      src={item.imageUrl}
                      alt={`${item.name} variation`}
                      className="max-w-full max-h-full object-contain"
                      loading="lazy"
                    />
                  </div>
                  <div className="p-2 bg-white">
                    <p className="text-xs sm:text-sm font-medium text-indigo-800 text-center truncate">
                      {item.name}
                    </p>
                    {/* Mini color palette */}
                    <div className="flex justify-center mt-1 space-x-1">
                      {Array.isArray(item.colors) && item.colors.slice(0, 5).map((color, cIdx) => (
                        <div
                          key={cIdx}
                          className="w-2 h-2 rounded-full border border-gray-300"
                          style={{ backgroundColor: color }}
                          title={color}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-6 bg-indigo-50 rounded-lg">
              <p className="text-indigo-600">No variations available for this concept</p>
            </div>
          )}

          {/* Export Button */}
          <div className="flex justify-end mt-6">
            <Button
              variant="primary"
              size="md"
              onClick={handleExportClick}
              disabled={displayItems.length === 0}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export Selected
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}; 