/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx}', './public/index.html'],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#4A154B',
          dark: '#3E0E40',
        },
        bullish: '#00c805',
        bearish: '#ff3b30',
      },
    },
  },
  plugins: [],
};
