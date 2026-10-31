/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        parliament: {
          green: '#005C2B',
          'green-light': '#008740',
          'green-dark': '#00431F',
          gold: '#CBA135',
          'gold-light': '#E2BE5E',
          'gold-dark': '#A88225',
          red: '#BB2B2B',
          black: '#111827'
        }
      }
    },
  },
  plugins: [],
}
