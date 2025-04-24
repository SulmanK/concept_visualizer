import { test, expect } from "./fixtures";

/**
 * Visual regression tests for key pages.
 * These tests take screenshots of key pages and compare them to reference screenshots.
 * References are automatically generated on first run, and future runs will compare
 * against these references to detect visual changes.
 */

// Helper function to stabilize dynamic content before taking screenshots
async function stabilizePage(page) {
  // Wait for any animations to complete
  await page.waitForTimeout(500);

  // Hide date/time elements that would cause false positives
  await page.addStyleTag({
    content: `
      [data-testid="date"],
      [data-testid="time"],
      .dynamic-content {
        visibility: hidden !important;
      }
    `,
  });
}

test("visual regression - home page", async ({ page, mockApi }) => {
  // Navigate to the home page
  await page.goto("/");

  // Stabilize the page before taking screenshots
  await stabilizePage(page);

  // Take a screenshot of the entire page
  await expect(page).toHaveScreenshot("home-page.png", {
    fullPage: true,
    threshold: 0.2, // Allow for small differences (2%)
  });
});

test("visual regression - concept generation page", async ({
  page,
  mockApi,
}) => {
  // Navigate to the concept generation page
  await page.goto("/create");

  // Stabilize the page before taking screenshots
  await stabilizePage(page);

  // Take a screenshot of the form
  await expect(page.locator("form")).toHaveScreenshot("concept-form.png", {
    threshold: 0.2,
  });

  // Fill out the form
  await page
    .getByLabel(/Logo Description/i)
    .fill("Modern tech logo with abstract shapes");
  await page
    .getByLabel(/Theme Description/i)
    .fill("Gradient indigo color scheme with clean design");

  // Submit the form
  await page.getByRole("button", { name: /Generate Concept/i }).click();

  // Wait for the result to appear
  await expect(page.getByText(/Your Generated Concept/i)).toBeVisible();

  // Stabilize the page again
  await stabilizePage(page);

  // Take a screenshot of the result
  await expect(page.locator("main")).toHaveScreenshot("concept-result.png", {
    threshold: 0.2,
  });
});

test("visual regression - refinement page", async ({
  page,
  mockApi,
  mockLocalStorage,
}) => {
  // Navigate to the refinement page
  await page.goto("/refine/test-concept-123");

  // Stabilize the page before taking screenshots
  await stabilizePage(page);

  // Take a screenshot of the refinement form
  await expect(page.locator("main")).toHaveScreenshot("refinement-page.png", {
    threshold: 0.2,
  });

  // Fill out the form
  await page
    .getByLabel(/Refinement Instructions/i)
    .fill("Make it more vibrant with brighter colors");

  // Select preservation options
  await page.getByLabel(/Preserve color scheme/i).check();

  // Submit the form
  await page.getByRole("button", { name: /Refine Concept/i }).click();

  // Wait for the result to appear
  await expect(page.getByAltText(/Refined concept/i)).toBeVisible();

  // Stabilize the page again
  await stabilizePage(page);

  // Take a screenshot of the comparison view
  await expect(page.locator("main")).toHaveScreenshot("refinement-result.png", {
    threshold: 0.2,
  });
});
