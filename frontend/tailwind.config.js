/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Paleta Keepr — cream, carvão, âmbar como acento
        cream: {
          50: "#FAF6EF",
          100: "#F5EFE6",
          200: "#EBE2D3",
        },
        ink: {
          900: "#1C1B1A",
          800: "#2B2A28",
          700: "#3C3A37",
          500: "#6B6862",
          400: "#8A8278",
          300: "#B4B2A9",
        },
        amber: {
          accent: "#C84F1C",
          soft: "#E8A77D",
        },
        // Status de produtos
        status: {
          ativa: "#1D9E75",
          vencendo: "#BA7517",
          vencida: "#A32D2D",
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', "ui-sans-serif", "system-ui", "sans-serif"],
        sans: ['"IBM Plex Sans"', "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ['"IBM Plex Mono"', "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};
