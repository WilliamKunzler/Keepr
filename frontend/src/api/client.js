import axios from "axios";

export const API_BASE = import.meta.env.VITE_API_URL || "";

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Monta a URL absoluta de um asset servido pelo backend (ex.: /uploads/<arquivo>).
 * Em dev o baseURL é vazio e o proxy do Vite cuida; em produção prefixa o backend
 * (Render), senão o <img> tentaria carregar do domínio da Vercel e daria 404.
 */
export function assetUrl(path) {
  if (!path) return path;
  if (/^https?:\/\//i.test(path)) return path;
  const base = API_BASE.replace(/\/$/, ""); // evita //uploads se a env vier com barra final
  return `${base}${path}`;
}

const TOKEN_KEY = "keepr_access_token";
const REFRESH_KEY = "keepr_refresh_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setTokens({ access_token, refresh_token }) {
  if (access_token) localStorage.setItem(TOKEN_KEY, access_token);
  if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token);
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearTokens();
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  },
);

export async function pingBackend() {
  try {
    const { data } = await api.get("/health");
    return data?.status === "ok";
  } catch {
    return false;
  }
}
