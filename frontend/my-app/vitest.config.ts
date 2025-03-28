import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/setupTests.ts'],
    mockReset: true,
    css: true,
    clearMocks: true,
    cache: false,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      exclude: ['node_modules/']
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  }
}); 