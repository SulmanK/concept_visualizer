import React from "react";
import { ConceptCard } from "../../../components/ui/ConceptCard";
import { SkeletonLoader } from "../../../components/ui/SkeletonLoader";
import { Link } from "react-router-dom";
import { ConceptData } from "../../../services/supabaseClient";
import { useErrorHandling } from "../../../hooks/useErrorHandling";
import { createAsyncErrorHandler } from "../../../utils/errorUtils";

interface RecentConceptsSectionProps {
  concepts: Array<ConceptData>;
  onEdit: (conceptId: string, variationId?: string | null) => void;
  onViewDetails: (conceptId: string, variationId?: string | null) => void;
  isLoading?: boolean;
}

/**
 * Helper function to adapt Concept data for the UI ConceptCard
 * with additional safety checks to prevent errors
 */
function adaptConceptForUiCard(
  concept: ConceptData,
  errorHandler: ReturnType<typeof useErrorHandling>,
) {
  const handleAsyncError = createAsyncErrorHandler(errorHandler, {
    defaultErrorMessage: "Error processing concept data",
    context: "adaptConceptForUiCard",
  });

  if (!concept) {
    console.warn("Received null or undefined concept in adaptConceptForUiCard");
    // Return default data if concept is null or undefined
    return {
      title: "Missing Concept",
      description: "No data available",
      colorVariations: [["#4F46E5", "#60A5FA", "#1E293B"]],
      initials: "NA",
      includeOriginal: false,
      gradient: { from: "blue-400", to: "indigo-500" },
      colorData: [],
      id: "missing",
    };
  }

  try {
    // Log the raw concept data with color_variations
    console.log(`[adaptConceptForUiCard] Processing concept ${concept.id}`);
    console.log(
      `[adaptConceptForUiCard] Has color_variations: ${!!concept.color_variations}`,
    );
    if (concept.color_variations) {
      console.log(
        `[adaptConceptForUiCard] Number of variations: ${concept.color_variations.length}`,
      );
      concept.color_variations.slice(0, 2).forEach((variation, i) => {
        console.log(
          `[adaptConceptForUiCard] - Variation ${i + 1}: ID ${
            variation.id
          }, Color count: ${
            variation.colors.length
          }, Image URL exists: ${!!variation.image_url}`,
        );
      });
    }

    // Get initials from the logo description (with safety checks)
    const logoDescription = concept.logo_description || "Untitled";
    const words = logoDescription.trim().split(/\s+/);
    const initials =
      words.length === 1
        ? words[0].substring(0, 2).toUpperCase()
        : (words[0][0] + (words.length > 1 ? words[1][0] : "")).toUpperCase();

    // Create colorData for mapping indices to variation IDs
    const colorData = (concept.color_variations || []).map((variation) => ({
      id: variation.id,
      colors: Array.isArray(variation.colors) ? variation.colors : ["#4F46E5"],
    }));

    // Check if the concept has a valid image_url
    const hasOriginalImage = !!concept.image_url || !!concept.base_image_url;

    // Log the adapted data
    console.log(`[adaptConceptForUiCard] Adapted concept ${concept.id}:`, {
      colorDataCount: colorData.length,
      hasOriginalImage,
    });

    return {
      initials,
      colorData,
      id: concept.id,
    };
  } catch (error) {
    console.error("Error in adaptConceptForUiCard:", error);

    // Use standardized error handling
    handleAsyncError(() => Promise.reject(error), "concept-adaptation");

    // Return a safe fallback on error
    return {
      title: "Error Processing Concept",
      description: "An error occurred while processing this concept",
      colorVariations: [["#4F46E5", "#60A5FA", "#1E293B"]],
      initials: "ER",
      includeOriginal: false,
      gradient: { from: "red-400", to: "red-600" },
      colorData: [],
      id: concept?.id || "error",
    };
  }
}

/**
 * Recent concepts section showing previously created concepts
 * Optimized for responsive viewing on mobile and desktop
 * Uses direct ConceptCards like in ConceptList
 */
export const RecentConceptsSection: React.FC<RecentConceptsSectionProps> = ({
  concepts,
  onEdit,
  onViewDetails,
  isLoading = false,
}) => {
  // Move the useErrorHandling hook to the component level
  const errorHandler = useErrorHandling();

  // If there are no concepts and not loading, don't render the section
  if (!concepts || (concepts.length === 0 && !isLoading)) {
    return null;
  }

  // Render skeleton cards when loading
  const renderSkeletonCards = () => {
    return Array.from({ length: 3 }).map((_, index) => (
      <div key={`skeleton-${index}`} className="h-full">
        <SkeletonLoader type="card" height="360px" className="rounded-xl" />
      </div>
    ));
  };

  // Handle click on edit button
  const handleEdit = (conceptId: string, variationId?: string | null) => {
    console.log("[RecentConceptsSection] Edit clicked:", {
      conceptId,
      variationId,
    });
    onEdit(conceptId, variationId);
  };

  // Handle click on view details button
  const handleViewDetails = (
    conceptId: string,
    variationId?: string | null,
  ) => {
    console.log("[RecentConceptsSection] View details clicked:", {
      conceptId,
      variationId,
    });
    onViewDetails(conceptId, variationId);
  };

  return (
    <div className="mt-10 sm:mt-16 mb-8 sm:mb-12">
      <div className="bg-white shadow-lg border border-indigo-100 p-4 sm:p-6 md:p-8 relative overflow-hidden rounded-xl">
        {/* Enhanced gradient background accents - removed for consistency with form */}

        <div className="relative z-10">
          {/* Header with view all link */}
          <div className="flex justify-between items-center mb-4 sm:mb-8">
            <h2 className="text-xl sm:text-2xl font-bold text-indigo-900 flex items-center">
              {isLoading ? "Loading Recent Concepts..." : "Recent Concepts"}
              <span className="ml-2 text-xs py-1 px-2 bg-indigo-100 text-indigo-700 rounded-full">
                Gallery
              </span>
            </h2>
            <Link
              to="/recent"
              className="text-indigo-600 hover:text-indigo-800 transition-colors text-sm font-medium flex items-center"
            >
              <span className="mr-1">View All</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </Link>
          </div>

          {/* Grid with responsive columns */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 md:gap-8">
            {isLoading
              ? renderSkeletonCards()
              : concepts.map((concept) => {
                  // Adapt the concept for the UI card using our helper function, passing errorHandler
                  const adaptedProps = adaptConceptForUiCard(
                    concept,
                    errorHandler,
                  );

                  // Check if sample concept (using direct image) or normal concept
                  const isSampleConcept = concept.id.startsWith("sample-");
                  const sampleImageUrl = isSampleConcept
                    ? concept.image_url
                    : undefined;

                  return (
                    <div key={concept.id} className="h-full">
                      <ConceptCard
                        concept={concept}
                        initials={adaptedProps.initials}
                        sampleImageUrl={sampleImageUrl}
                        editButtonText="Refine"
                        includeOriginal={true}
                        onEdit={(index: number) => {
                          // Map the index to a variation ID
                          let variationId = null;

                          if (
                            index > 0 &&
                            adaptedProps.colorData &&
                            index - 1 < adaptedProps.colorData.length
                          ) {
                            variationId = adaptedProps.colorData[index - 1].id;
                          }

                          handleEdit(concept.id, variationId);
                        }}
                        onViewDetails={(index: number) => {
                          // Map the index to a variation ID
                          let variationId = null;

                          if (
                            index > 0 &&
                            adaptedProps.colorData &&
                            index - 1 < adaptedProps.colorData.length
                          ) {
                            variationId = adaptedProps.colorData[index - 1].id;
                          }

                          handleViewDetails(concept.id, variationId);
                        }}
                      />
                    </div>
                  );
                })}
          </div>
        </div>
      </div>
    </div>
  );
};
