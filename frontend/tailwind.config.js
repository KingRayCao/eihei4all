/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        surface: '#1e2030',
        panel: '#252839',
        border: '#2e3250',
        accent: '#818cf8',
        'accent-dark': '#6366f1',
      },
    },
  },
  plugins: [],
}
