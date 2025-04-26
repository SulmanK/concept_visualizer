import React, { useState, useEffect, useMemo } from "react";
import { Card } from "./Card";
import { ConceptData } from "../../services/supabaseClient";
import styles from "./ConceptCard.module.css";
import { OptimizedImage } from "./OptimizedImage";

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
 * Concept initials generator
 *
 * @param description The concept description
 * @returns Two-letter initials extracted from the description
 */
const getConceptInitials = (description: string): string => {
  const words = description.split(" ");
  if (words.length === 1) {
    return words[0].substring(0, 2).toUpperCase();
  }
  return (words[0][0] + words[1][0]).toUpperCase();
};

export interface ConceptCardProps {
  /**
   * Either provide a complete ConceptData object
   */
  concept?: ConceptData;

  /**
   * Or provide individual properties
   */

  /**
   * Concept title/name
   */
  title?: string;

  /**
   * Concept description
   */
  description?: string;

  /**
   * Colors to display in the palette
   * Each element represents a color variation with an array of colors
   */
  colorVariations?: string[][];

  /**
   * Images for each color variation, if available
   * If includeOriginal is true, the first image is considered the original
   */
  images?: string[];

  /**
   * Whether to include the original image as a variation option
   * If true, the first image in the images array is the original
   */
  includeOriginal?: boolean;

  /**
   * Gradient colors for the header (from and to)
   */
  gradient?: {
    from: string;
    to: string;
  };

  /**
   * Initials to display in the centered circle
   */
  initials?: string;

  /**
   * Handler for edit button click
   * Either version can be provided: simple index or with concept/variation IDs
   */
  onEdit?:
    | ((index: number) => void)
    | ((conceptId: string, variationId?: string | null) => void);

  /**
   * Handler for view details button click
   * Either version can be provided: simple index or with concept/variation IDs
   */
  onViewDetails?:
    | ((index: number) => void)
    | ((conceptId: string, variationId?: string | null) => void);

  /**
   * Text to display on the edit button (default: "Edit")
   */
  editButtonText?: string;

  /**
   * Direct image URL for sample concepts
   * This bypasses the Supabase storage processing
   */
  sampleImageUrl?: string;

  /**
   * Optional color variation data including IDs
   * This is used to map UI indices to backend variation IDs
   */
  variations?: Array<{
    id: string;
    colors: string[];
  }>;

  /** Prevents default navigation on card click */
  preventNavigation?: boolean;

  /** Callback when a specific color variation is clicked */
  onColorClick?: (variationId: string) => void;
}

/**
 * Card component for displaying concept previews
 */
export const ConceptCard: React.FC<ConceptCardProps> = ({
  concept,
  title,
  description,
  colorVariations,
  images,
  includeOriginal = false,
  initials,
  onEdit,
  onViewDetails,
  editButtonText = "Edit",
  sampleImageUrl,
  preventNavigation = false,
  onColorClick,
}) => {
  // State to track the selected color variation
  const [selectedVariationIndex, setSelectedVariationIndex] = useState(0);

  // DERIVED PROPS: Set derived values based on whether we're using concept data or direct props
  // These derived variables normalize the two input methods

  // Get the final title
  const finalTitle = concept?.logo_description || title || "Concept";

  // Get the final description
  const finalDescription = concept?.theme_description || description || "";

  // Get the final initials
  const finalInitials =
    initials ||
    (concept ? getConceptInitials(concept.logo_description || "") : "CV");

  // Get the final color variations
  const finalColorVariations = useMemo(() => {
    if (concept?.color_variations && concept.color_variations.length > 0) {
      // Log that we're using concept.color_variations
      console.log(
        `[ConceptCard] Using color_variations from concept: ${concept.id}`,
      );
      console.log(
        `[ConceptCard] Found ${concept.color_variations.length} color variations`,
      );
      concept.color_variations.slice(0, 2).forEach((variation, i) => {
        console.log(
          `[ConceptCard] - Variation ${i + 1}: ID ${variation.id}, Colors: ${
            variation.colors.length
          }`,
        );
      });
      return concept.color_variations.map((variation) => variation.colors);
    }

    // Log if we're using direct colorVariations prop
    if (colorVariations && colorVariations.length > 0) {
      console.log(
        `[ConceptCard] Using provided colorVariations prop: ${colorVariations.length} variations`,
      );
    } else {
      console.log(`[ConceptCard] No color variations found, using empty array`);
    }

    return colorVariations || [];
  }, [concept, colorVariations]);

  // Get the final images array
  const finalImages = useMemo(() => {
    if (concept) {
      if (concept.color_variations && concept.color_variations.length > 0) {
        // If we have variations, collect all image URLs
        const baseImage = concept.image_url || concept.base_image_url;
        const variationImages = concept.color_variations
          .map((v) => v.image_url)
          .filter(Boolean);

        // Log the images we found
        console.log(`[ConceptCard] Base image exists: ${!!baseImage}`);
        console.log(
          `[ConceptCard] Found ${variationImages.length} variation images`,
        );

        // If we have a base image, put it first
        return baseImage ? [baseImage, ...variationImages] : variationImages;
      } else if (concept.image_url) {
        // Just the base image if no variations
        console.log(`[ConceptCard] Only using base image, no variations`);
        return [concept.image_url];
      }
    }

    // Log if we're using direct images prop
    if (images && images.length > 0) {
      console.log(
        `[ConceptCard] Using provided images prop: ${images.length} images`,
      );
    } else {
      console.log(`[ConceptCard] No images found, using empty array`);
    }

    return images || [];
  }, [concept, images]);

  // Log the configuration - OPTIMIZED: only log when necessary data changes
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      // We'll use the existing hasVariations declaration later in the component
      const hasColorVariations = finalColorVariations.length > 0;
      console.log(`[ConceptCard] Configuration:`, {
        hasColorVariations,
        colorVariationsCount: finalColorVariations.length,
        imagesCount: finalImages.length,
        includeOriginal,
        selectedVariationIndex,
      });
    }
  }, [
    finalColorVariations,
    finalImages,
    includeOriginal,
    selectedVariationIndex,
  ]);

  // Add debug useEffect to track variation changes - OPTIMIZED: only log when necessary
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      console.log(
        `ConceptCard - Selected variation changed to: ${selectedVariationIndex}`,
      );

      // If we have a concept, log selected variation details
      if (concept?.color_variations) {
        // Get the actual color variation index (accounting for the Original option)
        const variationIndex = includeOriginal
          ? selectedVariationIndex - 1
          : selectedVariationIndex;

        // Log the selected variation details
        if (
          variationIndex >= 0 &&
          variationIndex < concept.color_variations.length
        ) {
          const variation = concept.color_variations[variationIndex];
          console.log(
            `ConceptCard - Selected variation: ${variation.id}, palette: ${variation.palette_name}`,
          );
        }
      }
    }
  }, [selectedVariationIndex, concept, includeOriginal]);

  // Log props for debugging - OPTIMIZED: only log in development and when props change
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      console.log(`ConceptCard - Props:`, {
        hasConceptObj: concept ? true : false,
        title: finalTitle,
        includeOriginal,
        hasImages: finalImages ? true : false,
        imagesCount: finalImages?.length || 0,
        variationsCount: finalColorVariations?.length || 0,
      });
    }
  }, [concept, finalTitle, includeOriginal, finalImages, finalColorVariations]);

  // Handle color variation selection
  const handleVariationSelect = (index: number, e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault(); // Prevent navigation when clicking on color circles
      e.stopPropagation(); // Prevent the card click from triggering
    }

    console.log(`ConceptCard - Selected variation index: ${index}`);
    setSelectedVariationIndex(index);

    // If onColorClick is provided and we have a concept object
    if (
      onColorClick &&
      concept?.color_variations &&
      index >= 0 &&
      index < concept.color_variations.length
    ) {
      const variationId = concept.color_variations[index].id;
      if (variationId) {
        console.log("Calling onColorClick with variation ID:", variationId);
        onColorClick(variationId);
      }
    }
  };

  // Determine the current image URL based on selected variation
  const logoImageUrl = useMemo(() => {
    // If sample image URL is provided, use it directly
    if (sampleImageUrl) {
      console.log(`ConceptCard - Using sample image URL: ${sampleImageUrl}`);
      return sampleImageUrl;
    }

    // If we have a concept, use its image logic
    if (concept) {
      // If includeOriginal is true and index is 0, or we're at index 0 without includeOriginal
      // or we have no color variations, use the original image
      if (
        (includeOriginal && selectedVariationIndex === 0) ||
        selectedVariationIndex === 0 ||
        !concept.color_variations ||
        concept.color_variations.length === 0
      ) {
        const baseUrl = concept.image_url || concept.base_image_url;
        console.log(
          `ConceptCard - Using concept original image: ${baseUrl?.substring(
            0,
            50,
          )}...`,
        );
        return baseUrl || "/placeholder-image.png";
      }

      // For color variations, adjust the index if includeOriginal is true
      const variationIndex = includeOriginal
        ? selectedVariationIndex - 1
        : selectedVariationIndex;

      // Otherwise, find the right variation image
      if (
        concept.color_variations &&
        variationIndex >= 0 &&
        variationIndex < concept.color_variations.length
      ) {
        const variationImage =
          concept.color_variations[variationIndex].image_url;
        console.log(
          `ConceptCard - Using variation image: ${variationImage?.substring(
            0,
            50,
          )}...`,
        );
        return variationImage || concept.image_url || "/placeholder-image.png";
      }
    }

    // Otherwise use the original logic for direct props
    console.log(`ConceptCard - Selected variation: ${selectedVariationIndex}`);
    console.log(
      `ConceptCard - Has images array: ${finalImages ? "yes" : "no"}, length: ${
        finalImages?.length || 0
      }`,
    );
    console.log(`ConceptCard - includeOriginal: ${includeOriginal}`);

    // If we don't have images, return empty string
    if (!finalImages || finalImages.length === 0) {
      console.log("ConceptCard - No images available");
      return "";
    }

    // Calculate which image to use based on the selected variation
    // Selection logic depends on whether we're including original or not
    let imageIndex = 0;

    if (includeOriginal) {
      // If includeOriginal is true, index 0 represents the original image
      // and variation indices start at 1
      imageIndex = selectedVariationIndex;
    } else {
      // If includeOriginal is false, variations start at index 0
      imageIndex = selectedVariationIndex;
    }

    // Ensure the index is within bounds
    if (imageIndex >= 0 && imageIndex < finalImages.length) {
      // Process the image URL to handle Supabase storage paths
      const rawUrl = finalImages[imageIndex];
      console.log(
        `ConceptCard - Using image at index ${imageIndex}:`,
        rawUrl?.substring(0, 50),
      );
      return rawUrl;
    }

    // Fallback to the first image if index is out of bounds
    console.log(
      "ConceptCard - Index out of bounds, using first image as fallback",
    );
    return finalImages[0];
  }, [
    sampleImageUrl,
    concept,
    selectedVariationIndex,
    finalImages,
    includeOriginal,
  ]);

  // Handle edit button click with proper typing for the callback
  const handleEdit = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!onEdit) return;

    if (concept) {
      // Get variation ID from selected index
      const variationId =
        selectedVariationIndex >= 0 &&
        concept.color_variations &&
        selectedVariationIndex < concept.color_variations.length
          ? concept.color_variations[selectedVariationIndex].id
          : null;

      console.log("[ConceptCard] Edit clicked:", {
        conceptId: concept.id,
        selectedIndex: selectedVariationIndex,
        variationId,
      });

      // Call with concept ID style params
      (onEdit as (conceptId: string, variationId?: string | null) => void)(
        concept.id,
        variationId,
      );
    } else {
      // Call with index style params
      (onEdit as (index: number) => void)(selectedVariationIndex);
    }
  };

  // Handle view details button click with proper typing for the callback
  const handleViewDetails = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!onViewDetails) return;

    if (concept) {
      // Get variation ID from selected index
      const variationId =
        selectedVariationIndex >= 0 &&
        concept.color_variations &&
        selectedVariationIndex < concept.color_variations.length
          ? concept.color_variations[selectedVariationIndex].id
          : null;

      console.log("[ConceptCard] View details clicked:", {
        conceptId: concept.id,
        selectedIndex: selectedVariationIndex,
        variationId,
      });

      // Call with concept ID style params
      (
        onViewDetails as (
          conceptId: string,
          variationId?: string | null,
        ) => void
      )(concept.id, variationId);
    } else {
      // Call with index style params
      (onViewDetails as (index: number) => void)(selectedVariationIndex);
    }
  };

  // Handle card click
  const handleCardClick = () => {
    // If prevention is enabled, do nothing
    if (preventNavigation) {
      return;
    }

    // Otherwise, trigger view details if handler exists
    if (onViewDetails) {
      handleViewDetails({
        preventDefault: () => {},
        stopPropagation: () => {},
      } as React.MouseEvent);
    }
  };

  // Create the card content
  const cardContent = (
    <div className={styles.card}>
      <div className={styles.headerImage}>
        {/* Display the initials in the colored background for a cleaner look */}
        <span className={styles.headerInitials}>{finalInitials}</span>
      </div>

      <div className={styles.content}>
        <div className={styles.logoContainer}>
          <div className={styles.logo}>
            {logoImageUrl ? (
              <OptimizedImage
                src={logoImageUrl || "/placeholder-image.png"}
                alt={finalTitle + " logo"}
                className={styles.logoImage}
                lazy={true}
                width="80"
                height="80"
                backgroundColor="#ffffff"
                placeholder="data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=="
              />
            ) : (
              <span className={styles.logoInitials}>{finalInitials}</span>
            )}
          </div>
        </div>

        <div className={styles.textContent}>
          <h3 className={styles.title}>{finalTitle}</h3>
          <p className={styles.description}>{finalDescription}</p>
        </div>

        {/* Color variations */}
        {finalColorVariations.length > 0 && (
          <div className={styles.colorVariations}>
            {includeOriginal && (
              <div
                className={styles.originalVariation}
                onClick={(e) => handleVariationSelect(0, e)}
              >
                O
              </div>
            )}

            {finalColorVariations.map((colorSet, variationIndex) => {
              // Adjust index if we include original variation
              const actualIndex = includeOriginal
                ? variationIndex + 1
                : variationIndex;
              const isSelected = selectedVariationIndex === actualIndex;
              const mainColor = colorSet[0] || "#4F46E5";
              const needsBorder = isLightColor(mainColor);

              return (
                <div
                  key={`${colorSet.join(",")}-${variationIndex}`}
                  className={`${styles.colorDot} ${
                    isSelected ? styles.colorDotSelected : ""
                  } ${needsBorder ? styles.colorDotLight : ""}`}
                  style={{ backgroundColor: mainColor }}
                  onClick={(e) => handleVariationSelect(actualIndex, e)}
                />
              );
            })}
          </div>
        )}

        {/* Action buttons */}
        <div className={styles.actions}>
          {onEdit && (
            <button onClick={handleEdit} className={styles.editButton}>
              {editButtonText}
            </button>
          )}

          {onViewDetails && (
            <button onClick={handleViewDetails} className={styles.viewButton}>
              View Details
            </button>
          )}
        </div>
      </div>
    </div>
  );

  // Wrap in Card component
  return (
    <Card onClick={handleCardClick} className="h-full">
      {cardContent}
    </Card>
  );
};

// Wrap with React.memo for performance optimization
export default React.memo(ConceptCard);
