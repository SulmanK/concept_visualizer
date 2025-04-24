import React from "react";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { RecentConceptsPage } from "../RecentConceptsPage";
import { vi } from "vitest";

// Mock the ConceptList component
vi.mock("../components/ConceptList", () => ({
  ConceptList: () => <div data-testid="concept-list">Mocked Concept List</div>,
}));

// Mock the RecentConceptsHeader component
vi.mock("../components/RecentConceptsHeader", () => ({
  RecentConceptsHeader: () => (
    <div data-testid="recent-concepts-header">Mocked Header</div>
  ),
}));

describe("RecentConceptsPage Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("renders the header and concept list", () => {
    render(
      <BrowserRouter>
        <RecentConceptsPage />
      </BrowserRouter>,
    );

    // Check that the header is rendered
    expect(screen.getByTestId("recent-concepts-header")).toBeInTheDocument();

    // Check that the concept list is rendered
    expect(screen.getByTestId("concept-list")).toBeInTheDocument();
  });
});
