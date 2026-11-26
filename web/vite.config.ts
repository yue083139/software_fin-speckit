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
    // antd 在 jsdom 首次渲染要 5–11 秒（樣式注入與元件初始化），預設 5 秒會時綠時紅（web-workbench 評審）
    testTimeout: 30000,
    hookTimeout: 30000,
  },
});
