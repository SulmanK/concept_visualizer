import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { ConceptRefinementForm } from "../ConceptRefinementForm";
import { FormStatus } from "../../../types";
import { vi } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { TaskProvider } from "../../../contexts/TaskContext";

// Mock TaskProvider for tests
vi.mock("../../../hooks/useTaskSubscription", () => ({
  useTaskSubscription: () => ({
    taskData: null,
    error: null,
    status: "success",
  }),
}));

// Create a wrapper component for the tests
const TestWrapper = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <TaskProvider>{children}</TaskProvider>
    </QueryClientProvider>
  );
};

describe("ConceptRefinementForm Component", () => {
  // Mock handlers and props
  const mockSubmit = vi.fn();
  const mockCancel = vi.fn();
  const originalImageUrl = "https://example.com/original-concept.png";
  const initialLogoDescription = "Initial logo description";
  const initialThemeDescription = "Initial theme description";

  // Reset mocks before each test
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // Basic rendering test
  test("renders form fields and buttons", () => {
    render(
      <TestWrapper>
        <ConceptRefinementForm
          originalImageUrl={originalImageUrl}
          onSubmit={mockSubmit}
          status="idle"
          onCancel={mockCancel}
          initialLogoDescription={initialLogoDescription}
          initialThemeDescription={initialThemeDescription}
        />
      </TestWrapper>,
    );

    // Check for card title - be more specific to get the heading, not the button
    const titleHeading = screen.getByRole("heading", {
      name: "Refine Concept",
    });
    expect(titleHeading).toBeInTheDocument();

    // Check for form inputs
    const refinementLabel = screen.getByText("Refinement Instructions");
    const logoLabel = screen.getByText("Updated Logo Description (Optional)");
    const themeLabel = screen.getByText("Updated Theme Description (Optional)");
    expect(refinementLabel).toBeInTheDocument();
    expect(logoLabel).toBeInTheDocument();
    expect(themeLabel).toBeInTheDocument();

    // Check for the original image
    const originalImage = screen.getByAltText("Original concept");
    expect(originalImage).toBeInTheDocument();
    expect(originalImage).toHaveAttribute("src", originalImageUrl);

    // Check for preserve aspects section
    const preserveAspectsText = screen.getByText("Preserve Aspects (Optional)");
    expect(preserveAspectsText).toBeInTheDocument();

    // Check for aspect options
    const layoutOption = screen.getByText("Layout");
    const colorsOption = screen.getByText("Colors");
    const styleOption = screen.getByText("Style");
    const symbolsOption = screen.getByText("Symbols/Icons");
    const proportionsOption = screen.getByText("Proportions");
    expect(layoutOption).toBeInTheDocument();
    expect(colorsOption).toBeInTheDocument();
    expect(styleOption).toBeInTheDocument();
    expect(symbolsOption).toBeInTheDocument();
    expect(proportionsOption).toBeInTheDocument();

    // Check for buttons
    const cancelButton = screen.getByRole("button", { name: /Cancel/i });
    const submitButton = screen.getByRole("button", {
      name: /Refine Concept/i,
    });
    expect(cancelButton).toBeInTheDocument();
    expect(submitButton).toBeInTheDocument();
  });

  // Initial values test
  test("renders with initial values", () => {
    render(
      <TestWrapper>
        <ConceptRefinementForm
          originalImageUrl={originalImageUrl}
          onSubmit={mockSubmit}
          status="idle"
          onCancel={mockCancel}
          initialLogoDescription={initialLogoDescription}
          initialThemeDescription={initialThemeDescription}
        />
      </TestWrapper>,
    );

    // Find the textareas by their labels
    const logoLabel = screen.getByText("Updated Logo Description (Optional)");
    const themeLabel = screen.getByText("Updated Theme Description (Optional)");

    // Find the textareas via their parent elements
    const logoTextarea = logoLabel.closest("div")?.querySelector("textarea");
    const themeTextarea = themeLabel.closest("div")?.querySelector("textarea");

    // Check that they have the initial values
    expect(logoTextarea).toHaveValue(initialLogoDescription);
    expect(themeTextarea).toHaveValue(initialThemeDescription);
  });

  // Form validation test - empty refinement prompt
  test("validates form and prevents submission with empty refinement prompt", () => {
    render(
      <TestWrapper>
        <ConceptRefinementForm
          originalImageUrl={originalImageUrl}
          onSubmit={mockSubmit}
          status="idle"
          onCancel={mockCancel}
        />
      </TestWrapper>,
    );

    // Find and click the submit button without filling out the refinement prompt
    const submitButton = screen.getByRole("button", {
      name: /Refine Concept/i,
    });
    fireEvent.click(submitButton);

    // Check for validation error message
    const error = screen.getByText("Please provide refinement instructions");
    expect(error).toBeInTheDocument();

    // Verify that the submission handler was not called
    expect(mockSubmit).not.toHaveBeenCalled();
  });

  // Form validation test - refinement prompt too short
  test("validates form and prevents submission with refinement prompt that is too short", () => {
    render(
      <TestWrapper>
        <ConceptRefinementForm
          originalImageUrl={originalImageUrl}
          onSubmit={mockSubmit}
          status="idle"
          onCancel={mockCancel}
        />
      </TestWrapper>,
    );

    // Find the refinement prompt textarea by its label
    const refinementLabel = screen.getByText("Refinement Instructions");
    const refinementTextarea = refinementLabel
      .closest("div")
      ?.querySelector("textarea");

    // Fill out the refinement prompt with a value that is too short
    if (refinementTextarea) {
      fireEvent.change(refinementTextarea, { target: { value: "Test" } });
    }

    // Find and click the submit button
    const submitButton = screen.getByRole("button", {
      name: /Refine Concept/i,
    });
    fireEvent.click(submitButton);

    // Check for validation error message
    const error = screen.getByText(
      "Refinement instructions must be at least 5 characters",
    );
    expect(error).toBeInTheDocument();

    // Verify that the submission handler was not called
    expect(mockSubmit).not.toHaveBeenCalled();
  });

  // Successful form submission test - with no preserved aspects
  test("submits form with valid refinement prompt and no preserved aspects", () => {
    render(
      <TestWrapper>
        <ConceptRefinementForm
          originalImageUrl={originalImageUrl}
          onSubmit={mockSubmit}
          status="idle"
          onCancel={mockCancel}
          initialLogoDescription={initialLogoDescription}
          initialThemeDescription={initialThemeDescription}
        />
      </TestWrapper>,
    );

    // Find the refinement prompt textarea by its label
    const refinementLabel = screen.getByText("Refinement Instructions");
    const refinementTextarea = refinementLabel
      .closest("div")
      ?.querySelector("textarea");

    // Fill out the refinement prompt with a valid value
    if (refinementTextarea) {
      fireEvent.change(refinementTextarea, {
        target: { value: "Make the logo more minimalist and modern" },
      });
    }

    // Find and click the submit button
    const submitButton = screen.getByRole("button", {
      name: /Refine Concept/i,
    });
    fireEvent.click(submitButton);

    // Verify that the submission handler was called with the correct values
    expect(mockSubmit).toHaveBeenCalledWith(
      "Make the logo more minimalist and modern",
      initialLogoDescription,
      initialThemeDescription,
      [],
    );
  });

  // Successful form submission test - with preserved aspects
  test("submits form with valid refinement prompt and selected preserved aspects", () => {
    render(
      <TestWrapper>
        <ConceptRefinementForm
          originalImageUrl={originalImageUrl}
          onSubmit={mockSubmit}
          status="idle"
          onCancel={mockCancel}
          initialLogoDescription={initialLogoDescription}
          initialThemeDescription={initialThemeDescription}
        />
      </TestWrapper>,
    );

    // Find the refinement prompt textarea by its label
    const refinementLabel = screen.getByText("Refinement Instructions");
    const refinementTextarea = refinementLabel
      .closest("div")
      ?.querySelector("textarea");

    // Fill out the refinement prompt with a valid value
    if (refinementTextarea) {
      fireEvent.change(refinementTextarea, {
        target: { value: "Make the logo more minimalist and modern" },
      });
    }

    // Select some preserve aspects checkboxes
    const colorsCheckbox = screen.getByText("Colors").previousElementSibling;
    const styleCheckbox = screen.getByText("Style").previousElementSibling;

    if (colorsCheckbox && styleCheckbox) {
      fireEvent.click(colorsCheckbox);
      fireEvent.click(styleCheckbox);
    }

    // Find and click the submit button
    const submitButton = screen.getByRole("button", {
      name: /Refine Concept/i,
    });
    fireEvent.click(submitButton);

    // Verify that the submission handler was called with the correct values
    expect(mockSubmit).toHaveBeenCalledWith(
      "Make the logo more minimalist and modern",
      initialLogoDescription,
      initialThemeDescription,
      ["colors", "style"],
    );
  });

  // Test aspect selection toggle
  test("toggles preserve aspect when checkbox is clicked", () => {
    render(
      <TestWrapper>
        <ConceptRefinementForm
          originalImageUrl={originalImageUrl}
          onSubmit={mockSubmit}
          status="idle"
          onCancel={mockCancel}
        />
      </TestWrapper>,
    );

    // Find the colors checkbox
    const colorsCheckbox = screen.getByText("Colors").previousElementSibling;

    // Initially, it should not be checked
    expect(colorsCheckbox).not.toBeChecked();

    // Click to select it
    if (colorsCheckbox) {
      fireEvent.click(colorsCheckbox);
    }

    // Now it should be checked
    expect(colorsCheckbox).toBeChecked();

    // Click again to deselect
    if (colorsCheckbox) {
      fireEvent.click(colorsCheckbox);
    }

    // It should be unchecked again
    expect(colorsCheckbox).not.toBeChecked();
  });

  // Test loading state
  test("displays loading state when status is submitting", () => {
    render(
      <TestWrapper>
        <ConceptRefinementForm
          originalImageUrl={originalImageUrl}
          onSubmit={mockSubmit}
          status="submitting"
          onCancel={mockCancel}
        />
      </TestWrapper>,
    );

    // Check for loading state
    const submitButton = screen.getByRole("button", { name: /Processing.../i });
    expect(submitButton).toBeDisabled();

    // Form should be disabled
    const refinementPrompt = screen.getByLabelText("Refinement Instructions");
    expect(refinementPrompt).toBeDisabled();
  });

  // Test error display
  test("displays error message when provided", () => {
    render(
      <TestWrapper>
        <ConceptRefinementForm
          originalImageUrl={originalImageUrl}
          onSubmit={mockSubmit}
          status="error"
          onCancel={mockCancel}
          error="Something went wrong during refinement"
        />
      </TestWrapper>,
    );

    // Check for error message
    const errorMessage = screen.getByText(
      "Something went wrong during refinement",
    );
    expect(errorMessage).toBeInTheDocument();
  });

  // Test cancel button
  test("calls onCancel when cancel button is clicked", () => {
    render(
      <TestWrapper>
        <ConceptRefinementForm
          originalImageUrl={originalImageUrl}
          onSubmit={mockSubmit}
          status="idle"
          onCancel={mockCancel}
        />
      </TestWrapper>,
    );

    // Find and click the cancel button
    const cancelButton = screen.getByRole("button", { name: /Cancel/i });
    fireEvent.click(cancelButton);

    // Verify that the cancel handler was called
    expect(mockCancel).toHaveBeenCalledTimes(1);
  });

  // Test success state
  test("disables form inputs when status is success", () => {
    render(
      <TestWrapper>
        <ConceptRefinementForm
          originalImageUrl={originalImageUrl}
          onSubmit={mockSubmit}
          status="success"
          onCancel={mockCancel}
        />
      </TestWrapper>,
    );

    // Form should be disabled
    const refinementPrompt = screen.getByLabelText("Refinement Instructions");
    expect(refinementPrompt).toBeDisabled();

    // Submit button should be disabled
    const submitButton = screen.getByRole("button", {
      name: /Refine Concept/i,
    });
    expect(submitButton).toBeDisabled();
  });

  // Test snapshot
  test("matches snapshot", () => {
    const { container } = render(
      <TestWrapper>
        <ConceptRefinementForm
          originalImageUrl={originalImageUrl}
          onSubmit={mockSubmit}
          status="idle"
          onCancel={mockCancel}
          initialLogoDescription={initialLogoDescription}
          initialThemeDescription={initialThemeDescription}
        />
      </TestWrapper>,
    );

    expect(container).toMatchSnapshot();
  });
});
