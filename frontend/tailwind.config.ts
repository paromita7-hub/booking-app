import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F8FAFC",
        foreground: "#0F172A",
        primary: {
          DEFAULT: "#1E3A8A", // Deep Navy
          foreground: "#FFFFFF",
          hover: "#1D4ED8",
          light: "#EFF6FF",
        },
        accent: {
          DEFAULT: "#0284C7", // Sky Blue accent
          foreground: "#FFFFFF",
        },
        card: {
          DEFAULT: "#FFFFFF",
          foreground: "#0F172A",
        },
        border: "#E2E8F0",
        muted: {
          DEFAULT: "#64748B",
          foreground: "#94A3B8",
          background: "#F1F5F9",
        },
        positive: {
          DEFAULT: "#15803D",
          light: "#DCFCE7",
          border: "#86EFAC",
        },
        negative: {
          DEFAULT: "#B91C1C",
          light: "#FEE2E2",
          border: "#FCA5A5",
        },
        warning: {
          DEFAULT: "#B45309",
          light: "#FEF3C7",
          border: "#FCD34D",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
