import { useState } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";

import { Button } from "../components/Button";
import { Field, Input } from "../components/Field";
import { useAuth } from "../contexts/AuthContext";

export function Login() {
  const { login, usuario } = useAuth();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState(null);
  const [carregando, setCarregando] = useState(false);

  if (usuario) return <Navigate to={location.state?.from || "/"} replace />;

  async function onSubmit(e) {
    e.preventDefault();
    setErro(null);
    setCarregando(true);
    try {
      await login(email, senha);
    } catch (err) {
      setErro(err.response?.data?.erro || "Erro ao entrar");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="px-6 py-4">
        <Link to="/" className="font-display text-lg font-semibold text-ink-900 tracking-tight">Keepr</Link>
      </header>

      <main className="flex-1 flex items-center justify-center px-6 -mt-10">
        <div className="w-full max-w-sm">
          <h1 className="font-display text-2xl font-semibold text-ink-900 tracking-tight mb-1">
            Entrar
          </h1>
          <p className="text-sm text-ink-500 mb-6">Acesse sua conta para continuar.</p>

          <form onSubmit={onSubmit} className="space-y-3">
            <Field label="E-mail">
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                placeholder="voce@exemplo.com"
              />
            </Field>
            <Field label="Senha" error={erro}>
              <Input
                type="password"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                required
                autoComplete="current-password"
              />
            </Field>

            <Button type="submit" disabled={carregando} className="w-full">
              {carregando ? "Entrando…" : "Entrar"}
            </Button>
          </form>

          <p className="mt-5 text-xs text-ink-500 text-center">
            Ainda não tem conta?{" "}
            <Link to="/registro" className="text-ink-900 underline underline-offset-4 hover:text-amber-accent">
              criar conta
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
