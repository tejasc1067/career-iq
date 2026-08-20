import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

// No @vitejs/plugin-react: Vite's built-in JSX transform covers the tests, and
// the plugin's Babel 8 peer conflicts with the shadcn CLI's Babel 7 pin.
export default defineConfig({
  resolve: {
    alias: { "@": fileURLToPath(new URL("./", import.meta.url)) },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
    include: ["tests/**/*.test.{ts,tsx}"],
  },
});
