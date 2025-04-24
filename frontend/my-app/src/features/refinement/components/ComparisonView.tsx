import React, { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useConceptDetail } from "../../../hooks/useConceptQueries";
import { Card } from "../../../components/ui";
import { SkeletonLoader } from "../../../components/ui";
import { ConceptResult } from "../../../components/concept";
import { OptimizedImage } from "../../../components/ui";

interface ComparisonViewProps {
  originalImageUrl: string;
  refinedConceptId: string;
  onColorSelect?: (color: string) => void;
  selectedColor?: string | null;
}

/**
 * Displays a comparison between the original and refined concept
 */
export const ComparisonView: React.FC<ComparisonViewProps> = ({
  originalImageUrl,
  refinedConceptId,
  onColorSelect = () => {}, // Default to empty function
  selectedColor = null,
}) => {
  const navigate = useNavigate();

  // Fetch the refined concept using its ID
  const {
    data: refinedConcept,
    isLoading,
    error,
  } = useConceptDetail(refinedConceptId);

  // Handle export button click
  const handleExport = useCallback(() => {
    console.log("Export clicked for:", refinedConceptId);
    // Implementation would go here
  }, [refinedConceptId]);

  // Handle view details button click
  const handleViewDetails = useCallback(() => {
    if (refinedConcept?.id) {
      navigate(`/concepts/${refinedConcept.id}`);
    }
  }, [navigate, refinedConcept?.id]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h2 className="text-xl font-semibold text-indigo-900 mb-4">
          Comparing Results
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SkeletonLoader type="image" height="250px" />
          <SkeletonLoader type="image" height="250px" />
        </div>
      </div>
    );
  }

  if (error || !refinedConcept) {
    return (
      <Card className="p-6 text-center">
        <h2 className="text-xl font-semibold text-red-600 mb-4">
          Error Loading Refined Concept
        </h2>
        <p className="text-indigo-700 mb-6">
          We encountered an error while loading the refined concept.
        </p>
        <button
          onClick={() => navigate("/")}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg"
        >
          Return Home
        </button>
      </Card>
    );
  }

  return (
    <>
      {/* Comparison view */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Original concept */}
        <div>
          <h2 className="text-xl font-semibold text-indigo-900 mb-4">
            Original
          </h2>
          <div className="border border-indigo-100 rounded-lg overflow-hidden shadow-md">
            <OptimizedImage
              src={originalImageUrl}
              alt="Original concept"
              className="w-full h-auto"
              lazy={true}
              width="100%"
              height="auto"
              backgroundColor="#f3f4f6"
            />
          </div>
        </div>

        {/* Refined concept */}
        <div>
          <h2 className="text-xl font-semibold text-indigo-900 mb-4">
            Refined
          </h2>
          <div className="border border-indigo-100 rounded-lg overflow-hidden shadow-md">
            <OptimizedImage
              src={refinedConcept.image_url}
              alt="Refined concept"
              className="w-full h-auto"
              lazy={true}
              width="100%"
              height="auto"
              backgroundColor="#f3f4f6"
            />
          </div>
        </div>
      </div>

      {/* Result details */}
      <div className="mt-8">
        <ConceptResult
          concept={refinedConcept}
          onColorSelect={onColorSelect}
          selectedColor={selectedColor}
          variations={refinedConcept.variations || []}
          onViewDetails={handleViewDetails}
          onExport={handleExport}
        />
      </div>

      {/* Selected color feedback */}
      {selectedColor && (
        <div className="mt-4 text-center text-sm text-indigo-600">
          <span className="bg-indigo-50 px-2 py-1 rounded font-mono">
            {selectedColor}
          </span>
          <span className="ml-2">copied to clipboard</span>
        </div>
      )}
    </>
  );
};
