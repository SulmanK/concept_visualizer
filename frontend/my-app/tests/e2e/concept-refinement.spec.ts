import { test, expect } from "./fixtures";

/**
 * End-to-end test for the concept refinement flow.
 * Tests the full user journey of refining a concept:
 * 1. Navigate to the refinement page with a concept ID
 * 2. Verify the original concept is displayed
 * 3. Fill out the refinement form
 * 4. Submit the form
 * 5. Verify the refined concept appears
 * 6. Save the refined concept
 */
test("concept refinement flow", async ({ page }) => {
  // Navigate directly to the refinement page with a concept ID
  await page.goto("/refine/test-concept-123");

  // Verify we're on the refinement page
  await expect(
    page.getByRole("heading", { name: /Refine Your Concept/i }),
  ).toBeVisible();

  // Verify the original concept is displayed
  const originalImage = page.getByAltText(/Original concept/i);
  await expect(originalImage).toBeVisible();
  await expect(originalImage).toHaveAttribute(
    "src",
    "https://example.com/original-concept.png",
  );

  // Fill out the refinement form
  await page
    .getByLabel(/Refinement Instructions/i)
    .fill("Make it more vibrant with brighter colors");

  // Select preservation options
  await page.getByLabel(/Preserve color scheme/i).check();

  // Submit the form
  await page.getByRole("button", { name: /Refine Concept/i }).click();

  // Wait for the loading state to appear and then disappear
  await expect(page.getByText(/Refining your concept/i)).toBeVisible();
  await expect(page.getByText(/Refining your concept/i)).not.toBeVisible({
    timeout: 10000,
  });

  // Verify both original and refined concepts are displayed
  await expect(page.getByText(/Original Concept/i)).toBeVisible();
  await expect(page.getByText(/Refined Concept/i)).toBeVisible();

  // Verify the refined image is displayed
  const refinedImage = page.getByAltText(/Refined concept/i);
  await expect(refinedImage).toBeVisible();
  await expect(refinedImage).toHaveAttribute(
    "src",
    "https://example.com/refined-concept.png",
  );

  // Check that the color palette is displayed for the refined concept
  await expect(page.getByText(/Primary/i).first()).toBeVisible();

  // Save the refined concept
  await page.getByRole("button", { name: /Save Refined Concept/i }).click();

  // Verify we're redirected to the home page after saving
  await expect(page).toHaveURL("/");
});
