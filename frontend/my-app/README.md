# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config({
  extends: [
    // Remove ...tseslint.configs.recommended and replace with this
    ...tseslint.configs.recommendedTypeChecked,
    // Alternatively, use this for stricter rules
    ...tseslint.configs.strictTypeChecked,
    // Optionally, add this for stylistic rules
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config({
  plugins: {
    // Add the react-x and react-dom plugins
    'react-x': reactX,
    'react-dom': reactDom,
  },
  rules: {
    // other rules...
    // Enable its recommended typescript rules
    ...reactX.configs['recommended-typescript'].rules,
    ...reactDom.configs.recommended.rules,
  },
})
```

## Testing Framework

### Unit Tests
Unit tests are written using Vitest and React Testing Library. They can be run with:

```bash
npm test
```

### End-to-End Tests
End-to-End tests are implemented with Playwright. They simulate user interaction with the application in a real browser environment.

To run the E2E tests:

```bash
npm run test:e2e
```

To run with the Playwright UI mode (for debugging):

```bash
npm run test:e2e:ui
```

### Visual Regression Tests
Visual regression tests capture screenshots of key pages and UI elements to detect unexpected visual changes.

To run visual regression tests:

```bash
npm run test:visual
```

If UI changes are intentional, update the reference screenshots:

```bash
npm run test:visual:update
```

### Accessibility Tests
Accessibility tests verify that the application meets WCAG accessibility standards using axe-core.

To run accessibility tests:

```bash
npm run test:a11y
```

To run with the Playwright UI mode (for debugging):

```bash
npm run test:a11y:ui
```

Accessibility tests check for:
- WCAG 2.0 A and AA compliance
- Proper labeling of form elements
- Sufficient color contrast
- Keyboard navigability

### API Mock Service
For integration testing, we use a mock API service that simulates backend responses. This is available in:

```
src/mocks/mockApiService.ts
src/mocks/mockHooks.ts
```

The mock service can be imported and configured in tests to provide consistent test data without requiring a real backend connection.
