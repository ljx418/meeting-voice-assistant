import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const bffTarget = process.env.VITE_BFF_PROXY_TARGET || "http://127.0.0.1:18040";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
      "/bff": bffTarget,
    },
  },
  preview: {
    port: 4174,
    proxy: {
      "/bff": bffTarget,
    },
  },
});
