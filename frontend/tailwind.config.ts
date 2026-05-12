import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#050816",
        surface: "#0d1324",
        surfaceAlt: "#10192f",
        border: "#22304e",
        accent: "#7dd3fc",
        accentStrong: "#38bdf8",
        text: "#f8fafc",
        muted: "#94a3b8",
      },
      boxShadow: {
        glow: "0 20px 80px rgba(56, 189, 248, 0.18)",
      },
      backgroundImage: {
        hero: "radial-gradient(circle at top, rgba(56, 189, 248, 0.22), transparent 35%), linear-gradient(180deg, #07101f 0%, #050816 60%, #03060f 100%)",
      },
    },
  },
  plugins: [],
} satisfies Config;

