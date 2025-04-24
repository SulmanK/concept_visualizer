import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import ConceptImage from "../ConceptImage";

// Mock the OptimizedImage component
vi.mock("../../ui/OptimizedImage", () => ({
  OptimizedImage: ({ src, alt, onError, className, lazy }) => (
    <img
      data-testid="optimized-image"
      src={src}
      alt={alt}
      className={className}
      data-lazy={lazy}
      onError={() => onError && onError()}
    />
  ),
}));

describe("ConceptImage Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    console.error = vi.fn(); // Mock console.error to prevent test output pollution
  });

  // Test rendering with url prop
  it("renders OptimizedImage with url when provided", () => {
    const testUrl = "https://example.com/test-image.jpg";
    render(<ConceptImage url={testUrl} alt="Test image" />);

    // Check that OptimizedImage is rendered with the correct src
    const image = screen.getByTestId("optimized-image");
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute("src", testUrl);
    expect(image).toHaveAttribute("alt", "Test image");
  });

  // Test rendering with path prop (used as fallback)
  it("renders OptimizedImage with path when url is not provided", () => {
    const testPath = "/images/test-image.jpg";
    render(<ConceptImage path={testPath} alt="Test image from path" />);

    // Check that OptimizedImage is rendered with the path as src
    const image = screen.getByTestId("optimized-image");
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute("src", testPath);
  });

  // Test that url is preferred over path when both are provided
  it("prefers url over path when both are provided", () => {
    const testUrl = "https://example.com/test-image.jpg";
    const testPath = "/images/test-image.jpg";
    render(<ConceptImage url={testUrl} path={testPath} alt="Test image" />);

    // Check that OptimizedImage is rendered with the url as src
    const image = screen.getByTestId("optimized-image");
    expect(image).toHaveAttribute("src", testUrl);
  });

  // Test rendering without url or path
  it("shows placeholder message when neither url nor path is provided", () => {
    render(<ConceptImage alt="Missing image" />);

    // Check that placeholder is shown instead of OptimizedImage
    const placeholder = screen.getByText("No image available");
    expect(placeholder).toBeInTheDocument();

    // OptimizedImage should not be rendered
    expect(screen.queryByTestId("optimized-image")).not.toBeInTheDocument();
  });

  // Test rendering with empty string url and path
  it("shows placeholder message when url and path are empty strings", () => {
    render(<ConceptImage url="" path="" alt="Empty image" />);

    // Check that placeholder is shown instead of OptimizedImage
    const placeholder = screen.getByText("No image available");
    expect(placeholder).toBeInTheDocument();
  });

  // Test error handling
  it("shows error message when image fails to load", () => {
    const testUrl = "https://example.com/broken-image.jpg";

    render(<ConceptImage url={testUrl} alt="Broken image" />);

    // Find the image and simulate an error
    const image = screen.getByTestId("optimized-image");
    fireEvent.error(image);

    // Check that error message is shown
    const errorMessage = screen.getByText("Failed to load image");
    expect(errorMessage).toBeInTheDocument();

    // OptimizedImage should not be rendered anymore
    expect(screen.queryByTestId("optimized-image")).not.toBeInTheDocument();

    // Console.error should have been called
    expect(console.error).toHaveBeenCalledWith("Error loading image:", testUrl);
  });

  // Test passing className to OptimizedImage
  it("passes className to OptimizedImage", () => {
    const testUrl = "https://example.com/test-image.jpg";
    const testClass = "custom-image-class";

    render(
      <ConceptImage url={testUrl} alt="Test image" className={testClass} />,
    );

    // Check that the class is passed to OptimizedImage
    const image = screen.getByTestId("optimized-image");
    expect(image).toHaveAttribute("class", testClass);
  });

  // Test lazy loading prop
  it("passes lazy prop to OptimizedImage", () => {
    const testUrl = "https://example.com/test-image.jpg";

    render(
      <ConceptImage
        url={testUrl}
        alt="Test image"
        lazy={false} // Explicitly set to false to test (default is true)
      />,
    );

    // Check that lazy attribute is passed to OptimizedImage
    const image = screen.getByTestId("optimized-image");
    expect(image).toHaveAttribute("data-lazy", "false");
  });
});
