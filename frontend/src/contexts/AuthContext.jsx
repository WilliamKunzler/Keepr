import { createContext, useCallback, useContext, useEffect, useState } from "react";

import { auth as authApi } from "../api/endpoints";
import { clearTokens, getToken, setTokens } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelado = false;
    async function carregar() {
      if (!getToken()) {
        setLoading(false);
        return;
      }
      try {
        const u = await authApi.me();
        if (!cancelado) setUsuario(u);
      } catch {
        clearTokens();
      } finally {
        if (!cancelado) setLoading(false);
      }
    }
    carregar();
    return () => {
      cancelado = true;
    };
  }, []);

  const login = useCallback(async (email, senha) => {
    const data = await authApi.login(email, senha);
    setTokens(data);
    setUsuario(data.usuario);
    return data.usuario;
  }, []);

  const registro = useCallback(async (dados) => {
    await authApi.registro(dados);
    return login(dados.email, dados.senha);
  }, [login]);

  const logout = useCallback(() => {
    clearTokens();
    setUsuario(null);
  }, []);

  const value = { usuario, loading, login, registro, logout, isAdmin: usuario?.tipo === "admin" };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth precisa estar dentro do AuthProvider");
  return ctx;
}
