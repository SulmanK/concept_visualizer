import React, { useState } from "react";

export interface ExportOptionsProps {
  /**
   * URL of the image to export
   */
  imageUrl: string;

  /**
   * Title/name of the concept
   */
  conceptTitle: string;

  /**
   * Variation name
   */
  variationName?: string;

  /**
   * Callback when the download button is clicked
   */
  onDownload?: (format: string, size: string) => void;
}

type ExportFormat = "png" | "svg" | "jpg";
type ExportSize = "small" | "medium" | "large" | "original";

const sizeMap = {
  small: "256 x 256 px",
  medium: "512 x 512 px",
  large: "1024 x 1024 px",
  original: "Max Quality",
};

/**
 * Component that allows users to export a concept in different formats and sizes
 */
export const ExportOptions: React.FC<ExportOptionsProps> = ({
  imageUrl,
  conceptTitle,
  variationName,
  onDownload,
}) => {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>("png");
  const [selectedSize, setSelectedSize] = useState<ExportSize>("medium");

  const handleDownload = () => {
    if (onDownload) {
      onDownload(selectedFormat, selectedSize);
    } else {
      // Default download behavior if no callback provided
      const a = document.createElement("a");
      a.href = imageUrl;
      a.download = `${conceptTitle}${
        variationName ? `-${variationName}` : ""
      }.${selectedFormat}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-6 mb-8 border border-indigo-100">
      <h3 className="text-lg font-semibold text-indigo-800 mb-4 flex items-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5 mr-2"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fillRule="evenodd"
            d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
            clipRule="evenodd"
          />
        </svg>
        Export Options
      </h3>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Image Preview */}
        <div className="w-full md:w-1/3">
          <div className="rounded-lg overflow-hidden shadow-md border border-indigo-100 bg-indigo-50">
            <img
              src={imageUrl}
              alt={conceptTitle}
              className="w-full h-auto object-contain"
            />
          </div>
          {variationName && (
            <div className="mt-4 text-center">
              <span className="text-sm font-medium text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full">
                {variationName}
              </span>
            </div>
          )}
        </div>

        {/* Export Options */}
        <div className="w-full md:w-2/3">
          <div className="mb-6">
            <h4 className="text-sm font-semibold text-indigo-700 mb-2">
              Select Format
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {/* PNG Format */}
              <div
                className={`border rounded-lg p-4 bg-white hover:shadow-md transition-all cursor-pointer group relative flex flex-col items-center
                  ${
                    selectedFormat === "png"
                      ? "border-indigo-400 shadow-md"
                      : "border-indigo-200 hover:border-indigo-400"
                  }`}
                onClick={() => setSelectedFormat("png")}
              >
                <div className="text-indigo-600 font-bold text-lg">.PNG</div>
                <span className="text-xs text-gray-500 mb-2">
                  Transparent Background
                </span>
                <div className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded-full">
                  Recommended
                </div>
                <div className="mt-2 text-xs text-gray-600 text-center">
                  Best for web, digital use
                </div>
              </div>

              {/* SVG Format */}
              <div
                className={`border rounded-lg p-4 bg-white hover:shadow-md transition-all cursor-pointer group relative flex flex-col items-center
                  ${
                    selectedFormat === "svg"
                      ? "border-indigo-400 shadow-md"
                      : "border-indigo-200 hover:border-indigo-400"
                  }`}
                onClick={() => setSelectedFormat("svg")}
              >
                <div className="text-indigo-600 font-bold text-lg">.SVG</div>
                <span className="text-xs text-gray-500 mb-2">
                  Vector Format
                </span>
                <div className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded-full">
                  Scalable
                </div>
                <div className="mt-2 text-xs text-gray-600 text-center">
                  Best for printing, scaling
                </div>
              </div>

              {/* JPG Format */}
              <div
                className={`border rounded-lg p-4 bg-white hover:shadow-md transition-all cursor-pointer group relative flex flex-col items-center
                  ${
                    selectedFormat === "jpg"
                      ? "border-indigo-400 shadow-md"
                      : "border-indigo-200 hover:border-indigo-400"
                  }`}
                onClick={() => setSelectedFormat("jpg")}
              >
                <div className="text-indigo-600 font-bold text-lg">.JPG</div>
                <span className="text-xs text-gray-500 mb-2">
                  With Background
                </span>
                <div className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded-full">
                  Smaller Size
                </div>
                <div className="mt-2 text-xs text-gray-600 text-center">
                  Best for photos, email
                </div>
              </div>
            </div>
          </div>

          <div className="mb-6">
            <h4 className="text-sm font-semibold text-indigo-700 mb-2">
              Size Options
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(sizeMap).map(([size, label]) => (
                <div
                  key={size}
                  className={`border rounded-lg p-3 bg-white hover:shadow-md transition-all cursor-pointer text-center
                    ${
                      selectedSize === size
                        ? "border-indigo-400 shadow-md"
                        : "border-indigo-200 hover:border-indigo-400"
                    }`}
                  onClick={() => setSelectedSize(size as ExportSize)}
                >
                  <div
                    className={`font-medium ${
                      selectedSize === size
                        ? "text-indigo-700"
                        : "text-indigo-600"
                    }`}
                  >
                    {size.charAt(0).toUpperCase() + size.slice(1)}
                  </div>
                  <span className="text-xs text-gray-500">{label}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="border-t border-indigo-100 pt-6 flex justify-between items-center">
            <div className="text-sm text-gray-600">
              <span className="font-medium">Selected:</span>{" "}
              {selectedFormat.toUpperCase()}, {sizeMap[selectedSize]}
            </div>

            <div className="flex gap-3">
              <button
                className="px-4 py-2 border border-indigo-200 text-indigo-600 font-medium rounded-lg hover:bg-indigo-50 transition-colors"
                onClick={() => window.open(imageUrl, "_blank")}
              >
                Preview
              </button>
              <button
                className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-indigo-400 text-white font-medium rounded-lg shadow-sm hover:shadow-md transition-all flex items-center"
                onClick={handleDownload}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4 mr-1"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
                Download
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
