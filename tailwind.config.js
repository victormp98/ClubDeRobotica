/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        /* Primary — Indigo (LotOS signature) */
        brand: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          900: '#312e81',
        },
        /* Accent — Teal */
        accent: {
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
        },
        /* Premium — Rose/Pink */
        premium: {
          400: '#f472b6',
          500: '#ec4899',
        },
        /* Surfaces */
        dark: {
          800: '#161b22',
          900: '#0d1117',
          950: '#070711',
        }
      },
      fontFamily: {
        sans:    ['Inter', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
