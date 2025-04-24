import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { visualizer } from "rollup-plugin-visualizer";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  return {
    plugins: [
      react(),
      mode === "analyze" &&
        visualizer({
          open: true,
          filename: "dist-analyze/stats.html",
          gzipSize: true,
          brotliSize: true,
        }),
    ],
    build: {
      rollupOptions: {
        output: {
          manualChunks(id) {
            // Group large vendor libraries into a vendor chunk
            if (id.includes("node_modules")) {
              // List core dependencies you want in the vendor chunk
              const vendors = [
                "react",
                "react-dom",
                "react-router",
                "react-router-dom",
                "@tanstack/react-query",
                "@tanstack/query-core",
                "@emotion",
                "@mui", // Group MUI related libs
                "framer-motion",
                "motion-utils",
                "motion-dom", // Group Framer Motion
                "axios",
                "supabase",
                "@supabase", // API clients
                "uuid",
                "js-cookie",
                "use-context-selector", // Utilities
              ];
              // Check if the module ID includes any vendor name
              if (
                vendors.some((vendor) => id.includes(`node_modules/${vendor}`))
              ) {
                return "vendor";
              }
            }
          },
        },
      },
    },
    server: {
      proxy: {
        // Proxy API requests to the backend server
        "/api": {
          target: "http://localhost:8000",
          changeOrigin: true,
          secure: false,
        },
      },
    },
  };
});
