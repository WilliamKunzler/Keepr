import { useState } from "react";
import { Link, Navigate } from "react-router-dom";

import { Button } from "../components/Button";
import { Field, Input } from "../components/Field";
import { useAuth } from "../contexts/AuthContext";

export function Registro() {
  const { registro, usuario } = useAuth();
  const [form, setForm] = useState({ nome: "", email: "", senha: "", telefone: "" });
  const [erro, setErro] = useState(null);
  const [carregando, setCarregando] = useState(false);

  if (usuario) return <Navigate to="/" replace />;

  function set(k) { return (e) => setForm({ ...form, [k]: e.target.value }); }

  async function onSubmit(e) {
    e.preventDefault();
    setErro(null);
    setCarregando(true);
    try {
      await registro(form);
    } catch (err) {
      setErro(err.response?.data?.erro || "Erro ao criar conta");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="px-6 py-4">
        <Link to="/" className="font-display text-lg font-semibold text-ink-900 tracking-tight">Keepr</Link>
      </header>

      <main className="flex-1 flex items-center justify-center px-6 py-6">
        <div className="w-full max-w-sm">
          <h1 className="font-display text-2xl font-semibold text-ink-900 tracking-tight mb-1">
            Criar conta
          </h1>
          <p className="text-sm text-ink-500 mb-6">Leva menos de um minuto.</p>

          <form onSubmit={onSubmit} className="space-y-3">
            <Field label="Nome">
              <Input value={form.nome} onChange={set("nome")} required autoComplete="name" />
            </Field>
            <Field label="E-mail">
              <Input type="email" value={form.email} onChange={set("email")} required autoComplete="email" />
            </Field>
            <Field label="Telefone" hint="opcional">
              <Input value={form.telefone} onChange={set("telefone")} autoComplete="tel" />
            </Field>
            <Field label="Senha" error={erro}>
              <Input type="password" value={form.senha} onChange={set("senha")} required minLength={6} autoComplete="new-password" />
            </Field>

            <Button type="submit" disabled={carregando} className="w-full">
              {carregando ? "Criando…" : "Criar conta"}
            </Button>
          </form>

          <p className="mt-5 text-xs text-ink-500 text-center">
            Já tem conta?{" "}
            <Link to="/login" className="text-ink-900 underline underline-offset-4 hover:text-amber-accent">
              entrar
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
