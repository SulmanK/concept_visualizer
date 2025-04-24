import { test as base, Page } from "@playwright/test";

/**
 * Custom test fixture that includes common test setup and teardown operations.
 * This helps avoid duplicating code across test files.
 */
export const test = base.extend({
  /**
   * Sets up API mocking for both generation and refinement endpoints.
   */
  mockApi: async ({ page }, use) => {
    // Setup API route mocking for concept generation
    await page.route("**/api/concepts/generate", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          imageUrl: "https://example.com/mock-concept.png",
          colorPalette: {
            primary: "#4F46E5",
            secondary: "#818CF8",
            accent: "#C4B5FD",
            background: "#F5F3FF",
            text: "#1E1B4B",
          },
          generationId: "mock-gen-123",
          createdAt: new Date().toISOString(),
        }),
      });
    });

    // Setup API route mocking for concept refinement
    await page.route("**/api/concepts/refine", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          imageUrl: "https://example.com/refined-concept.png",
          colorPalette: {
            primary: "#6366F1",
            secondary: "#A5B4FC",
            accent: "#E0E7FF",
            background: "#EEF2FF",
            text: "#312E81",
          },
          generationId: "refined-concept-123",
          createdAt: new Date().toISOString(),
          originalImageUrl: "https://example.com/original-concept.png",
          refinementPrompt:
            route.request().postDataJSON().refinementPrompt ||
            "Make it more vibrant",
        }),
      });
    });

    await use();
  },

  /**
   * Sets up mock saved concepts in localStorage.
   */
  mockLocalStorage: async ({ page }, use) => {
    await page.addInitScript(() => {
      const mockConcepts = [
        {
          imageUrl: "https://example.com/original-concept.png",
          colorPalette: {
            primary: "#4F46E5",
            secondary: "#818CF8",
            accent: "#C4B5FD",
            background: "#F5F3FF",
            text: "#1E1B4B",
          },
          generationId: "test-concept-123",
          createdAt: new Date().toISOString(),
        },
      ];

      localStorage.setItem("savedConcepts", JSON.stringify(mockConcepts));
    });

    await use();
  },
});

/**
 * Re-export expect to avoid having to import it separately
 */
export { expect } from "@playwright/test";
