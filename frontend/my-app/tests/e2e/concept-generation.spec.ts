import { test, expect } from "./fixtures";

/**
 * End-to-end test for the concept generation flow.
 * Tests the full user journey of generating a concept:
 * 1. Navigate to the home page
 * 2. Go to the concept generation page
 * 3. Fill out the form with logo and theme descriptions
 * 4. Submit the form
 * 5. Verify the generated concept appears
 */
test("concept generation flow", async ({ page, mockApi }) => {
  // Navigate to the home page
  await page.goto("/");

  // Verify the page has loaded correctly
  await expect(page).toHaveTitle(/Concept Visualizer/);

  // Click on the "Create Concept" link/button to navigate to the concept generation page
  await page.getByRole("link", { name: /Create/ }).click();

  // Verify we're on the concept generation page
  await expect(
    page.getByRole("heading", { name: /Create Visual Concepts/ }),
  ).toBeVisible();

  // Fill out the form
  await page
    .getByLabel(/Logo Description/i)
    .fill("Modern tech logo with abstract shapes");
  await page
    .getByLabel(/Theme Description/i)
    .fill("Gradient indigo color scheme with clean design");

  // Submit the form
  await page.getByRole("button", { name: /Generate Concept/i }).click();

  // Wait for the loading state to appear and then disappear (indicating the request has completed)
  await expect(page.getByText(/Generating your concept/i)).toBeVisible();
  await expect(page.getByText(/Generating your concept/i)).not.toBeVisible({
    timeout: 10000,
  });

  // Verify the generated concept appears
  await expect(page.getByText(/Your Generated Concept/i)).toBeVisible();

  // Verify the image is displayed
  const conceptImage = page.getByAltText(/Generated concept image/i);
  await expect(conceptImage).toBeVisible();
  await expect(conceptImage).toHaveAttribute(
    "src",
    "https://example.com/mock-concept.png",
  );

  // Verify the color palette is displayed
  await expect(page.getByText(/Color Palette/i)).toBeVisible();

  // Verify action buttons are present
  await expect(
    page.getByRole("button", { name: /Refine This Concept/i }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /Download Image/i }),
  ).toBeVisible();
});
