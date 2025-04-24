import React, { useState, useEffect, useRef, useCallback } from "react";
import { ErrorMessage } from "../../../../components/ui";
import {
  RateLimitError,
  ExportFormat,
  ExportSize,
} from "../../../../services/apiClient";
import {
  useExportImageMutation,
  downloadBlob,
} from "../../../../hooks/useExportImageMutation";
import { extractStoragePathFromUrl } from "../../../../utils/url";
import EnhancedImagePreview from "./EnhancedImagePreview";
import "./ExportOptions.css";

export interface ExportOptionsProps {
  /**
   * URL of the image to process and download
   */
  imageUrl: string | undefined;

  /**
   * Storage path of the image (if available)
   * Will be extracted from imageUrl if not provided
   */
  storagePath?: string;

  /**
   * Title/name of the concept
   */
  conceptTitle: string;

  /**
   * Variation name
   */
  variationName?: string;

  /**
   * Indicates if this is a palette variation (vs an original concept)
   * Used to determine which storage bucket to use
   */
  isPaletteVariation?: boolean;

  /**
   * Callback when the download button is clicked
   */
  onDownload?: (format: ExportFormat, size: ExportSize) => void;
}

const sizeMap = {
  small: "256px",
  medium: "512px",
  large: "1024px",
  original: "Max Quality",
};

/**
 * Component that allows users to export a concept in different formats and sizes
 */
export const ExportOptions: React.FC<ExportOptionsProps> = ({
  imageUrl,
  storagePath,
  conceptTitle,
  variationName = "",
  isPaletteVariation = false,
  onDownload,
}) => {
  const componentId = useRef(
    `export-options-${Math.random().toString(36).substr(2, 9)}`,
  );
  console.log(`[ExportOptions ${componentId.current}] Component rendering`);

  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>("png");
  const [selectedSize, setSelectedSize] = useState<ExportSize>("medium");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [debugInfo, setDebugInfo] = useState<{
    lastAction: string;
    timestamp: number;
    previewCount: number;
  }>({
    lastAction: "init",
    timestamp: Date.now(),
    previewCount: 0,
  });
  const [modalPreviewUrl, setModalPreviewUrl] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  // References to track blob URLs for cleanup
  const revokedUrlsRef = useRef<Set<string>>(new Set());

  // Use our new export mutation hook
  const {
    mutate: exportImage,
    isPending: isExporting,
    error: exportError,
  } = useExportImageMutation();

  // Use another instance of the export mutation hook specifically for previews
  const {
    mutate: previewImage,
    isPending: isPreviewExporting,
    error: previewError,
    reset: resetPreviewMutation,
  } = useExportImageMutation();

  // Update debug info when preview states change
  useEffect(() => {
    console.log(
      `[ExportOptions ${componentId.current}] isPreviewExporting changed to: ${isPreviewExporting}`,
    );

    if (isPreviewExporting) {
      setDebugInfo((prev) => ({
        ...prev,
        lastAction: "preview-started",
        timestamp: Date.now(),
      }));
    } else {
      // Only log transitions from true to false
      if (debugInfo.lastAction === "preview-started") {
        setDebugInfo((prev) => ({
          ...prev,
          lastAction: "preview-finished",
          timestamp: Date.now(),
        }));
      }
    }
  }, [isPreviewExporting, debugInfo.lastAction]);

  // Safe URL revocation function to prevent revoking the same URL twice
  const safeRevokeObjectURL = (url: string) => {
    if (!url.startsWith("blob:")) return;

    if (!revokedUrlsRef.current.has(url)) {
      console.log(
        `[ExportOptions ${componentId.current}] Revoking blob URL:`,
        url,
      );
      URL.revokeObjectURL(url);
      revokedUrlsRef.current.add(url);
    } else {
      console.log(
        `[ExportOptions ${componentId.current}] URL already revoked, skipping:`,
        url,
      );
    }
  };

  // Update error message when export fails
  useEffect(() => {
    if (exportError) {
      console.log(
        `[ExportOptions ${componentId.current}] Export error detected:`,
        exportError,
      );
      const error = exportError as Error;
      // Format a user-friendly error message
      if (error instanceof RateLimitError) {
        setErrorMessage(
          `Export limit reached: ${error.getUserFriendlyMessage()}`,
        );
      } else {
        setErrorMessage(`Failed to export image: ${error.message}`);
      }
    } else if (previewError) {
      console.log(
        `[ExportOptions ${componentId.current}] Preview error detected:`,
        previewError,
      );
      const error = previewError as Error;
      // Format a user-friendly error message for preview errors
      if (error instanceof RateLimitError) {
        setErrorMessage(
          `Preview limit reached: ${error.getUserFriendlyMessage()}`,
        );
      } else {
        setErrorMessage(`Failed to generate preview: ${error.message}`);
      }
    } else {
      setErrorMessage("");
    }
  }, [exportError, previewError]);

  // Clean up any blob URLs when component unmounts or preview changes
  useEffect(() => {
    return () => {
      console.log(
        `[ExportOptions ${componentId.current}] Component unmounting, cleaning up resources`,
      );
      if (previewUrl && previewUrl.startsWith("blob:")) {
        safeRevokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  // Clean up modal preview URL when component unmounts
  useEffect(() => {
    return () => {
      if (modalPreviewUrl && modalPreviewUrl.startsWith("blob:")) {
        safeRevokeObjectURL(modalPreviewUrl);
      }
    };
  }, [modalPreviewUrl]);

  // Helper function to determine which bucket to use
  const determineStorageBucket = useCallback((): string => {
    console.log(
      `[ExportOptions ${componentId.current}] Determining bucket: isPaletteVariation=${isPaletteVariation}, storagePath=${storagePath}, variationName=${variationName}`,
    );

    // If isPaletteVariation is explicitly set, always use palette bucket
    if (isPaletteVariation) {
      console.log(
        `[ExportOptions ${componentId.current}] Using palette-images bucket: isPaletteVariation flag is true`,
      );
      return "palette-images";
    }

    // Check if the variation name indicates a palette variation
    if (
      variationName &&
      (variationName.toLowerCase().includes("palette") ||
        variationName.toLowerCase().includes("color"))
    ) {
      console.log(
        `[ExportOptions ${componentId.current}] Using palette-images bucket: variation name indicates palette`,
      );
      return "palette-images";
    }

    // Use concept-images bucket by default
    return "concept-images";
  }, [isPaletteVariation, variationName]);

  // Force clear all React Query state for this component
  const forceClearMutationState = useCallback(() => {
    console.log(
      `[ExportOptions ${componentId.current}] Forcing clear of mutation state`,
    );
    resetPreviewMutation();
    // Wait a small amount of time and check if state is actually reset
    setTimeout(() => {
      console.log(
        `[ExportOptions ${componentId.current}] After reset: isPreviewExporting=${isPreviewExporting}`,
      );
    }, 100);
  }, [resetPreviewMutation, isPreviewExporting]);

  // Close modal and clean up preview URL when modal closes
  const handleCloseModal = useCallback(() => {
    setIsModalOpen(false);
    // Clean up the blob URL after the modal is closed
    setTimeout(() => {
      if (modalPreviewUrl && modalPreviewUrl.startsWith("blob:")) {
        safeRevokeObjectURL(modalPreviewUrl);
        setModalPreviewUrl(null);
      }
    }, 300);
  }, [modalPreviewUrl]);

  // Handle preview button click
  const handlePreview = async () => {
    console.log(
      `[ExportOptions ${componentId.current}] Preview button clicked. Current state: isPreviewExporting=${isPreviewExporting}`,
    );

    // Safety check - if somehow we're already in a loading state, force reset it first
    if (isPreviewExporting) {
      console.log(
        `[ExportOptions ${componentId.current}] WARNING: Preview already in progress, forcibly resetting state`,
      );
      resetPreviewMutation();
      // Small delay to let the reset take effect
      await new Promise((resolve) => setTimeout(resolve, 50));
    }

    // Check if we have a valid imageUrl
    if (!imageUrl) {
      setErrorMessage("No image URL available for preview");
      return;
    }

    // Clear any previous errors
    setErrorMessage("");

    // Create an AbortController to timeout the request if it takes too long
    const abortController = new AbortController();
    // Set a 10-second timeout
    const timeoutId = setTimeout(() => {
      console.log(
        `[ExportOptions ${componentId.current}] Preview request timed out, aborting`,
      );
      abortController.abort();
    }, 10000);

    // Update debug info
    setDebugInfo((prev) => ({
      ...prev,
      lastAction: "preview-button-clicked",
      timestamp: Date.now(),
      previewCount: prev.previewCount + 1,
    }));

    try {
      // Extract storage path from URL if not provided
      const imagePath = storagePath || extractStoragePathFromUrl(imageUrl);

      if (!imagePath) {
        setErrorMessage("Could not determine storage path for image");
        clearTimeout(timeoutId);
        return;
      }

      // Determine which bucket the image is in
      const bucket = determineStorageBucket();
      console.log(
        `[ExportOptions ${componentId.current}] Using bucket "${bucket}" for preview of image: ${imagePath}`,
      );

      // Build a distinct request ID for logging/debugging
      const requestId = `prev_${Date.now()}_${Math.random()
        .toString(36)
        .substr(2, 5)}`;

      // Use the preview mutation to generate the preview
      previewImage(
        {
          imageIdentifier: imagePath,
          format: selectedFormat,
          size: selectedSize,
          svgParams:
            selectedFormat === "svg"
              ? {
                  color_mode: "color",
                  hierarchical: true,
                }
              : undefined,
          bucket: bucket,
          _timestamp: Date.now(),
        },
        {
          onSuccess: (blob) => {
            console.log(
              `[ExportOptions ${componentId.current}] Preview request ${requestId} succeeded, creating blob URL`,
            );
            // Clear the timeout since the request succeeded
            clearTimeout(timeoutId);

            // Create URL for preview
            const url = URL.createObjectURL(blob);

            // Update state to show preview in modal
            setModalPreviewUrl(url);
            setIsModalOpen(true);

            // Update debug info
            setDebugInfo((prev) => ({
              ...prev,
              lastAction: "preview-success",
              timestamp: Date.now(),
            }));
          },
          onError: (error) => {
            console.error(
              `[ExportOptions ${componentId.current}] Preview request ${requestId} failed:`,
              error,
            );
            // Clear the timeout since the request failed
            clearTimeout(timeoutId);

            // Update debug info
            setDebugInfo((prev) => ({
              ...prev,
              lastAction: "preview-error",
              timestamp: Date.now(),
            }));
          },
          onSettled: () => {
            console.log(
              `[ExportOptions ${componentId.current}] Preview request ${requestId} settled. Explicitly resetting state.`,
            );
            // Clear the timeout as a precaution
            clearTimeout(timeoutId);

            // Update debug info
            setDebugInfo((prev) => ({
              ...prev,
              lastAction: "preview-settled",
              timestamp: Date.now(),
            }));

            // Explicitly call reset for the preview mutation with a small delay
            // to ensure all React Query internal processes are complete
            setTimeout(() => {
              resetPreviewMutation();

              // Check state after reset
              setTimeout(() => {
                console.log(
                  `[ExportOptions ${componentId.current}] After reset: isPreviewExporting=${isPreviewExporting}`,
                );
                // If still loading after reset, force another reset
                if (isPreviewExporting) {
                  console.log(
                    `[ExportOptions ${componentId.current}] Still loading after reset, forcing another reset`,
                  );
                  resetPreviewMutation();
                }
              }, 50);
            }, 50);
          },
        },
      );
    } catch (error) {
      console.error(
        `[ExportOptions ${componentId.current}] Error initiating preview:`,
        error,
      );
      setErrorMessage(
        `Failed to create preview: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
      );

      // Clear the timeout since we're handling the error
      clearTimeout(timeoutId);

      // Update debug info
      setDebugInfo((prev) => ({
        ...prev,
        lastAction: "preview-catch-error",
        timestamp: Date.now(),
      }));

      // Ensure reset is called even if the initial try block fails
      resetPreviewMutation();
    }
  };

  // Handle download button click
  const handleDownloadClick = () => {
    // Check if we have a valid imageUrl
    if (!imageUrl) {
      setErrorMessage("No image URL available for download");
      return;
    }

    console.log(
      `[ExportOptions ${componentId.current}] Download button clicked`,
    );
    console.log(`[ExportOptions ${componentId.current}] Image URL:`, imageUrl);
    console.log(
      `[ExportOptions ${componentId.current}] Storage path:`,
      storagePath,
    );
    console.log(
      `[ExportOptions ${componentId.current}] Is palette variation:`,
      isPaletteVariation,
    );
    console.log(
      `[ExportOptions ${componentId.current}] Variation name:`,
      variationName,
    );

    try {
      // Extract storage path from URL if not provided
      const imagePath = storagePath || extractStoragePathFromUrl(imageUrl);

      if (!imagePath) {
        setErrorMessage("Could not determine storage path for image");
        return;
      }

      // Determine which bucket the image is in
      const bucket = determineStorageBucket();
      console.log(
        `[ExportOptions ${componentId.current}] Using bucket "${bucket}" for image: ${imagePath}`,
      );

      // Create a filename for the download using the requested format: filename-size.format
      // Sanitize concept title and variation name for filename
      const sanitizedTitle = conceptTitle
        .replace(/[^\w\s-]/g, "")
        .trim()
        .replace(/\s+/g, "_");
      const sanitizedVariation = variationName
        ? variationName
            .replace(/[^\w\s-]/g, "")
            .trim()
            .replace(/\s+/g, "_")
        : "";

      // Construct the filename with the pattern: concept-variation-size.format
      const filename = `${sanitizedTitle}${
        sanitizedVariation ? `-${sanitizedVariation}` : ""
      }-${selectedSize}.${selectedFormat}`;

      console.log(
        `[ExportOptions ${componentId.current}] Downloading file as: ${filename}`,
      );
      console.log(`[ExportOptions ${componentId.current}] Request params:`, {
        imageIdentifier: imagePath,
        format: selectedFormat,
        size: selectedSize,
        svgParams:
          selectedFormat === "svg"
            ? { color_mode: "color", hierarchical: true }
            : undefined,
        bucket: bucket,
      });

      // Use the export mutation to generate the file
      exportImage(
        {
          imageIdentifier: imagePath,
          format: selectedFormat,
          size: selectedSize,
          svgParams:
            selectedFormat === "svg"
              ? {
                  color_mode: "color",
                  hierarchical: true,
                }
              : undefined,
          bucket: bucket,
          _timestamp: Date.now(),
        },
        {
          onSuccess: (blob) => {
            // Use the downloadBlob utility to trigger the download
            downloadBlob(blob, filename);
          },
        },
      );
    } catch (error) {
      console.error("Error initiating download:", error);
      setErrorMessage(
        `Failed to initiate download: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
      );
    }
  };

  // Handle copy link button click
  const handleCopyLink = () => {
    if (!imageUrl) {
      setErrorMessage("No image URL available to copy");
      return;
    }

    try {
      navigator.clipboard.writeText(imageUrl).then(() => {
        // Show success message
        setCopySuccess(true);
        // Reset the success message after a short delay
        setTimeout(() => {
          setCopySuccess(false);
        }, 2000);
      });
    } catch (error) {
      console.error("Error copying image URL:", error);
      setErrorMessage(
        `Failed to copy link: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
      );
    }
  };

  // Render debug information conditionally if in development
  const renderDebugInfo = () => {
    // Always return null to hide debug info in all environments
    return null;
  };

  return (
    <div className="export-options">
      <div className="export-options-body">
        <div className="export-format-section">
          <div className="export-section-title">Format</div>
          <div className="export-format-buttons">
            <button
              className={`format-button ${
                selectedFormat === "png" ? "selected" : ""
              }`}
              onClick={() => setSelectedFormat("png")}
            >
              PNG
            </button>
            <button
              className={`format-button ${
                selectedFormat === "jpg" ? "selected" : ""
              }`}
              onClick={() => setSelectedFormat("jpg")}
            >
              JPG
            </button>
            <button
              className={`format-button ${
                selectedFormat === "svg" ? "selected" : ""
              }`}
              onClick={() => setSelectedFormat("svg")}
            >
              SVG
            </button>
          </div>
        </div>

        <div className="export-size-section">
          <div className="export-section-title">Size</div>
          <div className="export-size-buttons">
            <button
              className={`size-button ${
                selectedSize === "small" ? "selected" : ""
              }`}
              onClick={() => setSelectedSize("small")}
            >
              <span className="size-label">256px</span>
            </button>
            <button
              className={`size-button ${
                selectedSize === "medium" ? "selected" : ""
              }`}
              onClick={() => setSelectedSize("medium")}
            >
              <span className="size-label">512px</span>
            </button>
            <button
              className={`size-button ${
                selectedSize === "large" ? "selected" : ""
              }`}
              onClick={() => setSelectedSize("large")}
            >
              <span className="size-label">1024px</span>
            </button>
            <button
              className={`size-button ${
                selectedSize === "original" ? "selected" : ""
              }`}
              onClick={() => setSelectedSize("original")}
            >
              <span className="size-label">Max Quality</span>
            </button>
          </div>
        </div>

        {errorMessage && (
          <div className="export-error-message">
            <ErrorMessage message={errorMessage} />
          </div>
        )}

        <div className="export-actions">
          <button
            className="preview-button"
            onClick={handlePreview}
            disabled={isPreviewExporting || !imageUrl}
          >
            {isPreviewExporting ? "Previewing..." : "Preview"}
          </button>
          <button
            className="download-button"
            onClick={handleDownloadClick}
            disabled={isExporting || !imageUrl}
          >
            {isExporting ? "Exporting..." : "Download"}
          </button>
          <button
            className={`copy-link-button ${copySuccess ? "success" : ""}`}
            onClick={handleCopyLink}
            disabled={!imageUrl}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4 mr-1"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              {copySuccess ? (
                // Checkmark icon when copied
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              ) : (
                // Link icon normally
                <path
                  fillRule="evenodd"
                  d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z"
                  clipRule="evenodd"
                />
              )}
            </svg>
            {copySuccess ? "Copied!" : "Copy Original Link"}
          </button>
        </div>

        {renderDebugInfo()}
      </div>

      {/* Modal for preview */}
      <EnhancedImagePreview
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        imageUrl={modalPreviewUrl || ""}
        format={selectedFormat}
      />
    </div>
  );
};
