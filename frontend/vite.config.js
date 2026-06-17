import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// bypass retorna "/index.html" para requisições de navegação do browser
// (Accept: text/html), impedindo que o proxy intercepte rotas do React Router.
function apiOnly(req) {
  if (req.headers.accept?.includes("text/html")) return "/index.html";
}

const BACKEND = "http://localhost:5001";
const proxyRoute = (target = BACKEND) => ({ target, bypass: apiOnly });

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/auth": proxyRoute(),
      "/produtos": proxyRoute(),
      "/garantias": proxyRoute(),
      "/categorias": proxyRoute(),
      "/comprovantes": proxyRoute(),
      "/notificacoes": proxyRoute(),
      "/relatorios": proxyRoute(),
      "/usuarios": proxyRoute(),
      "/uploads": proxyRoute(),
      "/health": proxyRoute(),
    },
  },
});
