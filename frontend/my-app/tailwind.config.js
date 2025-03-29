/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4F46E5',
        'primary-dark': '#4338CA',
        secondary: '#818CF8',
        'secondary-dark': '#5051DB',
        accent: '#EEF2FF',
        'accent-foreground': '#312E81',
        dark: {
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
          600: '#475569',
          700: '#334155',
          800: '#1E293B',
          900: '#0F172A',
        },
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(to right, var(--tw-gradient-stops))',
        'gradient-secondary': 'linear-gradient(to right, var(--tw-gradient-stops))',
        'gradient-page': 'linear-gradient(to bottom right, var(--tw-gradient-stops))',
      },
      boxShadow: {
        'modern': '0 10px 30px -5px rgba(79, 70, 229, 0.2)',
        'modern-hover': '0 20px 40px -5px rgba(79, 70, 229, 0.3)',
      },
      fontFamily: {
        sans: ['Montserrat', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
} 