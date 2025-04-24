import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useRecentConcepts } from "../../hooks/useConceptQueries";
import { ConceptData, ColorVariationData } from "../../services/supabaseClient";
import { useAuth } from "../../contexts/AuthContext";
import { useQueryClient } from "@tanstack/react-query";
import { OptimizedImage } from "../../components/ui/OptimizedImage";

/**
 * Helper function to determine if a color is light
 * @param hexColor - Hex color string
 * @returns boolean - True if color is light
 */
const isLightColor = (hexColor: string): boolean => {
  // Default to false for non-hex colors
  if (!hexColor || !hexColor.startsWith("#")) {
    return false;
  }

  // Convert hex to RGB
  let r = 0,
    g = 0,
    b = 0;
  if (hexColor.length === 7) {
    r = parseInt(hexColor.substring(1, 3), 16);
    g = parseInt(hexColor.substring(3, 5), 16);
    b = parseInt(hexColor.substring(5, 7), 16);
  } else if (hexColor.length === 4) {
    r = parseInt(hexColor.substring(1, 2), 16) * 17;
    g = parseInt(hexColor.substring(2, 3), 16) * 17;
    b = parseInt(hexColor.substring(3, 4), 16) * 17;
  }

  // Calculate perceived brightness (YIQ formula)
  const yiq = (r * 299 + g * 587 + b * 114) / 1000;
  return yiq >= 200; // Higher threshold to catch very light colors
};

/**
 * Page for selecting a concept to refine
 */
export const RefinementSelectionPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // Use React Query directly instead of the context
  const {
    data: recentConcepts = [],
    isLoading: loadingConcepts,
    error: errorLoadingConcepts,
    refetch: refetchConcepts,
  } = useRecentConcepts(user?.id, 10);

  const [expandedConceptId, setExpandedConceptId] = useState<string | null>(
    null,
  );
  const [selectedVariation, setSelectedVariation] = useState<{
    conceptId: string;
    variationId?: string;
    imageUrl: string;
    isOriginal: boolean;
  } | null>(null);

  // Function to refresh concepts
  const refreshConcepts = () => {
    // Both approaches work, but the second is sometimes more reliable
    refetchConcepts();
    queryClient.invalidateQueries({
      queryKey: ["concepts", "recent", user?.id],
    });
  };

  // Fetch concepts on component mount
  useEffect(() => {
    refreshConcepts();
    // We intentionally exclude refreshConcepts from the dependency array
    // to prevent an infinite loop
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Handle selecting a concept to refine
  const handleSelectConcept = (
    conceptId: string,
    colorVariationId?: string,
  ) => {
    if (colorVariationId) {
      navigate(`/refine/${conceptId}?colorId=${colorVariationId}`);
    } else {
      navigate(`/refine/${conceptId}`);
    }
  };

  // Toggle expanded state of a concept to show its variations
  const toggleExpandConcept = (conceptId: string) => {
    setExpandedConceptId(expandedConceptId === conceptId ? null : conceptId);
  };

  // Handle selecting a variation or original image
  const handleSelectVariation = (
    conceptId: string,
    imageUrl: string,
    isOriginal: boolean,
    variationId?: string,
  ) => {
    setSelectedVariation({
      conceptId,
      variationId,
      imageUrl,
      isOriginal,
    });
  };

  // Handle refining the selected variation
  const handleRefineSelected = () => {
    if (!selectedVariation) return;

    if (selectedVariation.variationId && !selectedVariation.isOriginal) {
      navigate(
        `/refine/${selectedVariation.conceptId}?colorId=${selectedVariation.variationId}`,
      );
    } else {
      navigate(`/refine/${selectedVariation.conceptId}`);
    }
  };

  // Handle loading state
  if (loadingConcepts) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-indigo-50 to-white">
        <main className="container mx-auto px-4 py-8 space-y-12">
          <div className="text-center py-8">
            <h1 className="text-4xl sm:text-5xl font-bold text-indigo-900 mb-4">
              Select a Concept to Refine
            </h1>
            <p className="text-indigo-700 text-lg sm:text-xl leading-relaxed max-w-3xl mx-auto">
              Choose one of your concepts to refine and improve.
            </p>
          </div>

          <div
            className="bg-white shadow-md p-8 text-center rounded-xl"
            data-testid="loading-skeleton"
          >
            <div className="animate-pulse">
              <div className="h-8 bg-indigo-200 rounded w-1/3 mb-8 mx-auto"></div>
              <div className="grid grid-cols-1 gap-8">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-32 bg-indigo-100 rounded-lg"></div>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  // Handle error state
  if (errorLoadingConcepts) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-indigo-50 to-white">
        <main className="container mx-auto px-4 py-8 space-y-12">
          <div className="text-center py-8">
            <h1 className="text-4xl sm:text-5xl font-bold text-indigo-900 mb-4">
              Select a Concept to Refine
            </h1>
            <p className="text-indigo-700 text-lg sm:text-xl leading-relaxed max-w-3xl mx-auto">
              Choose one of your concepts to refine and improve.
            </p>
          </div>

          <div className="bg-white shadow-md p-8 text-center rounded-xl">
            <h2 className="text-xl font-semibold text-red-600 mb-4">Error</h2>
            <p className="text-indigo-600 mb-6">
              {String(errorLoadingConcepts)}
            </p>
            <button
              onClick={() => refreshConcepts()}
              className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-full"
            >
              Try Again
            </button>
          </div>
        </main>
      </div>
    );
  }

  // Handle empty state
  if (!recentConcepts || recentConcepts.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-indigo-50 to-white">
        <main className="container mx-auto px-4 py-8 space-y-12">
          <div className="text-center py-8">
            <h1 className="text-4xl sm:text-5xl font-bold text-indigo-900 mb-4">
              Select a Concept to Refine
            </h1>
            <p className="text-indigo-700 text-lg sm:text-xl leading-relaxed max-w-3xl mx-auto">
              Choose one of your concepts to refine and improve.
            </p>
          </div>

          <div className="bg-white shadow-md p-8 text-center rounded-xl">
            <h2 className="text-xl font-semibold text-indigo-800 mb-4">
              No Concepts Available
            </h2>
            <p className="text-indigo-600 mb-6">
              You need to create concepts before you can refine them.
            </p>
            <button
              onClick={() => navigate("/create")}
              className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-full"
            >
              Create New Concept
            </button>
          </div>
        </main>
      </div>
    );
  }

  // Render a concept row with its variations
  const renderConceptRow = (concept: ConceptData) => {
    const isExpanded = expandedConceptId === concept.id;
    const hasVariations =
      concept.color_variations && concept.color_variations.length > 0;
    const totalVariations = hasVariations
      ? concept.color_variations!.length + 1
      : 1; // +1 for original

    // Check if this concept has a selected variation
    const hasSelectedVariation =
      selectedVariation && selectedVariation.conceptId === concept.id;

    // Check if original is selected for this concept
    const isOriginalSelected =
      hasSelectedVariation && selectedVariation.isOriginal;

    return (
      <div key={concept.id} className="mb-6">
        <div
          className={`bg-white p-4 rounded-lg shadow-sm border border-indigo-100 transition-all ${
            isExpanded
              ? "shadow-md border-indigo-300"
              : "hover:shadow-md hover:border-indigo-200"
          }`}
        >
          {/* Main concept row */}
          <div
            className="flex items-center cursor-pointer"
            onClick={() => toggleExpandConcept(concept.id)}
          >
            <div className="w-24 h-24 flex-shrink-0 rounded-md overflow-hidden border border-indigo-100">
              <OptimizedImage
                src={
                  concept.image_url ||
                  concept.base_image_url ||
                  "/placeholder-image.png"
                }
                alt={concept.logo_description || "Concept"}
                className="w-full h-full object-cover"
                lazy={true}
                width="100%"
                height="100%"
                objectFit="cover"
                backgroundColor="#f3f4f6"
              />
            </div>
            <div className="ml-6 flex-grow">
              <h3 className="font-semibold text-lg text-indigo-900 mb-1">
                {concept.logo_description}
              </h3>
              <p className="text-sm text-gray-600 mb-2 line-clamp-1">
                {concept.theme_description}
              </p>
              <div className="flex items-center">
                <span className="text-xs font-medium text-indigo-600 mr-2">
                  {totalVariations}{" "}
                  {totalVariations === 1 ? "option" : "options"}
                </span>
                <div className="flex space-x-1">
                  {/* Original color option */}
                  <div className="w-4 h-4 rounded-full border border-gray-300 flex items-center justify-center bg-white">
                    <span className="text-[8px] font-bold text-gray-600">
                      O
                    </span>
                  </div>

                  {/* Color variations */}
                  {hasVariations &&
                    concept.color_variations
                      ?.slice(0, 3)
                      .map((variation, idx) => {
                        const color = variation.colors[0] || "#4F46E5";
                        const isLight = isLightColor(color);

                        return (
                          <div
                            key={idx}
                            className={`w-4 h-4 rounded-full ${
                              isLight ? "border-2 border-gray-400" : ""
                            }`}
                            style={{ backgroundColor: color }}
                          />
                        );
                      })}
                  {hasVariations && concept.color_variations!.length > 3 && (
                    <div className="w-4 h-4 rounded-full bg-gray-200 flex items-center justify-center text-[8px] font-medium text-gray-700">
                      +{concept.color_variations!.length - 3}
                    </div>
                  )}
                </div>
              </div>
            </div>
            <div className="ml-4">
              <button
                className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-full hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                onClick={(e) => {
                  e.stopPropagation();
                  handleSelectConcept(concept.id);
                }}
                data-testid={`concept-card-${concept.id}`}
              >
                Refine
              </button>
            </div>
          </div>

          {/* Expanded section with variations */}
          {isExpanded && (
            <div className="mt-4 pt-4 border-t border-indigo-100">
              <div className="font-medium text-sm text-indigo-900 mb-3">
                Select a variation to refine:
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {/* Original image option */}
                <div
                  className={`cursor-pointer rounded-md overflow-hidden h-28 border-2 ${
                    isOriginalSelected
                      ? "border-indigo-500 shadow-md"
                      : "border-transparent hover:border-indigo-300"
                  }`}
                  onClick={() =>
                    handleSelectVariation(
                      concept.id,
                      concept.image_url || concept.base_image_url,
                      true,
                    )
                  }
                >
                  <div className="h-full relative">
                    <OptimizedImage
                      src={
                        concept.image_url ||
                        concept.base_image_url ||
                        "/placeholder-image.png"
                      }
                      alt="Original concept"
                      className="w-full h-full object-cover"
                      lazy={true}
                      width="100%"
                      height="100%"
                      objectFit="cover"
                      backgroundColor="#f3f4f6"
                    />
                    <div className="absolute bottom-0 left-0 right-0 px-2 py-1 bg-indigo-900/70">
                      <div className="text-white text-xs font-medium truncate">
                        Original
                      </div>
                    </div>
                  </div>
                </div>

                {/* Variation options */}
                {hasVariations &&
                  concept.color_variations?.map((variation, idx) => {
                    const isVariationSelected =
                      hasSelectedVariation &&
                      !selectedVariation.isOriginal &&
                      selectedVariation.variationId === variation.id;

                    return (
                      <div
                        key={idx}
                        className={`cursor-pointer rounded-md overflow-hidden h-28 border-2 ${
                          isVariationSelected
                            ? "border-indigo-500 shadow-md"
                            : "border-transparent hover:border-indigo-300"
                        }`}
                        onClick={() =>
                          handleSelectVariation(
                            concept.id,
                            variation.image_url,
                            false,
                            variation.id,
                          )
                        }
                      >
                        <div className="h-full relative">
                          <OptimizedImage
                            src={
                              variation.image_url || "/placeholder-image.png"
                            }
                            alt={`Color variation ${idx + 1}`}
                            className="w-full h-full object-cover"
                            lazy={true}
                            width="100%"
                            height="100%"
                            objectFit="cover"
                            backgroundColor="#f3f4f6"
                          />
                          <div
                            className="absolute bottom-0 left-0 right-0 px-2 py-1"
                            style={{
                              backgroundColor: variation.colors[0] || "#4F46E5",
                            }}
                          >
                            <div
                              className="truncate max-w-full px-1 text-xs font-medium"
                              style={{
                                color: isLightColor(
                                  variation.colors[0] || "#4F46E5",
                                )
                                  ? "#374151"
                                  : "white",
                              }}
                            >
                              {variation.palette_name || `Variation ${idx + 1}`}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
              </div>

              <div className="mt-4 flex justify-end space-x-3">
                {hasSelectedVariation &&
                  selectedVariation.conceptId === concept.id && (
                    <button
                      onClick={handleRefineSelected}
                      className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-indigo-400 text-white rounded-full text-sm shadow-md hover:shadow-lg transform transition-transform hover:scale-105"
                    >
                      Refine Selected
                    </button>
                  )}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-50 to-white">
      <main className="container mx-auto px-4 py-8 space-y-12">
        <div className="text-center py-8">
          <h1 className="text-4xl sm:text-5xl font-bold text-indigo-900 mb-4">
            Select a Concept to Refine
          </h1>
          <p className="text-indigo-700 text-lg sm:text-xl leading-relaxed max-w-3xl mx-auto">
            Choose one of your concepts to refine and improve.
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="mb-6 pb-4 border-b border-indigo-100 flex items-center">
            <h2 className="font-semibold text-xl text-indigo-900 flex-grow">
              Your Recent Concepts
            </h2>
            <div className="flex space-x-2">
              <button
                onClick={refreshConcepts}
                className="px-3 py-1 text-indigo-600 border border-indigo-300 rounded-full text-sm hover:bg-indigo-50 transition-colors"
                title="Refresh concepts"
              >
                Refresh
              </button>
              <button
                onClick={() => navigate("/create")}
                className="px-3 py-1 bg-indigo-600 text-white rounded-full text-sm hover:bg-indigo-700 transition-colors"
                title="Create new concept"
              >
                Create New
              </button>
            </div>
          </div>

          {selectedVariation && (
            <div className="mb-6 p-4 bg-indigo-50 rounded-lg flex flex-col sm:flex-row items-center sm:items-start">
              <div className="w-32 h-32 rounded-md overflow-hidden border border-indigo-200 mb-4 sm:mb-0 sm:mr-6 flex-shrink-0">
                <OptimizedImage
                  src={selectedVariation?.imageUrl || "/placeholder-image.png"}
                  alt="Selected concept"
                  className="w-full h-full object-cover"
                  lazy={true}
                  width="100%"
                  height="100%"
                  objectFit="cover"
                  backgroundColor="#f3f4f6"
                />
              </div>
              <div className="flex-grow text-center sm:text-left">
                <h3 className="font-semibold text-lg text-indigo-900 mb-2">
                  Selected Concept
                </h3>
                <p className="text-indigo-700 mb-4">
                  {selectedVariation.isOriginal
                    ? "Original Design"
                    : "Color Variation"}
                </p>
                <button
                  onClick={handleRefineSelected}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-full text-sm hover:bg-indigo-700 transition-colors"
                >
                  Start Refining This Concept
                </button>
              </div>
            </div>
          )}

          {recentConcepts.map(renderConceptRow)}
        </div>
      </main>
    </div>
  );
};
