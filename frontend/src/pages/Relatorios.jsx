import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import {
  ChartBar,
  Tag,
  Warning,
  ShieldWarning,
  Trash,
  Plus,
  CaretDown,
  CaretUp,
} from "@phosphor-icons/react";

import { Button } from "../components/Button";
import { Field, Select } from "../components/Field";
import { useConfirm } from "../contexts/ConfirmContext";
import { relatorios as api } from "../api/endpoints";

const TIPOS = [
  {
    id: "resumo_geral",
    label: "Resumo geral",
    Icone: ChartBar,
    cor: "text-blue-700 bg-blue-50 border-blue-200",
  },
  {
    id: "produtos_por_categoria",
    label: "Produtos por categoria",
    Icone: Tag,
    cor: "text-amber-700 bg-amber-50 border-amber-200",
  },
  {
    id: "produtos_vencendo",
    label: "Produtos vencendo",
    Icone: Warning,
    cor: "text-red-700 bg-red-50 border-red-200",
  },
  {
    id: "garantias_vencendo",
    label: "Garantias vencendo",
    Icone: ShieldWarning,
    cor: "text-orange-700 bg-orange-50 border-orange-200",
  },
];

const TIPO_MAP = Object.fromEntries(TIPOS.map((t) => [t.id, t]));

export function Relatorios() {
  const [tipo, setTipo] = useState("resumo_geral");
  const [erro, setErro] = useState(null);
  const qc = useQueryClient();
  const confirmar = useConfirm();

  const lista = useQuery({
    queryKey: ["relatorios"],
    queryFn: () => api.list(),
  });

  const gerar = useMutation({
    mutationFn: (t) => api.gerar(t),
    onSuccess: () => {
      setErro(null);
      qc.invalidateQueries({ queryKey: ["relatorios"] });
    },
    onError: (err) => setErro(err.response?.data?.erro || "Erro ao gerar relatório"),
  });

  const excluir = useMutation({
    mutationFn: (id) => api.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["relatorios"] }),
  });

  async function onDelete(r) {
    const meta = TIPO_MAP[r.tipo];
    const ok = await confirmar({
      titulo: "Excluir relatório",
      texto: `O relatório "${meta?.label || r.tipo}" de ${fmtDataHora(r.data_geracao)} será removido.`,
      confirmar: "Excluir",
      perigo: true,
    });
    if (ok) excluir.mutate(r.id);
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink-900 tracking-tight">
          Relatórios
        </h1>
        <p className="text-sm text-ink-500 mt-1">Snapshots do sistema gerados sob demanda.</p>
      </div>

      {/* Painel de geração */}
      <div className="bg-white border border-cream-200 rounded-xl p-4 shadow-sm">
        <p className="text-sm font-medium text-ink-700 mb-3">Gerar novo relatório</p>
        <div className="flex flex-col sm:flex-row sm:items-end gap-3">
          <div className="flex-1">
            <Field label="Tipo de relatório">
              <Select value={tipo} onChange={(e) => setTipo(e.target.value)}>
                {TIPOS.map((t) => (
                  <option key={t.id} value={t.id}>{t.label}</option>
                ))}
              </Select>
            </Field>
          </div>
          <Button onClick={() => gerar.mutate(tipo)} disabled={gerar.isPending}>
            <Plus size={15} weight="bold" />
            {gerar.isPending ? "Gerando…" : "Gerar"}
          </Button>
        </div>
        {erro && <p className="text-xs text-status-vencida mt-2">{erro}</p>}
      </div>

      {/* Lista de relatórios */}
      {lista.isLoading ? (
        <p className="text-sm text-ink-400">Carregando…</p>
      ) : lista.data?.length === 0 ? (
        <div className="bg-cream-50 border border-dashed border-cream-200 rounded-xl py-12 text-center">
          <ChartBar size={32} className="mx-auto text-ink-300 mb-2" weight="duotone" />
          <p className="text-sm text-ink-500">Nenhum relatório gerado ainda.</p>
        </div>
      ) : (
        <ul className="space-y-3">
          {lista.data.map((r) => (
            <RelatorioItem key={r.id} relatorio={r} onExcluir={() => onDelete(r)} />
          ))}
        </ul>
      )}
    </div>
  );
}

function RelatorioItem({ relatorio, onExcluir }) {
  const [aberto, setAberto] = useState(false);
  const meta = TIPO_MAP[relatorio.tipo];
  const { Icone, cor, label } = meta || { Icone: ChartBar, cor: "text-ink-600 bg-ink-50 border-ink-200", label: relatorio.tipo };

  return (
    <li className="bg-white border border-cream-200 rounded-xl shadow-sm overflow-hidden">
      {/* Cabeçalho do card */}
      <div className="px-4 py-3 flex items-center gap-3">
        <div className={`w-9 h-9 rounded-lg border flex items-center justify-center shrink-0 ${cor}`}>
          <Icone size={18} weight="duotone" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-ink-900">{label}</p>
          <p className="text-xs text-ink-400">{fmtDataHora(relatorio.data_geracao)}</p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={onExcluir}
            className="p-1.5 rounded-lg text-ink-400 hover:text-status-vencida hover:bg-red-50 transition-colors"
            title="Excluir relatório"
          >
            <Trash size={16} />
          </button>
          <button
            onClick={() => setAberto((v) => !v)}
            className="p-1.5 rounded-lg text-ink-400 hover:text-ink-700 hover:bg-cream-100 transition-colors"
            title={aberto ? "Ocultar" : "Ver dados"}
          >
            {aberto ? <CaretUp size={16} /> : <CaretDown size={16} />}
          </button>
        </div>
      </div>

      {/* Conteúdo expandido */}
      {aberto && (
        <div className="border-t border-cream-200 px-4 py-4 bg-cream-50">
          <ConteudoRelatorio tipo={relatorio.tipo} dados={relatorio.conteudo} />
        </div>
      )}
    </li>
  );
}

function ConteudoRelatorio({ tipo, dados }) {
  if (!dados) return null;

  if (tipo === "resumo_geral") {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <Stat label="Usuários" valor={dados.usuarios} />
        <Stat label="Produtos" valor={dados.produtos} />
        <Stat label="Com validade" valor={dados.validade} />
        <Stat label="Com garantia" valor={dados.garantia} />
        <Stat label="Garantias" valor={dados.garantias} />
        <Stat label="Categorias" valor={dados.categorias} />
      </div>
    );
  }

  if (tipo === "produtos_por_categoria") {
    return (
      <div className="space-y-3">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <Stat label="Total de produtos" valor={dados.total_produtos} />
          <Stat label="Sem categoria" valor={dados.sem_categoria} />
        </div>
        {dados.por_categoria?.length > 0 && (
          <div>
            <p className="text-xs font-medium text-ink-500 mb-2">Por categoria</p>
            <div className="rounded-lg overflow-hidden border border-cream-200">
              <table className="w-full text-sm">
                <thead className="bg-cream-100">
                  <tr>
                    <th className="text-left px-3 py-2 text-xs font-medium text-ink-500">Categoria</th>
                    <th className="text-right px-3 py-2 text-xs font-medium text-ink-500">Total</th>
                    <th className="text-right px-3 py-2 text-xs font-medium text-ink-500">Validade</th>
                    <th className="text-right px-3 py-2 text-xs font-medium text-ink-500">Garantia</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-cream-200">
                  {dados.por_categoria.map((c, i) => (
                    <tr key={i} className="bg-white">
                      <td className="px-3 py-2 font-medium text-ink-900">{c.categoria}</td>
                      <td className="px-3 py-2 text-right text-ink-700">{c.quantidade}</td>
                      <td className="px-3 py-2 text-right text-emerald-700">{c.validade ?? "—"}</td>
                      <td className="px-3 py-2 text-right text-blue-700">{c.garantia ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    );
  }

  if (tipo === "produtos_vencendo") {
    return (
      <div className="space-y-3">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <Stat label="Total com validade" valor={dados.total_validade} />
          <Stat label="Em risco (7 dias)" valor={dados.em_risco_7_dias} destaque="vencendo" />
          <Stat label="Já vencidos" valor={dados.vencidos} destaque="vencida" />
        </div>
        <ListaRisco itens={dados.itens_em_risco} colunaExtra="dias" labelExtra="Dias restantes" />
      </div>
    );
  }

  if (tipo === "garantias_vencendo") {
    return (
      <div className="space-y-3">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <Stat label="Total com garantia" valor={dados.total_garantia} />
          <Stat label="Em risco (30 dias)" valor={dados.garantias_em_risco_30_dias} destaque="vencendo" />
        </div>
        <ListaRisco itens={dados.itens_em_risco} colunaExtra="dias_restantes" labelExtra="Dias restantes" />
      </div>
    );
  }

  // fallback genérico
  return (
    <pre className="text-xs text-ink-600 bg-cream-100 rounded-lg p-3 overflow-x-auto">
      {JSON.stringify(dados, null, 2)}
    </pre>
  );
}

function Stat({ label, valor, destaque }) {
  const cores = {
    vencendo: "text-amber-700",
    vencida: "text-red-700",
  };
  return (
    <div className="bg-white border border-cream-200 rounded-lg px-3 py-2.5">
      <p className="text-xs text-ink-400">{label}</p>
      <p className={`font-display text-2xl font-bold leading-none mt-1 ${cores[destaque] || "text-ink-900"}`}>
        {valor ?? "—"}
      </p>
    </div>
  );
}

function ListaRisco({ itens, colunaExtra, labelExtra }) {
  if (!itens?.length) {
    return <p className="text-xs text-ink-400">Nenhum item em risco.</p>;
  }
  return (
    <div>
      <p className="text-xs font-medium text-ink-500 mb-2">Itens em risco</p>
      <div className="rounded-lg overflow-hidden border border-cream-200">
        <table className="w-full text-sm">
          <thead className="bg-cream-100">
            <tr>
              <th className="text-left px-3 py-2 text-xs font-medium text-ink-500">Produto</th>
              <th className="text-right px-3 py-2 text-xs font-medium text-ink-500">{labelExtra}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-cream-200">
            {itens.map((item, i) => (
              <tr key={i} className="bg-white">
                <td className="px-3 py-2 font-medium text-ink-900">{item.nome}</td>
                <td className="px-3 py-2 text-right text-amber-700 font-medium">
                  {item[colunaExtra] != null ? `${item[colunaExtra]} dia(s)` : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function fmtDataHora(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("pt-BR");
}
