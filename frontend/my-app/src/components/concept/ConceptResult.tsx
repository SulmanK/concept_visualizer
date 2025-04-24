import React, { useState, useEffect } from "react";
import { GenerationResponse, ColorPalette } from "../../types";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { ColorPalette as ColorPaletteComponent } from "../ui/ColorPalette";
import { logger } from "../../utils/logger";
import { devLog, devWarn, logError } from "../../utils/dev-logging";
import styles from "./ConceptResult.module.css";

export interface ConceptResultProps {
  /**
   * The generated concept data
   */
  concept: GenerationResponse;

  /**
   * Handler for requesting refinement
   */
  onRefineRequest?: () => void;

  /**
   * Handler for downloading the image
   */
  onDownload?: () => void;

  /**
   * Handler for selecting a color
   */
  onColorSelect?: (color: string) => void;

  /**
   * Optional color variations
   */
  variations?: Array<{
    name: string;
    colors: string[];
    image_url: string;
    description?: string;
  }>;

  /**
   * Handler for navigating to concept detail page
   */
  onExport?: (conceptId: string) => void;

  /**
   * The currently selected color
   */
  selectedColor?: string | null;

  /**
   * Handler for viewing concept details
   */
  onViewDetails?: () => void;
}

/**
 * Component for displaying generated concept results
 */
export const ConceptResult: React.FC<ConceptResultProps> = ({
  concept,
  onRefineRequest,
  onDownload,
  onColorSelect,
  variations = [],
  onExport,
  selectedColor = null,
  onViewDetails,
}) => {
  const [selectedVariation, setSelectedVariation] = useState<number | null>(
    null,
  );
  const [imageLoadErrors, setImageLoadErrors] = useState<
    Record<string, boolean>
  >({});

  useEffect(() => {
    // Reset selected variation when concept changes
    setSelectedVariation(null);
  }, [concept]);

  const handleImageError = (event: React.SyntheticEvent<HTMLImageElement>) => {
    const target = event.target as HTMLImageElement;
    devWarn(`Failed to load image: ${target.src}`);

    // Set a placeholder or fallback image
    target.src = "/images/placeholder-image.png";
    target.alt = "Image failed to load";
  };

  if (!concept || !concept.image_url) {
    return (
      <div className="p-6 text-center">
        <p className="text-gray-500">No concept data available</p>
      </div>
    );
  }

  // Format the date - just use created_at
  const createdDate = concept.created_at
    ? new Date(concept.created_at).toLocaleString()
    : "";

  const getFileName = (url: string): string => {
    try {
      // Extract filename from URL
      const parts = url.split("/");
      const filename = parts[parts.length - 1].split("?")[0]; // Remove query params if present

      // If the filename looks valid, use it
      if (filename && filename.includes(".")) {
        return filename;
      }
    } catch (error) {
      logError(error, "Error extracting filename from URL");
    }

    // Fallback filename
    return `concept-${concept.id || "image"}.png`;
  };

  const handleDownload = () => {
    if (onDownload) {
      onDownload();
      return;
    }

    // Use the formatted URL of the current image (variation or original)
    const imageUrl = getCurrentImageUrl();
    const filename = getFileName(imageUrl);

    // Create a link element and trigger download
    const link = document.createElement("a");
    link.href = imageUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getCurrentPalette = (): ColorPalette | string[] => {
    if (
      selectedVariation !== null &&
      variations &&
      variations[selectedVariation]
    ) {
      return variations[selectedVariation].colors;
    }

    return concept.color_palette || [];
  };

  const getOriginalImageUrl = (): string => {
    return concept.image_url || "/images/placeholder-image.png";
  };

  const getCurrentImageUrl = () => {
    // If a variation is selected, use its image_url
    if (
      selectedVariation !== null &&
      variations &&
      variations[selectedVariation]
    ) {
      return (
        variations[selectedVariation].image_url ||
        "/images/placeholder-image.png"
      );
    }

    // Otherwise use the original concept image
    return concept.image_url || "/images/placeholder-image.png";
  };

  const getCurrentVariationName = () => {
    if (
      selectedVariation !== null &&
      variations &&
      variations[selectedVariation]
    ) {
      return variations[selectedVariation].name;
    }

    return "Original";
  };

  const handleColorSelect = (color: string) => {
    if (onColorSelect) {
      onColorSelect(color);
    }
  };

  const getCurrentPaletteColors = () => {
    const palette = getCurrentPalette();
    return Array.isArray(palette)
      ? palette
      : (Object.values(palette as ColorPalette).filter(
          (val) => typeof val === "string",
        ) as string[]);
  };

  const getImageElements = () => {
    return variations.map((variation) => variation.image_url);
  };

  // Function to create a proper ColorPalette object from an array or existing object
  const createColorPaletteObject = (
    colors: string[] | ColorPalette,
  ): ColorPalette => {
    // If it's already a ColorPalette object with the expected properties
    if (
      typeof colors === "object" &&
      !Array.isArray(colors) &&
      "primary" in colors &&
      "secondary" in colors
    ) {
      return colors as ColorPalette;
    }

    // Convert array to ColorPalette object
    const colorArray = Array.isArray(colors)
      ? colors
      : ((typeof colors === "object"
          ? Object.values(colors).filter((val) => typeof val === "string")
          : []) as string[]);

    const palette: ColorPalette = {
      primary: colorArray[0] || "#4F46E5",
      secondary: colorArray[1] || "#818CF8",
      accent: colorArray[2] || "#C7D2FE",
      background: colorArray[3] || "#EEF2FF",
      text: colorArray[4] || "#312E81",
      additionalColors: [],
    };

    // Add any additional colors
    if (colorArray.length > 5) {
      palette.additionalColors = colorArray.slice(5);
    }

    return palette;
  };

  // Get the current palette as a proper ColorPalette object
  const currentPalette = createColorPaletteObject(getCurrentPalette());

  return (
    <div className={styles.container}>
      {/* Header with title and date */}
      <div className={styles.pageHeader}>
        <h2 className={styles.title}>Generated Concept</h2>
        {createdDate && <span className={styles.date}>{createdDate}</span>}
      </div>

      {/* Main concept image */}
      <div className={styles.section}>
        <div className={styles.sectionTitle}>{getCurrentVariationName()}</div>
        <div className={styles.mainImageContainer}>
          <img
            src={getCurrentImageUrl()}
            alt={`Generated concept - ${getCurrentVariationName()}`}
            className={styles.image}
            onError={handleImageError}
          />
        </div>
      </div>

      {/* Color palette section */}
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Color Palette</h3>

        <div className={styles.card}>
          <ColorPaletteComponent
            palette={currentPalette}
            showLabels={true}
            selectable={!!onColorSelect}
            selectedColor={selectedColor || undefined}
            onColorSelect={(color) => handleColorSelect(color)}
            size="md"
            className="flex justify-center"
          />
        </div>
      </div>

      {/* Variations */}
      {variations && variations.length > 0 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Variations</h3>
          <div className={styles.variationsGrid}>
            {/* Original version */}
            <div
              className={`${styles.variationCard} ${
                selectedVariation === null ? styles.variationCardSelected : ""
              } hover:shadow-md`}
              onClick={() => setSelectedVariation(null)}
            >
              <div className={styles.variationHeader}>
                <span className={styles.variationTitle}>Original</span>
              </div>
              <div className={styles.variationContent}>
                <img
                  src={getOriginalImageUrl()}
                  alt="Original concept"
                  className={styles.variationImage}
                  onError={handleImageError}
                />
                <div className={styles.colorDotsContainer}>
                  {concept.color_palette && Array.isArray(concept.color_palette)
                    ? concept.color_palette
                        .slice(0, 5)
                        .map((color, idx) => (
                          <div
                            key={`original-color-${idx}`}
                            className={styles.colorDot}
                            style={{ backgroundColor: color }}
                          />
                        ))
                    : concept.color_palette &&
                      typeof concept.color_palette === "object"
                    ? Object.values(concept.color_palette)
                        .filter((val) => typeof val === "string")
                        .slice(0, 5)
                        .map((color, idx) => (
                          <div
                            key={`original-color-${idx}`}
                            className={styles.colorDot}
                            style={{ backgroundColor: color as string }}
                          />
                        ))
                    : null}
                </div>
              </div>
            </div>

            {/* Other variations */}
            {variations.map((variation, index) => (
              <div
                key={`variation-${index}`}
                className={`${styles.variationCard} ${
                  selectedVariation === index
                    ? styles.variationCardSelected
                    : ""
                } hover:shadow-md`}
                onClick={() => setSelectedVariation(index)}
              >
                <div className={styles.variationHeader}>
                  <span className={styles.variationTitle}>
                    {variation.name}
                  </span>
                </div>
                <div className={styles.variationContent}>
                  <img
                    src={variation.image_url}
                    alt={`Variation: ${variation.name}`}
                    className={styles.variationImage}
                    onError={handleImageError}
                  />
                  <div className={styles.colorDotsContainer}>
                    {variation.colors.slice(0, 5).map((color, idx) => (
                      <div
                        key={`var-${index}-color-${idx}`}
                        className={styles.colorDot}
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className={styles.actionsContainer}>
        {onViewDetails && (
          <Button variant="primary" onClick={onViewDetails}>
            View Details
          </Button>
        )}

        {onRefineRequest && (
          <Button variant="outline" onClick={onRefineRequest}>
            Refine Concept
          </Button>
        )}

        <Button variant="outline" onClick={handleDownload}>
          Download
        </Button>

        {onExport && concept.id && (
          <Button
            variant="outline"
            onClick={() => onExport(concept.id as string)}
          >
            Export
          </Button>
        )}
      </div>
    </div>
  );
};
