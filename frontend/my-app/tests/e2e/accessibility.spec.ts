import { test, expect } from "./fixtures";
import AxeBuilder from "@axe-core/playwright";

/**
 * Accessibility tests using axe-core to check for WCAG compliance
 * These tests ensure the application meets accessibility standards
 */

test.describe("Accessibility", () => {
  test("home page should not have accessibility violations", async ({
    page,
  }) => {
    await page.goto("/");

    // Analyze the page for accessibility issues
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa"]) // Check WCAG 2.0 A and AA rules
      .analyze();

    // Log the number of violations for debugging (even if test passes)
    console.log(
      `Found ${accessibilityScanResults.violations.length} accessibility violations`,
    );

    // Expect no violations
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test("concept generation page should not have accessibility violations", async ({
    page,
  }) => {
    await page.goto("/create");

    // Analyze the page for accessibility issues
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa"])
      .analyze();

    // Log the number of violations for debugging
    console.log(
      `Found ${accessibilityScanResults.violations.length} accessibility violations`,
    );

    // Expect no violations
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test("concept refinement page should not have accessibility violations", async ({
    page,
  }) => {
    await page.goto("/refine/test-concept-123");

    // Analyze the page for accessibility issues
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa"])
      .analyze();

    // Log the number of violations for debugging
    console.log(
      `Found ${accessibilityScanResults.violations.length} accessibility violations`,
    );

    // Expect no violations
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test("form elements should have proper labels and ARIA attributes", async ({
    page,
  }) => {
    await page.goto("/create");

    // Check that all form elements have associated labels
    const inputs = await page.locator("input, textarea, select").all();

    for (const input of inputs) {
      // Get input ID
      const id = await input.getAttribute("id");
      if (id) {
        // Check for associated label
        const label = await page.locator(`label[for="${id}"]`).count();
        expect(
          label,
          `Input with ID ${id} should have an associated label`,
        ).toBeGreaterThan(0);
      } else {
        // If no ID, it should be wrapped in a label or have aria-label
        const parentLabel = await input
          .locator("xpath=./ancestor::label")
          .count();
        const ariaLabel = await input.getAttribute("aria-label");
        const ariaLabelledBy = await input.getAttribute("aria-labelledby");

        expect(
          parentLabel > 0 || ariaLabel !== null || ariaLabelledBy !== null,
          "Input should have a label or appropriate ARIA attributes",
        ).toBeTruthy();
      }
    }
  });

  test("interactive elements have sufficient color contrast", async ({
    page,
  }) => {
    await page.goto("/");

    // Run a specific check for color contrast
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(["color-contrast"])
      .analyze();

    // Log any specific contrast issues for debugging
    if (accessibilityScanResults.violations.length > 0) {
      for (const violation of accessibilityScanResults.violations) {
        console.log(`Contrast issue: ${violation.description}`);
        for (const node of violation.nodes) {
          console.log(`  - ${node.html}`);
        }
      }
    }

    // Expect no color contrast violations
    expect(accessibilityScanResults.violations).toEqual([]);
  });
});
