import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import {
  UserCircle,
  SignOut,
  BookOpen,
} from "@phosphor-icons/react";

import { useAuth } from "../contexts/AuthContext";
import { useConfirm } from "../contexts/ConfirmContext";
import { Tutorial } from "./Tutorial";

function navClass({ isActive }) {
  const base = "text-sm transition-colors";
  return isActive
    ? `${base} text-ink-900 font-medium`
    : `${base} text-ink-500 hover:text-ink-900`;
}

export function Layout() {
  const { usuario, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const confirmar = useConfirm();
  const qc = useQueryClient();
  const [tutorialAberto, setTutorialAberto] = useState(false);

  async function onLogout() {
    const ok = await confirmar({
      titulo: "Sair da conta",
      texto: "Você precisará entrar novamente para acessar.",
      confirmar: "Sair",
    });
    if (ok) {
      logout();
      qc.clear(); // limpa cache para não vazar dados entre contas
      navigate("/login", { replace: true });
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-cream-200 bg-cream-50">
        <div className="max-w-6xl mx-auto px-5 sm:px-6 py-3 flex items-center justify-between gap-4">

          {/* Esquerda: avatar do usuário + logo */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="relative group">
              <button className="flex items-center justify-center w-9 h-9 rounded-full bg-ink-100 text-ink-600 hover:bg-ink-200 transition-colors">
                <UserCircle size={22} weight="fill" />
              </button>
              <div className="absolute left-0 top-full mt-2 w-48 bg-white border border-cream-200 rounded-xl shadow-lg p-3 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-150 z-50 pointer-events-none">
                <p className="text-sm font-semibold text-ink-900 truncate">{usuario?.nome}</p>
                <span className={`inline-block mt-1.5 text-xs font-medium px-2 py-0.5 rounded-full ${
                  isAdmin
                    ? "bg-amber-50 text-amber-700 border border-amber-200"
                    : "bg-blue-50 text-blue-700 border border-blue-200"
                }`}>
                  {isAdmin ? "Administrador" : "Cliente"}
                </span>
              </div>
            </div>

            <NavLink to="/" className="font-display text-lg font-semibold text-ink-900 tracking-tight leading-none">
              Keepr
            </NavLink>
          </div>

          {/* Centro: navegação */}
          <nav className="flex items-center gap-4 overflow-x-auto">
            <NavLink to="/" end className={navClass}>Dashboard</NavLink>
            <NavLink to="/produtos" className={navClass}>Produtos</NavLink>
            <NavLink to="/comprovantes" className={navClass}>Comprovantes</NavLink>
            {isAdmin && <NavLink to="/categorias" className={navClass}>Categorias</NavLink>}
            {isAdmin && <NavLink to="/relatorios" className={navClass}>Relatórios</NavLink>}
            {isAdmin && <NavLink to="/usuarios" className={navClass}>Usuários</NavLink>}
          </nav>

          {/* Direita: tutorial + sair */}
          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={() => setTutorialAberto(true)}
              className="hidden sm:flex items-center gap-1.5 text-sm text-ink-500 hover:text-amber-accent transition-colors"
              title="Reabrir tutorial"
            >
              <BookOpen size={16} />
              Tutorial
            </button>
            <button
              onClick={onLogout}
              className="flex items-center gap-1.5 text-sm text-ink-500 hover:text-status-vencida transition-colors"
            >
              <SignOut size={16} />
              Sair
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-6xl w-full mx-auto px-5 sm:px-6 py-6">
        <Outlet />
      </main>

      <footer className="border-t border-cream-200 px-6 py-3 text-xs text-ink-400 flex justify-between max-w-6xl mx-auto w-full">
        <span>Keepr · v0.2</span>
        <span>Nada vence esquecido.</span>
      </footer>

      <Tutorial
        aberto={tutorialAberto || undefined}
        onFechar={() => setTutorialAberto(false)}
      />
    </div>
  );
}
