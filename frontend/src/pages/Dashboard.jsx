import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { WarningCircle, Wrench, CheckCircle } from "@phosphor-icons/react";

import { StatusBadge, statusProduto } from "../components/StatusBadge";
import { notificacoes, produtos } from "../api/endpoints";
import { useAuth } from "../contexts/AuthContext";

const ICONE_TIPO = {
  validade_proxima:  <WarningCircle size={16} weight="fill" className="text-amber-500 shrink-0 mt-0.5" />,
  validade_expirada: <WarningCircle size={16} weight="fill" className="text-red-500 shrink-0 mt-0.5" />,
  garantia_proxima:  <Wrench       size={16} weight="fill" className="text-blue-500 shrink-0 mt-0.5" />,
  garantia_expirada: <Wrench       size={16} weight="fill" className="text-red-500 shrink-0 mt-0.5" />,
};

function Card({ titulo, valor, hint, tone = "default" }) {
  const tones = {
    default: "bg-white border-cream-200",
    vencendo: "bg-amber-50 border-amber-300",
    vencida: "bg-red-50 border-red-300",
    accent: "bg-blue-50 border-blue-300",
  };
  const valorColors = {
    default: "text-ink-900",
    vencendo: "text-amber-700",
    vencida: "text-red-700",
    accent: "text-blue-700",
  };
  return (
    <div className={`rounded-xl border-2 px-5 py-4 shadow-sm ${tones[tone]}`}>
      <p className="text-sm font-medium text-ink-500">{titulo}</p>
      <p className={`font-display text-4xl font-bold leading-none mt-2 ${valorColors[tone]}`}>{valor}</p>
      {hint && <p className="text-xs text-ink-400 mt-1.5">{hint}</p>}
    </div>
  );
}

export function Dashboard() {
  const { usuario } = useAuth();

  const todosQ = useQuery({ queryKey: ["produtos"], queryFn: () => produtos.list() });
  const vencendoQ = useQuery({ queryKey: ["produtos", "vencendo"], queryFn: () => produtos.vencendo(7) });
  const garantiaQ = useQuery({ queryKey: ["produtos", "garantia"], queryFn: () => produtos.garantiaVencendo(30) });
  const notifQ = useQuery({ queryKey: ["notificacoes"], queryFn: notificacoes.list });

  const total = todosQ.data?.length ?? 0;
  const vencendo = vencendoQ.data?.length ?? 0;
  const garantia = garantiaQ.data?.length ?? 0;
  const naoLidas = notifQ.data?.filter((n) => !n.lida).length ?? 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink-900 tracking-tight">
          Olá, {usuario?.nome?.split(" ")[0]}
        </h1>
        <p className="text-sm text-ink-500 mt-1">Veja o que precisa de atenção hoje.</p>
      </div>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Card titulo="Produtos" valor={total} hint="cadastrados" />
        <Card titulo="Vencendo" valor={vencendo} tone={vencendo > 0 ? "vencendo" : "default"} hint="próximos 7 dias" />
        <Card titulo="Garantia" valor={garantia} tone={garantia > 0 ? "vencendo" : "default"} hint="próximos 30 dias" />
        <Card titulo="Notificações" valor={naoLidas} tone={naoLidas > 0 ? "accent" : "default"} hint="não lidas" />
      </section>

      <div className="grid md:grid-cols-2 gap-5">
        <ListaAlertas
          titulo="Vencendo em breve"
          items={[...(vencendoQ.data || []), ...(garantiaQ.data || [])]}
          loading={vencendoQ.isLoading || garantiaQ.isLoading}
          vazio="Nada vencendo nos próximos dias."
        />
        <Notificacoes data={notifQ.data} loading={notifQ.isLoading} refetch={notifQ.refetch} />
      </div>
    </div>
  );
}

function ListaAlertas({ titulo, items, loading, vazio }) {
  return (
    <section>
      <h2 className="font-display text-lg font-semibold text-ink-900 mb-3">{titulo}</h2>
      {loading ? (
        <p className="text-sm text-ink-400">Carregando…</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-ink-500">{vazio}</p>
      ) : (
        <ul className="space-y-2">
          {items.map((p) => (
            <li key={`${p.tipo}-${p.id}`} className="bg-white border border-cream-200 rounded-lg px-4 py-3 flex items-center justify-between shadow-sm">
              <div className="min-w-0">
                <Link to="/produtos" className="text-sm font-medium text-ink-900 hover:text-amber-accent truncate block">{p.nome}</Link>
                <p className="text-xs text-ink-400 mt-0.5">
                  {p.tipo === "validade"
                    ? `Vence em ${p.dias_para_vencer} dia(s)`
                    : `Garantia: ${p.garantia?.dias_restantes} dia(s)`}
                </p>
              </div>
              <StatusBadge status={statusProduto(p)} />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

const LIMITE = 6;

// Ordena: não lidas primeiro (por data desc), lidas depois (por data desc)
function ordenar(lista) {
  const naoLidas = lista.filter((n) => !n.lida).sort((a, b) => b.data_envio > a.data_envio ? 1 : -1);
  const lidas    = lista.filter((n) =>  n.lida).sort((a, b) => b.data_envio > a.data_envio ? 1 : -1);
  return [...naoLidas, ...lidas];
}

function Notificacoes({ data, loading }) {
  const qc = useQueryClient();
  // IDs em animação de saída (deslizando para virar lida)
  const [saindo, setSaindo] = useState(new Set());

  const marcarLida = useMutation({
    mutationFn: (id) => notificacoes.marcarLida(id),
    onSuccess: (_res, id) => {
      // Após a animação: atualiza o cache localmente (move para lidas) sem refetch
      setTimeout(() => {
        setSaindo((prev) => { const s = new Set(prev); s.delete(id); return s; });
        qc.setQueryData(["notificacoes"], (old) =>
          old ? old.map((n) => (n.id === id ? { ...n, lida: true } : n)) : old
        );
      }, 320);
    },
  });

  const marcarTodas = useMutation({
    mutationFn: notificacoes.marcarTodasLidas,
    onSuccess: () => {
      const ids = (data ?? []).filter((n) => !n.lida).map((n) => n.id);
      setSaindo(new Set(ids));
      setTimeout(() => {
        setSaindo(new Set());
        qc.setQueryData(["notificacoes"], (old) =>
          old ? old.map((n) => ({ ...n, lida: true })) : old
        );
      }, 320);
    },
  });

  function handleMarcarLida(id) {
    setSaindo((prev) => new Set(prev).add(id));
    marcarLida.mutate(id);
  }

  const ordenados = ordenar(data ?? []);
  const naoLidas  = ordenados.filter((n) => !n.lida);
  const visiveis  = ordenados.slice(0, LIMITE);
  const ocultas   = Math.max(0, ordenados.length - LIMITE);

  return (
    <section>
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-display text-lg font-semibold text-ink-900">Notificações</h2>
        {naoLidas.length > 0 && (
          <button
            onClick={() => marcarTodas.mutate()}
            disabled={marcarTodas.isPending}
            className="text-xs text-ink-400 hover:text-ink-700 transition-colors"
          >
            Marcar todas como lidas
          </button>
        )}
      </div>

      {loading ? (
        <p className="text-sm text-ink-400">Carregando…</p>
      ) : ordenados.length === 0 ? (
        <p className="text-sm text-ink-500">Sem notificações ainda.</p>
      ) : (
        <>
          <ul className="space-y-2">
            {visiveis.map((n) => {
              const sumindo = saindo.has(n.id);
              return (
                <li
                  key={n.id}
                  style={{
                    transition: "opacity 280ms ease, transform 280ms ease, max-height 320ms ease, padding 320ms ease",
                    maxHeight: sumindo ? "0px" : "120px",
                    opacity: sumindo ? 0 : 1,
                    transform: sumindo ? "translateX(16px)" : "translateX(0)",
                    overflow: "hidden",
                    paddingTop: sumindo ? "0px" : undefined,
                    paddingBottom: sumindo ? "0px" : undefined,
                  }}
                  className={`rounded-lg px-4 py-3 border flex items-start justify-between gap-3 ${
                    n.lida ? "bg-white border-cream-200 opacity-60" : "bg-blue-50 border-blue-200"
                  }`}
                >
                  {ICONE_TIPO[n.tipo] ?? <CheckCircle size={16} weight="fill" className="text-ink-300 shrink-0 mt-0.5" />}
                  <div className="min-w-0 flex-1">
                    <p className={`text-sm leading-snug ${n.lida ? "text-ink-500" : "text-ink-900"}`}>
                      {n.mensagem}
                    </p>
                    <p className="text-xs text-ink-400 mt-1">
                      {new Date(n.data_envio).toLocaleString("pt-BR")}
                    </p>
                  </div>
                  {!n.lida && (
                    <button
                      onClick={() => handleMarcarLida(n.id)}
                      disabled={sumindo}
                      className="shrink-0 text-xs text-blue-600 hover:text-blue-800 font-medium transition-colors whitespace-nowrap"
                    >
                      Marcar lida
                    </button>
                  )}
                </li>
              );
            })}
          </ul>

          {ocultas > 0 && (
            <p className="text-xs text-ink-400 mt-3 text-center">
              + {ocultas} notificaç{ocultas === 1 ? "ão" : "ões"} mais
            </p>
          )}
        </>
      )}
    </section>
  );
}
