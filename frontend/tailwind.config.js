/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Source Sans 3"', 'Inter', 'system-ui', 'sans-serif'],
        serif: ['"Source Serif 4"', 'Georgia', 'serif'],
      },
      colors: {
        parliament: {
          green: '#0B4D2C',
          'green-light': '#1F7A45',
          'green-dark': '#08361F',
          gold: '#C4A35A',
          'gold-light': '#E4C98A',
          'gold-dark': '#8C7030',
          red: '#9E2B2B',
          black: '#101612',
          ink: '#16241C',
          paper: '#F4F6F2'
        }
      },
      boxShadow: {
        card: '0 1px 2px rgba(16, 36, 24, 0.04), 0 16px 40px -24px rgba(11, 61, 36, 0.45)',
      }
    },
  },
  plugins: [],
}
