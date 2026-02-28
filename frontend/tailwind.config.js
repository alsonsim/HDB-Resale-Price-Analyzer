/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#eff6ff",
          100: "#dbeafe",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
        },
        hdb: {
          blue: "#003d7c",
          teal: "#00897b",
          orange: "#f57c00",
        },
      },
    },
  },
  plugins: [],
};
