import React from "react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { OptimizedImage } from "../OptimizedImage";

// Store the callback function reference globally for testing
let intersectionCallback: IntersectionObserverCallback;

// Create a proper IntersectionObserver mock
class MockIntersectionObserver {
  readonly root: Element | null;
  readonly rootMargin: string;
  readonly thresholds: ReadonlyArray<number>;

  constructor(
    callback: IntersectionObserverCallback,
    options?: IntersectionObserverInit,
  ) {
    // Store the callback globally for testing access
    intersectionCallback = callback;

    this.root = options?.root || null;
    this.rootMargin = options?.rootMargin || "0px";
    this.thresholds = options?.threshold
      ? Array.isArray(options.threshold)
        ? options.threshold
        : [options.threshold]
      : [0];

    this._elements = new Set();
  }

  private _elements = new Set<Element>();

  observe(element: Element): void {
    this._elements.add(element);
  }

  unobserve(element: Element): void {
    this._elements.delete(element);
  }

  disconnect(): void {
    this._elements.clear();
  }
}

describe("OptimizedImage", () => {
  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();
    intersectionCallback = null as unknown as IntersectionObserverCallback;

    // Mock console.error
    console.error = vi.fn();

    // Setup IntersectionObserver mock
    vi.stubGlobal("IntersectionObserver", MockIntersectionObserver);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders with default props", () => {
    render(<OptimizedImage src="/test-image.jpg" alt="Test Image" />);

    const image = screen.getByAltText("Test Image");
    expect(image).toBeInTheDocument();

    // Image should not have src initially when lazy loading is enabled
    expect(image.getAttribute("src")).toBeNull();
  });

  it("renders with src immediately when lazy is false", () => {
    const testSrc = "/test-image.jpg";
    render(<OptimizedImage src={testSrc} alt="Test Image" lazy={false} />);

    const image = screen.getByAltText("Test Image");
    expect(image.getAttribute("src")).toBe(testSrc);
  });

  it("uses placeholder image when src is undefined", () => {
    render(<OptimizedImage src={undefined} alt="Test Image" lazy={false} />);

    const image = screen.getByAltText("Test Image");
    expect(image.getAttribute("src")).toBe("/placeholder-image.png");
  });

  it("loads the image when it becomes visible (intersection observer callback)", () => {
    const testSrc = "/test-image.jpg";
    render(<OptimizedImage src={testSrc} alt="Test Image" />);

    // Get image element
    const image = screen.getByAltText("Test Image");
    expect(image.getAttribute("src")).toBeNull(); // Image should start with no src

    // Create mock entry
    const mockEntry = [
      {
        isIntersecting: true,
        target: image,
        boundingClientRect: {} as DOMRectReadOnly,
        intersectionRatio: 1,
        intersectionRect: {} as DOMRectReadOnly,
        rootBounds: null,
        time: Date.now(),
      },
    ] as IntersectionObserverEntry[];

    // Use act to ensure state updates are processed
    act(() => {
      // Trigger the intersection callback directly
      intersectionCallback(mockEntry, {} as IntersectionObserver);
    });

    // Force a re-render to ensure the state changes take effect
    fireEvent(image, new Event("load"));

    // Use new instance of image to ensure we get updated attributes
    const updatedImage = screen.getByAltText("Test Image");
    expect(updatedImage.getAttribute("src")).toBe(testSrc);
  });

  it("sets the loaded state when image loads", () => {
    render(<OptimizedImage src="/test-image.jpg" alt="Test Image" />);

    const image = screen.getByAltText("Test Image");

    // Initially the opacity should be 0 (not loaded)
    expect(image.style.opacity).toBe("0");

    // Simulate image load
    fireEvent.load(image);

    // After loading, opacity should be 1
    expect(image.style.opacity).toBe("1");
  });

  it("handles image loading error", () => {
    render(<OptimizedImage src="/test-image.jpg" alt="Test Image" />);

    const image = screen.getByAltText("Test Image");

    // Simulate image error
    fireEvent.error(image);

    // Error message and icon should be displayed
    expect(screen.getByText("Failed to load image")).toBeInTheDocument();
    expect(console.error).toHaveBeenCalled();
  });

  it("renders with custom class name", () => {
    const customClass = "custom-image-class";
    render(
      <OptimizedImage
        src="/test-image.jpg"
        alt="Test Image"
        className={customClass}
      />,
    );

    const container = screen.getByAltText("Test Image").parentElement;
    expect(container?.classList.contains(customClass)).toBe(true);
  });

  it("applies custom width and height", () => {
    const width = 300;
    const height = 200;

    render(
      <OptimizedImage
        src="/test-image.jpg"
        alt="Test Image"
        width={width}
        height={height}
      />,
    );

    const image = screen.getByAltText("Test Image");
    expect(image.style.width).toBe(`${width}px`);
    expect(image.style.height).toBe(`${height}px`);

    // Container should also have the same dimensions
    const container = image.parentElement;
    expect(container?.style.width).toBe(`${width}px`);
    expect(container?.style.height).toBe(`${height}px`);
  });

  it("renders loading placeholder while image is loading", () => {
    render(<OptimizedImage src="/test-image.jpg" alt="Test Image" />);

    // Before image is loaded, a pulse animation should be shown
    const pulseElement = document.querySelector(".animate-pulse");
    expect(pulseElement).toBeInTheDocument();

    // Simulate image load
    const image = screen.getByAltText("Test Image");
    fireEvent.load(image);

    // After loading, pulse animation should be gone
    expect(document.querySelector(".animate-pulse")).not.toBeInTheDocument();
  });

  it("renders custom placeholder while image is loading", () => {
    const placeholderSrc = "/placeholder.jpg";
    render(
      <OptimizedImage
        src="/test-image.jpg"
        alt="Test Image"
        placeholder={placeholderSrc}
      />,
    );

    // Placeholder image should be rendered
    const placeholderImage = screen.getByAltText("Loading placeholder");
    expect(placeholderImage).toBeInTheDocument();
    expect(placeholderImage.getAttribute("src")).toBe(placeholderSrc);

    // Simulate image load
    const image = screen.getByAltText("Test Image");
    fireEvent.load(image);

    // After loading, placeholder should be gone
    expect(
      screen.queryByAltText("Loading placeholder"),
    ).not.toBeInTheDocument();
  });

  it("applies custom backgroundColor", () => {
    const customColor = "#ff0000";
    render(
      <OptimizedImage
        src="/test-image.jpg"
        alt="Test Image"
        backgroundColor={customColor}
      />,
    );

    const container = screen.getByAltText("Test Image").parentElement;
    const containerBgColor = container?.style.backgroundColor;
    expect(
      ["#ff0000", "rgb(255, 0, 0)", "#f00"].includes(containerBgColor),
    ).toBe(true);
  });

  it("applies custom objectFit", () => {
    const objectFit = "cover";
    render(
      <OptimizedImage
        src="/test-image.jpg"
        alt="Test Image"
        objectFit={objectFit}
      />,
    );

    const image = screen.getByAltText("Test Image");
    expect(image.style.objectFit).toBe(objectFit);
  });
});
