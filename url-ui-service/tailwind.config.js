/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Poppins', 'sans-serif'],
        mono: ['Roboto Mono', 'monospace'],
      },
      colors: {
        'custom-white': '#F5F5F5', // Example of a custom white color
        'custom-blue': '#007BFF', // Blue color
        'custom-black': '#0A0A0A', // Black color
        'custom-dark-gray': '#141414', // Dark gray
        'custom-light-gray': '#D1D5DB', // Light gray text color
        'custom-yellow': '#FFD700', // Yellow for buttons or highlights
        'custom-grey': '#333333', // Grey color
        'custom-red': '#FF5733', // Glossy red for buttons
      },
      backgroundImage: {
        'black-gradient': 'linear-gradient(135deg, rgb(20, 1, 1), #141414)', // Black gradient background
        'custom-gradient': 'linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.03))', // Subtle gradient
      },
      boxShadow: {
        'custom-glow': '0 8px 32px rgba(0, 0, 0, 0.36)', // Soft glow effect
        'glossy-glow': '0 8px 15px rgba(255, 87, 51, 0.6)', // Glossy red glow for button
      },
      fontSize: {
        'xxl': '2rem', // Larger font size for headings/titles
      },
    },
  },
  plugins: [],
};
