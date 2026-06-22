import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { Button } from "../components/Button";
import { Field, Input, Select } from "../components/Field";
import { Modal } from "../components/Modal";
import { StatusBadge, statusProduto } from "../components/StatusBadge";
import { useConfirm } from "../contexts/ConfirmContext";
import { Plus, PencilSimple, Trash, Tag } from "@phosphor-icons/react";
import { produtos as api, categorias as apiCategorias } from "../api/endpoints";

const TABS = [
  { id: "todos", label: "Todos" },
  { id: "validade", label: "Com Validade" },
  { id: "garantia", label: "Com Garantia" },
];

const SEM_CATEGORIA = "sem";

export function Produtos() {
  const [tab, setTab] = useState("todos");
  const [busca, setBusca] = useState("");
  const [categoria, setCategoria] = useState(""); // "" = todas · "sem" = sem categoria · "<id>"
  const [modal, setModal] = useState(null);
  const qc = useQueryClient();
  const confirmar = useConfirm();

  const lista = useQuery({
    queryKey: ["produtos", busca || null],
    queryFn: () => api.list(busca || undefined),
  });

  const categoriasQ = useQuery({
    queryKey: ["categorias"],
    queryFn: () => apiCategorias.list(),
  });

  const filtrados = useMemo(() => {
    if (!lista.data) return [];
    return lista.data.filter((p) => {
      const okTab = tab === "todos" || p.tipo === tab;
      const okCategoria =
        categoria === ""
          ? true
          : categoria === SEM_CATEGORIA
            ? p.categoria_id == null
            : String(p.categoria_id) === categoria;
      return okTab && okCategoria;
    });
  }, [lista.data, tab, categoria]);

  const filtroAtivo = tab !== "todos" || categoria !== "" || busca.trim() !== "";

  const nomeCategoria =
    categoria === SEM_CATEGORIA
      ? "Sem categoria"
      : categoriasQ.data?.find((c) => String(c.id) === categoria)?.nome ?? "";

  function limparFiltros() {
    setTab("todos");
    setCategoria("");
    setBusca("");
  }

  // Abre o modal de criação já com o filtro ativo pré-preenchido (categoria + tipo).
  function adicionarComFiltro() {
    setModal({
      modo: "criar",
      preset: {
        categoria_id: /^\d+$/.test(categoria) ? Number(categoria) : null,
        tipo: tab === "validade" || tab === "garantia" ? tab : null,
      },
    });
  }

  const excluir = useMutation({
    mutationFn: (id) => api.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["produtos"] }),
  });

  async function onDelete(p) {
    const ok = await confirmar({
      titulo: "Excluir produto",
      texto: `"${p.nome}" será removido permanentemente.`,
      confirmar: "Excluir",
      perigo: true,
    });
    if (ok) excluir.mutate(p.id);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink-900 tracking-tight">
            Produtos
          </h1>
          <p className="text-sm text-ink-500 mt-1">Tudo o que você cadastrou.</p>
        </div>
        <Button onClick={() => setModal({ modo: "criar" })}><Plus size={15} weight="bold" /> Adicionar</Button>
      </div>

      <div className="flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex gap-1 bg-cream-50 border border-cream-200 rounded-lg p-1 w-fit">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`px-3 py-1.5 rounded-md text-sm transition-colors ${tab === t.id ? "bg-ink-900 text-cream-50" : "text-ink-500 hover:text-ink-900"
                }`}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div className="flex flex-col sm:flex-row gap-2 sm:items-center">
          <Select
            value={categoria}
            onChange={(e) => setCategoria(e.target.value)}
            className="sm:w-48"
            aria-label="Filtrar por categoria"
          >
            <option value="">Todas as categorias</option>
            {categoriasQ.data?.map((c) => (
              <option key={c.id} value={c.id}>{c.nome}</option>
            ))}
            <option value={SEM_CATEGORIA}>Sem categoria</option>
          </Select>
          <Input
            placeholder="Buscar por nome…"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            className="sm:max-w-xs"
          />
        </div>
      </div>

      {lista.isLoading ? (
        <p className="text-sm text-ink-400">Carregando…</p>
      ) : filtrados.length === 0 ? (
        filtroAtivo ? (
          <div className="bg-cream-50 border border-dashed border-cream-200 rounded-xl py-10 px-4 text-center">
            <p className="text-sm text-ink-500">
              {nomeCategoria
                ? <>Nenhum produto na categoria <span className="font-medium text-ink-700">{nomeCategoria}</span>.</>
                : "Nenhum produto encontrado com os filtros atuais."}
            </p>
            <div className="mt-3 flex flex-wrap items-center justify-center gap-2">
              <Button onClick={adicionarComFiltro}>
                <Plus size={15} weight="bold" /> Adicionar produto
              </Button>
              <Button variant="ghost" onClick={limparFiltros}>Limpar filtros</Button>
            </div>
          </div>
        ) : (
          <div className="bg-cream-50 border border-dashed border-cream-200 rounded-xl py-10 text-center">
            <p className="text-sm text-ink-500">Nada por aqui ainda.</p>
            <Button variant="ghost" className="mt-3" onClick={() => setModal({ modo: "criar" })}>
              Cadastrar primeiro produto
            </Button>
          </div>
        )
      ) : (
        <ul className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {filtrados.map((p) => (
            <ProdutoItem
              key={p.id}
              produto={p}
              onEditar={() => setModal({ modo: "editar", produto: p })}
              onExcluir={() => onDelete(p)}
            />
          ))}
        </ul>
      )}

      {modal && (
        <ProdutoModal
          modal={modal}
          onFechar={() => setModal(null)}
          onSalvo={() => {
            qc.invalidateQueries({ queryKey: ["produtos"] });
            setModal(null);
          }}
        />
      )}
    </div>
  );
}

function ProdutoItem({ produto, onEditar, onExcluir }) {
  const tipoLabel = produto.tipo === "validade" ? "Com Validade" : "Com Garantia";
  const tipoColor = produto.tipo === "validade"
    ? "text-emerald-600 bg-emerald-50 border-emerald-200"
    : "text-blue-600 bg-blue-50 border-blue-200";

  return (
    <li className="bg-white border border-cream-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <span className={`inline-block text-[10px] font-semibold px-2 py-0.5 rounded-full border mb-1.5 ${tipoColor}`}>
            {tipoLabel}
          </span>
          <h3 className="font-display text-base font-semibold text-ink-900 leading-tight truncate">{produto.nome}</h3>
          {produto.descricao && (
            <p className="text-xs text-ink-500 mt-0.5 line-clamp-1">{produto.descricao}</p>
          )}
          {produto.categoria && (
            <span className="inline-flex items-center gap-1 mt-1 text-[10px] text-amber-700 bg-amber-50 border border-amber-200 rounded-full px-2 py-0.5">
              <Tag size={10} weight="fill" /> {produto.categoria}
            </span>
          )}
        </div>
        <StatusBadge status={statusProduto(produto)} />
      </div>

      <dl className="mt-3 space-y-1 text-xs bg-cream-50 rounded-lg p-2.5">
        {produto.tipo === "validade" ? (
          <>
            <Linha label="Validade" valor={fmtData(produto.data_validade)} />
            <Linha label="Dias restantes" valor={produto.dias_para_vencer != null ? `${produto.dias_para_vencer} dia(s)` : "—"} />
          </>
        ) : (
          <>
            <Linha label="Comprado em" valor={fmtData(produto.data_compra)} />
            <Linha label="Garantia até" valor={fmtData(produto.garantia?.data_fim)} />
            <Linha label="Dias restantes" valor={produto.garantia?.dias_restantes != null ? `${produto.garantia.dias_restantes} dia(s)` : "—"} />
          </>
        )}
      </dl>

      <div className="mt-3 flex gap-2">
        <Button variant="ghost" onClick={onEditar} className="flex-1 !py-1.5 !text-xs"><PencilSimple size={13} /> Editar</Button>
        <Button variant="danger" onClick={onExcluir} className="!py-1.5 !text-xs"><Trash size={13} /> Excluir</Button>
      </div>
    </li>
  );
}

function Linha({ label, valor }) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <dt className="text-ink-400">{label}</dt>
      <dd className="text-ink-700 font-medium">{valor}</dd>
    </div>
  );
}

function fmtData(iso) {
  if (!iso) return "—";
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("pt-BR");
}

function ProdutoModal({ modal, onFechar, onSalvo }) {
  const editando = modal.modo === "editar";
  const p = modal.produto;
  const preset = modal.preset || {};
  const [form, setForm] = useState(
    editando
      ? {
        tipo: p.tipo,
        nome: p.nome,
        descricao: p.descricao || "",
        categoria_id: p.categoria_id || "",
        data_validade: p.data_validade || "",
        data_compra: p.data_compra || "",
        numero_serie: p.numero_serie || "",
        garantia_meses: p.garantia?.meses || 12,
      }
      : {
        tipo: preset.tipo || "validade",
        nome: "",
        descricao: "",
        categoria_id: preset.categoria_id || "",
        data_validade: "",
        data_compra: "",
        numero_serie: "",
        garantia_meses: 12,
      }
  );
  const [erro, setErro] = useState(null);

  const categoriasQ = useQuery({
    queryKey: ["categorias"],
    queryFn: () => apiCategorias.list(),
  });

  const mutation = useMutation({
    mutationFn: (body) =>
      editando ? api.update(p.id, body) : api.create(body),
    onSuccess: onSalvo,
    onError: (err) => setErro(extrairErro(err)),
  });

  function set(k) { return (e) => setForm({ ...form, [k]: e.target.value }); }

  function onSubmit(e) {
    e.preventDefault();
    setErro(null);
    const body = {
      nome: form.nome,
      descricao: form.descricao || null,
      categoria_id: form.categoria_id ? Number(form.categoria_id) : null,
    };
    if (form.tipo === "validade") {
      body.data_validade = form.data_validade;
      if (!editando) body.tipo = "validade";
    } else {
      body.data_compra = form.data_compra;
      body.numero_serie = form.numero_serie || null;
      if (!editando) {
        body.tipo = "garantia";
        body.garantia_meses = Number(form.garantia_meses);
      }
    }
    mutation.mutate(body);
  }

  return (
    <Modal
      open
      onClose={onFechar}
      title={editando ? "Editar produto" : "Adicionar produto"}
      footer={
        <>
          <Button variant="ghost" onClick={onFechar}>Cancelar</Button>
          <Button onClick={onSubmit} disabled={mutation.isPending}>
            {mutation.isPending ? "Salvando…" : "Salvar"}
          </Button>
        </>
      }
    >
      <form onSubmit={onSubmit} className="space-y-4">
        {!editando && (
          <Field label="Tipo">
            <Select value={form.tipo} onChange={set("tipo")}>
              <option value="validade">Com Validade</option>
              <option value="garantia">Com Garantia</option>
            </Select>
          </Field>
        )}

        <Field label="Nome">
          <Input value={form.nome} onChange={set("nome")} required />
        </Field>
        <Field label="Descrição" hint="opcional">
          <Input value={form.descricao} onChange={set("descricao")} />
        </Field>

        <Field label="Categoria" hint="opcional">
          <Select value={form.categoria_id} onChange={set("categoria_id")}>
            <option value="">Sem categoria</option>
            {categoriasQ.data?.map((c) => (
              <option key={c.id} value={c.id}>{c.nome}</option>
            ))}
          </Select>
        </Field>

        {form.tipo === "validade" ? (
          <Field label="Data de validade">
            <Input type="date" value={form.data_validade} onChange={set("data_validade")} required />
          </Field>
        ) : (
          <>
            <Field label="Data de compra">
              <Input type="date" value={form.data_compra} onChange={set("data_compra")} required />
            </Field>
            <Field label="Número de série" hint="opcional">
              <Input value={form.numero_serie} onChange={set("numero_serie")} />
            </Field>
            {!editando && (
              <Field label="Garantia (meses)">
                <Input
                  type="number"
                  value={form.garantia_meses}
                  onChange={set("garantia_meses")}
                  min={1}
                  max={120}
                  required
                />
              </Field>
            )}
          </>
        )}

        {erro && <p className="text-xs text-status-vencida">{erro}</p>}
      </form>
    </Modal>
  );
}

function extrairErro(err) {
  const body = err.response?.data;
  if (body?.erro) return body.erro;
  if (body?.erros?.[0]?.msg) {
    return `${body.erros[0].loc?.join(".")}: ${body.erros[0].msg}`;
  }
  return "Erro ao salvar";
}
