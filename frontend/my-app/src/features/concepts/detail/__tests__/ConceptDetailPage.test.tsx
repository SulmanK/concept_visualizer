import React from "react";
import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { ConceptDetailPage } from "../ConceptDetailPage";
import { withRoutesWrapper } from "../../../../test-wrappers";

// Mock the concept hooks
vi.mock("../../../../hooks/useConceptQueries", () => ({
  useConceptDetail: vi.fn(),
}));

// Import mocked hook
import { useConceptDetail } from "../../../../hooks/useConceptQueries";

// Mock react-router-dom hooks
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useLocation: () => ({ search: "", pathname: "/concepts/test-123" }),
    useParams: () => ({ conceptId: "test-123" }),
  };
});

// Mock the auth context
vi.mock("../../../../contexts/AuthContext", () => ({
  useAuth: () => ({
    user: { id: "test-user-id", email: "test@example.com" },
    isLoading: false,
    isAuthenticated: true,
  }),
}));

describe("ConceptDetailPage Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("renders loading state initially", () => {
    // Mock the hook to return loading state
    vi.mocked(useConceptDetail).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
      refetch: vi.fn(),
    });

    render(
      withRoutesWrapper(
        ["/concepts/test-123"],
        "/concepts/:conceptId",
        <ConceptDetailPage />,
      ),
    );

    // Check for loading animation element
    const loadingElement = document.querySelector(".animate-pulse");
    expect(loadingElement).toBeInTheDocument();
  });

  test("renders error state when there is an error", () => {
    // Mock the hook to return error state
    vi.mocked(useConceptDetail).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error("Test error"),
      refetch: vi.fn(),
    });

    render(
      withRoutesWrapper(
        ["/concepts/test-123"],
        "/concepts/:conceptId",
        <ConceptDetailPage />,
      ),
    );

    // Check for the error title specifically
    const errorTitle = screen.getByText("Error", { selector: "h2" });
    expect(errorTitle).toBeInTheDocument();

    // Check for the specific error message
    expect(
      screen.getByText("Error loading concept details"),
    ).toBeInTheDocument();
  });
});
