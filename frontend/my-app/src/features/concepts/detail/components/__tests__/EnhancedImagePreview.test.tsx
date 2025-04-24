import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { vi } from "vitest";
import EnhancedImagePreview from "../EnhancedImagePreview";
import { ThemeProvider } from "@mui/material/styles";
import { theme } from "../../../../../theme";

// Mock Material UI icons
vi.mock("@mui/icons-material/ZoomIn", () => ({
  default: () => <span data-testid="zoom-in-icon">ZoomIn</span>,
}));

vi.mock("@mui/icons-material/ZoomOut", () => ({
  default: () => <span data-testid="zoom-out-icon">ZoomOut</span>,
}));

vi.mock("@mui/icons-material/RestartAlt", () => ({
  default: () => <span data-testid="reset-icon">Reset</span>,
}));

vi.mock("@mui/icons-material/Close", () => ({
  default: () => <span data-testid="close-icon">Close</span>,
}));

describe("EnhancedImagePreview Component", () => {
  const mockImageUrl = "test-image.jpg";
  const mockFormat = "jpg";
  const mockOnClose = vi.fn();

  const defaultProps = {
    isOpen: true,
    imageUrl: mockImageUrl,
    format: mockFormat,
    onClose: mockOnClose,
  };

  const renderWithTheme = (ui: React.ReactElement) => {
    return render(<ThemeProvider theme={theme}>{ui}</ThemeProvider>);
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("renders correctly when open", () => {
    renderWithTheme(<EnhancedImagePreview {...defaultProps} />);

    // Check if the component is rendered
    expect(screen.getByRole("presentation")).toBeInTheDocument();

    // Check if image is rendered with correct attributes
    const image = screen.getByAltText(`Preview in ${mockFormat} format`);
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute("src", mockImageUrl);

    // Check for control buttons
    expect(screen.getByTitle("Zoom in")).toBeInTheDocument();
    expect(screen.getByTitle("Zoom out")).toBeInTheDocument();
    expect(screen.getByTitle("Reset zoom")).toBeInTheDocument();
    expect(screen.getByTitle("Close preview")).toBeInTheDocument();
  });

  test("does not render when closed", () => {
    renderWithTheme(<EnhancedImagePreview {...defaultProps} isOpen={false} />);

    // Modal should not be in the document
    expect(screen.queryByRole("presentation")).not.toBeInTheDocument();
  });

  test("calls onClose when close button is clicked", () => {
    renderWithTheme(<EnhancedImagePreview {...defaultProps} />);

    // Find and click the close button
    const closeButton = screen.getByTitle("Close preview");
    fireEvent.click(closeButton);

    // Check if onClose was called
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });
});
