import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { LoadingIndicator } from "../LoadingIndicator";

describe("LoadingIndicator", () => {
  it("renders with default props", () => {
    render(<LoadingIndicator />);

    const spinner = screen.getByTestId("loading-spinner");
    expect(spinner).toBeInTheDocument();
    expect(spinner.classList.contains("w-8")).toBe(true);
    expect(spinner.classList.contains("h-8")).toBe(true);
    expect(spinner.classList.contains("text-indigo-600")).toBe(true);

    // Label should not be present by default
    expect(screen.queryByText("Loading...")).not.toBeInTheDocument();
  });

  it("renders with small size", () => {
    render(<LoadingIndicator size="small" />);

    const spinner = screen.getByTestId("loading-spinner");
    expect(spinner.classList.contains("w-4")).toBe(true);
    expect(spinner.classList.contains("h-4")).toBe(true);
  });

  it("renders with medium size", () => {
    render(<LoadingIndicator size="medium" />);

    const spinner = screen.getByTestId("loading-spinner");
    expect(spinner.classList.contains("w-8")).toBe(true);
    expect(spinner.classList.contains("h-8")).toBe(true);
  });

  it("renders with large size", () => {
    render(<LoadingIndicator size="large" />);

    const spinner = screen.getByTestId("loading-spinner");
    expect(spinner.classList.contains("w-12")).toBe(true);
    expect(spinner.classList.contains("h-12")).toBe(true);
  });

  it("renders with light variant", () => {
    render(<LoadingIndicator variant="light" />);

    const spinner = screen.getByTestId("loading-spinner");
    expect(spinner.classList.contains("text-white")).toBe(true);
  });

  it("renders with dark variant", () => {
    render(<LoadingIndicator variant="dark" />);

    const spinner = screen.getByTestId("loading-spinner");
    expect(spinner.classList.contains("text-gray-800")).toBe(true);
  });

  it("renders with label when showLabel is true", () => {
    render(<LoadingIndicator showLabel />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("renders with custom label text", () => {
    const customLabel = "Please wait...";
    render(<LoadingIndicator showLabel labelText={customLabel} />);

    expect(screen.getByText(customLabel)).toBeInTheDocument();
  });

  it("applies correct text size class for small size", () => {
    render(<LoadingIndicator size="small" showLabel />);
    const label = screen.getByText("Loading...");
    expect(label.classList.contains("text-xs")).toBe(true);
  });

  it("applies correct text size class for medium size", () => {
    render(<LoadingIndicator size="medium" showLabel />);
    const mediumLabel = screen.getByText("Loading...");
    expect(mediumLabel.classList.contains("text-sm")).toBe(true);
  });

  it("applies correct text size class for large size", () => {
    render(<LoadingIndicator size="large" showLabel />);
    const largeLabel = screen.getByText("Loading...");
    expect(largeLabel.classList.contains("text-base")).toBe(true);
  });

  it("applies custom className to container", () => {
    const customClass = "custom-test-class";
    render(<LoadingIndicator className={customClass} />);

    // Find the container div and check for the custom class
    const container = screen.getByTestId("loading-spinner").closest("div")
      ?.parentElement;
    expect(container?.classList.contains(customClass)).toBe(true);
  });
});
