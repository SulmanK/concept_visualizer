import { test, expect } from './fixtures';

/**
 * Tests for responsive design across different viewport sizes.
 * Verifies that the application layout adapts correctly to different screen sizes.
 */

// Desktop viewport test
test('responsive design - desktop', async ({ page }) => {
  // Set viewport to a desktop size
  await page.setViewportSize({ width: 1280, height: 800 });
  
  // Navigate to the home page
  await page.goto('/');
  
  // Verify the header layout is correct for desktop
  await expect(page.locator('header')).toBeVisible();
  await expect(page.getByRole('link', { name: /Create/ })).toBeVisible();
  await expect(page.getByRole('link', { name: /Refine/ })).toBeVisible();

  // Verify the main content layout
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
  
  // Verify that the "How It Works" section has the correct layout
  const howItWorksSection = page.getByText(/How It Works/).first();
  await expect(howItWorksSection).toBeVisible();
  
  // Check if the features are displayed in a row (grid) on desktop
  const featuresGrid = page.locator('.grid').filter({ hasText: /How It Works/ });
  await expect(featuresGrid).toBeVisible();
  
  // Verify the grid has the desktop class (could be grid-cols-3, lg:grid-cols-3, etc.)
  const gridClasses = await featuresGrid.getAttribute('class');
  expect(gridClasses).toMatch(/grid-cols-3|lg:grid-cols-3|md:grid-cols-3/);
});

// Tablet viewport test
test('responsive design - tablet', async ({ page }) => {
  // Set viewport to a tablet size
  await page.setViewportSize({ width: 768, height: 1024 });
  
  // Navigate to the home page
  await page.goto('/');
  
  // Verify the header layout adapts for tablet
  await expect(page.locator('header')).toBeVisible();
  
  // Verify the main content layout for tablet
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
  
  // Check layouts specific to tablet viewport
  const howItWorksSection = page.getByText(/How It Works/).first();
  await expect(howItWorksSection).toBeVisible();
});

// Mobile viewport test
test('responsive design - mobile', async ({ page }) => {
  // Set viewport to a mobile size
  await page.setViewportSize({ width: 375, height: 667 });
  
  // Navigate to the home page
  await page.goto('/');
  
  // Verify the header layout adapts for mobile
  await expect(page.locator('header')).toBeVisible();
  
  // Check for mobile menu button if present
  const mobileMenuButton = page.getByRole('button', { name: /menu/i });
  if (await mobileMenuButton.count() > 0) {
    // If there's a mobile menu button, test the mobile menu functionality
    await mobileMenuButton.click();
    
    // Verify navigation links are now visible
    await expect(page.getByRole('link', { name: /Create/ })).toBeVisible();
    await expect(page.getByRole('link', { name: /Refine/ })).toBeVisible();
  } else {
    // If no mobile menu button, navigation should still be accessible somehow
    await expect(page.getByRole('link', { name: /Create/ })).toBeVisible();
  }
  
  // Verify the feature grid has stacked to a single column on mobile
  const featuresGrid = page.locator('.grid').filter({ hasText: /How It Works/ });
  const gridClasses = await featuresGrid.getAttribute('class');
  
  // Verify it doesn't have desktop grid classes or has mobile-specific grid classes
  expect(gridClasses).not.toMatch(/grid-cols-3|lg:grid-cols-3|md:grid-cols-3/);
  expect(gridClasses).toMatch(/grid-cols-1|sm:grid-cols-1/);
}); 