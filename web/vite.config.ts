import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  // Varsayılan: doğrudan quiz-service (8001). Gateway ile denemek için:
  // VITE_API_PROXY=http://127.0.0.1:8000 npm run dev
  const apiProxy = env.VITE_API_PROXY || "http://127.0.0.1:8001";

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        "/api": {
          target: apiProxy,
          changeOrigin: true,
          configure(proxy) {
            proxy.on("proxyReq", (proxyReq, req) => {
              const auth = req.headers.authorization;
              if (auth) proxyReq.setHeader("Authorization", auth);
            });
          },
        },
      },
    },
  };
});
