/// <reference types="vitest/config" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// 開發時由 Vite 代理到本機 server；正式 Demo 由 server 直接提供 web/dist（app-skeleton D1）
const SERVER = `http://127.0.0.1:${process.env.QUIZ_SERVER_PORT ?? "8000"}`;

export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": { target: SERVER, changeOrigin: true },
      "/ws": { target: SERVER.replace("http", "ws"), ws: true },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test-setup.ts"],
  },
});
