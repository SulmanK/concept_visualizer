import { defineConfig, devices } from '@playwright/test';

/**
 * Specialized configuration for accessibility tests
 */
export default defineConfig({
  // Look for accessibility tests
  testDir: './tests/e2e',
  testMatch: '**/*accessibility.spec.ts',

  // Longer timeout for accessibility tests that may take longer to analyze
  timeout: 60000,

  // Generate a report after tests finish
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/accessibility-results.json' }]
  ],

  // Run tests in files in parallel
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry failed accessibility tests
  retries: process.env.CI ? 2 : 0,

  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
      },
    },
    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
      },
    },
    {
      name: 'webkit',
      use: { 
        ...devices['Desktop Safari'],
      },
    },
  ],

  // Web server to test against
  webServer: {
    command: 'npm run build && npm run preview',
    port: 4173,
    reuseExistingServer: !process.env.CI,
  },

  // Configure the directory where Playwright will store results
  outputDir: 'test-results/accessibility/',
}); 