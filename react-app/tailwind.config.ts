/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./utils/**/*.{ts,tsx}",
    "./types/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Apercu Std",
          "-apple-system",
          "BlinkMacSystemFont",
          "Avenir Next",
          "Avenir",
          "Segoe UI",
          "Helvetica Neue",
          "Helvetica",
          "Ubuntu",
          "Roboto",
          "Noto",
          "Arial",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
