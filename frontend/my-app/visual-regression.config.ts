import { defineConfig, devices } from '@playwright/test';

/**
 * Specialized configuration for visual regression tests
 * This config extends the base configuration with settings optimized for visual testing
 */
export default defineConfig({
  // Look for visual regression tests
  testDir: './tests/e2e',
  testMatch: '**/*visual-regression.spec.ts',

  // Longer timeout for visual tests
  timeout: 60000,

  // Generate a report after tests finish
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/visual-regression-results.json' }]
  ],

  // Run tests in files in parallel
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry failed visual tests to reduce flakiness
  retries: process.env.CI ? 2 : 0,

  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,

  // Store snapshots in a dedicated directory
  snapshotPathTemplate: '{testDir}/__snapshots__/{testFilePath}/{arg}{ext}',

  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Consistent viewport size for visual tests
        viewport: { width: 1280, height: 720 },
        // Reduce visual noise in screenshots
        colorScheme: 'light',
        // Mask any time or date elements that may cause false positives
        maskColor: '#FF00FF',
      },
    },
  ],

  // Web server to test against
  webServer: {
    command: 'npm run build && npm run preview',
    port: 4173,
    reuseExistingServer: !process.env.CI,
  },

  // Configure the directory where Playwright will store screenshots etc
  outputDir: 'test-results/visual-regression/',

  // Custom expect options specifically for visual tests
  expect: {
    toHaveScreenshot: {
      // Default threshold for screenshot comparisons - 0.2% pixel difference is allowed
      threshold: 0.2,
      // Store screenshots in a dedicated directory
      snapshotDir: './tests/e2e/__snapshots__'
    }
  }
}); 