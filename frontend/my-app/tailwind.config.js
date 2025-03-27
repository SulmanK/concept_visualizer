/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f3eeff',
          100: '#e4dbfc',
          200: '#cbbaf9',
          300: '#ab8ef4',
          400: '#9162ef',
          500: '#7b3fe7',
          600: '#6c23db',
          700: '#5b1bbe',
          800: '#4b1a99',
          900: '#3d1b77',
          950: '#270f4c',
        },
        secondary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#b9e5fe',
          300: '#7cd2fd',
          400: '#36b9fa',
          500: '#0ca1ec',
          600: '#0080ca',
          700: '#0167a2',
          800: '#065786',
          900: '#0b4a70',
          950: '#072f4b',
        },
        accent: {
          50: '#fff1f2',
          100: '#ffe0e2',
          200: '#ffc6cb',
          300: '#ff9da5',
          400: '#ff6976',
          500: '#fa374a',
          600: '#e61b31',
          700: '#c1142a',
          800: '#a0162a',
          900: '#87192b',
          950: '#490811',
        },
        dark: {
          50: '#f6f6f9',
          100: '#edeef3',
          200: '#d8dae4',
          300: '#b6becb',
          400: '#8f99ae',
          500: '#707b93',
          600: '#5a6479',
          700: '#485163',
          800: '#3d4454',
          900: '#363c49',
          950: '#24272f',
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(var(--tw-gradient-stops))',
        'gradient-primary': 'linear-gradient(to right, #6c23db, #e61b31)',
      },
      boxShadow: {
        'glow': '0 0 15px rgba(123, 63, 231, 0.5)',
        'glow-accent': '0 0 15px rgba(250, 55, 74, 0.5)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
} 