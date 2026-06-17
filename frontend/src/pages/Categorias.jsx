import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "../components/Button";
import { Field, Input, Textarea } from "../components/Field";
import { Modal } from "../components/Modal";
import { useAuth } from "../contexts/AuthContext";
import { useConfirm } from "../contexts/ConfirmContext";
import { Plus, PencilSimple, Trash } from "@phosphor-icons/react";
import { categorias as api } from "../api/endpoints";

export function Categorias() {
  const { isAdmin } = useAuth();
  const [modal, setModal] = useState(null);
  const qc = useQueryClient();
  const confirmar = useConfirm();

  const lista = useQuery({
    queryKey: ["categorias"],
    queryFn: () => api.list(),
  });

  const excluir = useMutation({
    mutationFn: (id) => api.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["categorias"] }),
  });

  async function onDelete(c) {
    const ok = await confirmar({
      titulo: "Excluir categoria",
      texto: `A categoria "${c.nome}" será removida.`,
      confirmar: "Excluir",
      perigo: true,
    });
    if (ok) excluir.mutate(c.id);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink-900 tracking-tight">
            Categorias
          </h1>
          <p className="text-sm text-ink-500 mt-1">Como os produtos são organizados.</p>
        </div>
        {isAdmin && <Button onClick={() => setModal({ modo: "criar" })}><Plus size={15} weight="bold" /> Adicionar</Button>}
      </div>

      {lista.isLoading ? (
        <p className="text-sm text-ink-400">Carregando…</p>
      ) : lista.data?.length === 0 ? (
        <div className="bg-cream-50 border border-dashed border-cream-200 rounded-xl py-10 text-center">
          <p className="text-sm text-ink-500">Nenhuma categoria ainda.</p>
          {isAdmin && (
            <Button variant="ghost" className="mt-3" onClick={() => setModal({ modo: "criar" })}>
              Criar primeira categoria
            </Button>
          )}
        </div>
      ) : (
        <ul className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {lista.data.map((c) => (
            <li key={c.id} className="bg-white border-2 border-cream-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="font-display text-base font-semibold text-ink-900 leading-tight">{c.nome}</h3>
                  <p className="text-xs text-ink-500 mt-1 min-h-[1rem]">
                    {c.descricao || "Sem descrição"}
                  </p>
                </div>
                <span className="text-xs font-semibold text-amber-700 bg-amber-50 border border-amber-200 rounded-full px-2 py-0.5">
                  #{c.id}
                </span>
              </div>
              {isAdmin && (
                <div className="mt-3 flex gap-2">
                  <Button
                    variant="ghost"
                    onClick={() => setModal({ modo: "editar", categoria: c })}
                    className="flex-1 !py-1.5 !text-xs"
                  >
                    <PencilSimple size={13} /> Editar
                  </Button>
                  <Button variant="danger" onClick={() => onDelete(c)} className="!py-1.5 !text-xs">
                    <Trash size={13} /> Excluir
                  </Button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}

      {modal && (
        <CategoriaModal
          modal={modal}
          onFechar={() => setModal(null)}
          onSalvo={() => {
            qc.invalidateQueries({ queryKey: ["categorias"] });
            setModal(null);
          }}
        />
      )}
    </div>
  );
}

function CategoriaModal({ modal, onFechar, onSalvo }) {
  const editando = modal.modo === "editar";
  const c = modal.categoria;
  const [form, setForm] = useState({
    nome: editando ? c.nome : "",
    descricao: editando ? c.descricao || "" : "",
  });
  const [erro, setErro] = useState(null);

  const mutation = useMutation({
    mutationFn: (body) => (editando ? api.update(c.id, body) : api.create(body)),
    onSuccess: onSalvo,
    onError: (err) => setErro(extrairErro(err)),
  });

  function set(k) {
    return (e) => setForm({ ...form, [k]: e.target.value });
  }

  function onSubmit(e) {
    e.preventDefault();
    setErro(null);
    mutation.mutate({ nome: form.nome, descricao: form.descricao || null });
  }

  return (
    <Modal
      open
      onClose={onFechar}
      title={editando ? "Editar categoria" : "Adicionar categoria"}
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
        <Field label="Nome">
          <Input value={form.nome} onChange={set("nome")} required maxLength={80} />
        </Field>
        <Field label="Descrição" hint="opcional">
          <Textarea value={form.descricao} onChange={set("descricao")} maxLength={255} rows={3} />
        </Field>
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
