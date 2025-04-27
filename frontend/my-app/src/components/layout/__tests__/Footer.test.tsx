import React from "react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { Footer } from "../Footer";

// Helper function to render with router
const renderWithRouter = (ui: React.ReactElement) => {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
};

describe("Footer Component", () => {
  // Basic rendering tests
  test("renders footer with logo and title", () => {
    renderWithRouter(<Footer />);

    // Check for logo text
    const logo = screen.getByText("CV");
    expect(logo).toBeInTheDocument();

    // Check for title
    const title = screen.getByText("Concept Visualizer");
    expect(title).toBeInTheDocument();
  });

  test("renders tagline", () => {
    renderWithRouter(<Footer />);

    const tagline = screen.getByText(
      "Create and refine visual concepts with AI. Generate unique logos, color schemes, and design assets for your brand and projects.",
    );
    expect(tagline).toBeInTheDocument();
  });

  // Features section tests
  test("renders features section with links", () => {
    renderWithRouter(<Footer />);

    // Check for section title
    const featuresHeading = screen.getByText("Features");
    expect(featuresHeading).toBeInTheDocument();

    // Check for feature links
    const createLink = screen.getByText("Create Concepts");
    const recentLink = screen.getByText("Recent Concepts");
    const refineLink = screen.getByText("Refine Concepts");

    expect(createLink).toBeInTheDocument();
    expect(recentLink).toBeInTheDocument();
    expect(refineLink).toBeInTheDocument();
  });

  // Resources section tests
  test("renders resources section with links", () => {
    renderWithRouter(<Footer />);

    // Check for section title
    const resourcesHeading = screen.getByText("Resources");
    expect(resourcesHeading).toBeInTheDocument();

    // Check for resource links
    const githubLink = screen.getByText("GitHub Repository");
    const jigsawStackLink = screen.getByText("JigsawStack API");

    expect(githubLink).toBeInTheDocument();
    expect(jigsawStackLink).toBeInTheDocument();
  });

  // Check for JigsawStack badge
  test("renders JigsawStack badge", () => {
    renderWithRouter(<Footer />);

    const badge = screen.getByAltText(
      "Powered by JigsawStack. The One API for your next big thing.",
    );
    expect(badge).toBeInTheDocument();
  });

  // Copyright test
  test("renders copyright with current year", () => {
    // Mock current year
    const currentYear = new Date().getFullYear();
    renderWithRouter(<Footer />);

    const copyright = screen.getByText(
      `© ${currentYear} Concept Visualizer. All rights reserved.`,
    );
    expect(copyright).toBeInTheDocument();
  });

  test("renders copyright with custom year", () => {
    renderWithRouter(<Footer year={2025} />);

    const copyright = screen.getByText(
      "© 2025 Concept Visualizer. All rights reserved.",
    );
    expect(copyright).toBeInTheDocument();
  });

  // Replace snapshot tests with more robust structural tests
  describe("Structure and Layout", () => {
    test("footer has correct structural elements", () => {
      const { container } = renderWithRouter(<Footer />);

      // Check for main footer element
      const footer = container.querySelector("footer");
      expect(footer).toBeInTheDocument();

      // Check for key sections
      const linkSections = footer?.querySelectorAll("h3");
      expect(linkSections?.length).toBe(2); // Features and Resources sections
      expect(footer?.querySelector(".border-t")).toBeInTheDocument(); // Has a divider

      // Social links should exist
      const socialLinks = footer?.querySelectorAll("a[aria-label]");
      expect(socialLinks?.length).toBeGreaterThan(0);
    });

    test("footer with custom year has correct structure", () => {
      const { container } = renderWithRouter(<Footer year={2025} />);

      // Check for main footer element
      const footer = container.querySelector("footer");
      expect(footer).toBeInTheDocument();

      // Check for copyright section
      const copyrightSection = footer?.querySelector(".border-t");
      expect(copyrightSection).toBeInTheDocument();

      // Verify year appears in the right section
      expect(copyrightSection?.textContent).toContain("2025");
    });
  });
});
