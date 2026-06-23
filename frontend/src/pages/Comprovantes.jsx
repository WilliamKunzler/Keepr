import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";
import { UploadSimple, Plus, Trash } from "@phosphor-icons/react";

import { Button } from "../components/Button";
import { Field, Input, Select } from "../components/Field";
import { Modal } from "../components/Modal";
import { useConfirm } from "../contexts/ConfirmContext";
import { comprovantes as api } from "../api/endpoints";
import { assetUrl } from "../api/client";

export function Comprovantes() {
  const qc = useQueryClient();
  const lista = useQuery({ queryKey: ["comprovantes"], queryFn: api.list });
  const [aberto, setAberto] = useState(null);
  const inputRef = useRef(null);
  const confirmar = useConfirm();

  const upload = useMutation({
    mutationFn: (file) => api.upload(file),
    onSuccess: (comp) => {
      qc.invalidateQueries({ queryKey: ["comprovantes"] });
      setAberto(comp);
    },
  });

  const remover = useMutation({
    mutationFn: (id) => api.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["comprovantes"] }),
  });

  function onFile(e) {
    const file = e.target.files?.[0];
    if (file) upload.mutate(file);
    e.target.value = "";
  }

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink-900 tracking-tight">
            Comprovantes
          </h1>
          <p className="text-sm text-ink-500 mt-1">Envie uma nota e o sistema lê os produtos.</p>
        </div>
        <Button
          onClick={() => inputRef.current?.click()}
          disabled={upload.isPending}
          variant="amber"
        >
          <UploadSimple size={15} weight="bold" className="shrink-0" />
          {upload.isPending ? "Lendo…" : "Enviar nota"}
        </Button>
        <input
          ref={inputRef}
          type="file"
          accept="image/png,image/jpeg,image/jpg"
          onChange={onFile}
          className="hidden"
        />
      </div>

      {upload.error && (
        <div className="bg-status-vencida/5 border border-status-vencida/30 text-xs text-status-vencida rounded-lg px-3 py-2">
          {upload.error.response?.data?.erro || "Erro no upload"}
        </div>
      )}

      {lista.isLoading ? (
        <p className="text-sm text-ink-400">Carregando…</p>
      ) : lista.data?.length === 0 ? (
        <div className="bg-cream-50 border border-dashed border-cream-200 rounded-xl py-10 text-center">
          <p className="font-display text-lg font-semibold text-ink-900 mb-1">Sem comprovantes ainda</p>
          <p className="text-sm text-ink-500 mb-4">
            Envie a foto de uma nota fiscal e o sistema identifica os produtos.
          </p>
          <Button onClick={() => inputRef.current?.click()} variant="amber">
            <UploadSimple size={15} weight="bold" className="shrink-0" /> Enviar primeira nota
          </Button>
        </div>
      ) : (
        <ul className="grid sm:grid-cols-2 lg:grid-cols-4 gap-2">
          {lista.data.map((c) => (
            <ComprovanteCard
              key={c.id}
              c={c}
              onAbrir={() => setAberto(c)}
              onExcluir={async () => {
                const ok = await confirmar({
                  titulo: "Excluir comprovante",
                  texto: "O comprovante e sua imagem serão removidos.",
                  confirmar: "Excluir",
                  perigo: true,
                });
                if (ok) remover.mutate(c.id);
              }}
            />
          ))}
        </ul>
      )}

      {aberto && (
        <ComprovanteModal
          comprovante={aberto}
          onFechar={() => setAberto(null)}
          onConfirmado={() => {
            qc.invalidateQueries({ queryKey: ["comprovantes"] });
            qc.invalidateQueries({ queryKey: ["produtos"] });
            setAberto(null);
          }}
        />
      )}
    </div>
  );
}

function ComprovanteCard({ c, onAbrir, onExcluir }) {
  const data = new Date(c.data_upload).toLocaleDateString("pt-BR");
  return (
    <li className="bg-cream-50 border border-cream-200 rounded-xl overflow-hidden">
      <button onClick={onAbrir} className="block w-full">
        <div className="aspect-[4/3] bg-cream-200 overflow-hidden">
          <img src={assetUrl(c.url)} alt="comprovante" className="w-full h-full object-cover" />
        </div>
        <div className="px-2.5 py-2 text-left">
          <div className="flex items-center justify-between">
            <p className="text-xs text-ink-400">{data}</p>
            {c.confirmado ? (
              <span className="text-xs text-status-ativa">Confirmado</span>
            ) : (
              <span className="text-xs text-amber-accent">Pendente</span>
            )}
          </div>
          <p className="text-xs text-ink-700 mt-0.5">
            {c.valor_total ? `R$ ${c.valor_total.toFixed(2)}` : "—"}
            {" · "}
            {c.itens_identificados.length} item(ns)
          </p>
        </div>
      </button>
      <div className="px-2.5 pb-2">
        <button
          onClick={onExcluir}
          className="text-xs text-ink-400 hover:text-status-vencida"
        >
          Excluir
        </button>
      </div>
    </li>
  );
}

function ComprovanteModal({ comprovante, onFechar, onConfirmado }) {
  return (
    <Modal
      open
      onClose={onFechar}
      title={comprovante.confirmado ? "Comprovante" : "Confirmar produtos"}
    >
      <div className="space-y-5">
        <a href={assetUrl(comprovante.url)} target="_blank" rel="noreferrer" className="block">
          <img src={assetUrl(comprovante.url)} alt="comprovante" className="w-full rounded-lg border border-cream-200" />
        </a>

        {comprovante.valor_total != null && (
          <p className="text-sm text-ink-700">
            <span className="text-ink-400">Valor total: </span>
            R$ {comprovante.valor_total.toFixed(2)}
          </p>
        )}

        {comprovante.confirmado ? (
          <p className="text-sm text-ink-500">
            Este comprovante já foi confirmado. {comprovante.produtos_ids.length} produto(s) criado(s).
          </p>
        ) : (
          <Confirmar
            comprovanteId={comprovante.id}
            itens={comprovante.itens_identificados}
            onSucesso={onConfirmado}
          />
        )}

        {comprovante.texto_extraido && (
          <details className="text-xs">
            <summary className="cursor-pointer text-ink-400">
              Texto extraído (OCR)
            </summary>
            <pre className="mt-2 bg-cream-100 border border-cream-200 rounded-md p-3 whitespace-pre-wrap text-ink-500 font-mono text-[11px] leading-relaxed">
{comprovante.texto_extraido}
            </pre>
          </details>
        )}
      </div>
    </Modal>
  );
}

function Confirmar({ comprovanteId, itens, onSucesso }) {
  const inicial = itens.length > 0
    ? itens.map((i) => ({
        tipo: "validade",
        nome: i.nome,
        data_validade: "",
        data_compra: "",
        garantia_meses: 12,
        numero_serie: "",
      }))
    : [{ tipo: "validade", nome: "", data_validade: "", data_compra: "", garantia_meses: 12, numero_serie: "" }];
  const [linhas, setLinhas] = useState(inicial);
  const [erro, setErro] = useState(null);

  function atualizar(idx, k, v) {
    setLinhas(linhas.map((l, i) => i === idx ? { ...l, [k]: v } : l));
  }
  function remover(idx) {
    setLinhas(linhas.filter((_, i) => i !== idx));
  }
  function adicionar() {
    setLinhas([...linhas, { tipo: "validade", nome: "", data_validade: "", data_compra: "", garantia_meses: 12, numero_serie: "" }]);
  }

  const mutation = useMutation({
    mutationFn: (produtos) => api.confirmar(comprovanteId, produtos),
    onSuccess: onSucesso,
    onError: (err) => setErro(err.response?.data?.erro || err.response?.data?.erros?.[0]?.msg || "Erro ao confirmar"),
  });

  function onConfirmar(e) {
    e.preventDefault();
    setErro(null);
    const payload = linhas.map((l) => {
      if (l.tipo === "validade") {
        return { tipo: "validade", nome: l.nome, data_validade: l.data_validade };
      }
      return {
        tipo: "garantia",
        nome: l.nome,
        data_compra: l.data_compra,
        garantia_meses: Number(l.garantia_meses),
        numero_serie: l.numero_serie || null,
      };
    });
    mutation.mutate(payload);
  }

  return (
    <form onSubmit={onConfirmar} className="space-y-4">
      <p className="text-sm text-ink-500">
        {itens.length > 0
          ? `${itens.length} item(ns) identificados — revise e complete os dados`
          : "Nenhum item identificado — adicione manualmente"}
      </p>

      {linhas.map((l, idx) => (
        <div key={idx} className="bg-cream-100 border border-cream-200 rounded-xl p-4 space-y-3 relative">
          <button
            type="button"
            onClick={() => remover(idx)}
            className="absolute top-3 right-3 text-ink-400 hover:text-status-vencida"
            aria-label="remover"
          >
            <Trash size={16} />
          </button>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Tipo">
              <Select value={l.tipo} onChange={(e) => atualizar(idx, "tipo", e.target.value)}>
                <option value="validade">Com Validade</option>
                <option value="garantia">Com Garantia</option>
              </Select>
            </Field>
            <Field label="Nome">
              <Input value={l.nome} onChange={(e) => atualizar(idx, "nome", e.target.value)} required />
            </Field>
          </div>

          {l.tipo === "validade" ? (
            <Field label="Validade">
              <Input
                type="date"
                value={l.data_validade}
                onChange={(e) => atualizar(idx, "data_validade", e.target.value)}
                required
              />
            </Field>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              <Field label="Data da compra">
                <Input
                  type="date"
                  value={l.data_compra}
                  onChange={(e) => atualizar(idx, "data_compra", e.target.value)}
                  required
                />
              </Field>
              <Field label="Garantia (meses)">
                <Input
                  type="number"
                  value={l.garantia_meses}
                  onChange={(e) => atualizar(idx, "garantia_meses", e.target.value)}
                  min={1}
                  max={120}
                  required
                />
              </Field>
            </div>
          )}
        </div>
      ))}

      <button
        type="button"
        onClick={adicionar}
        className="inline-flex items-center gap-1 text-sm font-medium text-amber-accent hover:text-ink-900"
      >
        <Plus size={14} weight="bold" /> Adicionar outro
      </button>

      {erro && <p className="text-xs text-status-vencida">{erro}</p>}

      <div className="flex justify-end gap-2 pt-2">
        <Button type="submit" disabled={mutation.isPending || linhas.length === 0}>
          {mutation.isPending ? "Cadastrando…" : `Cadastrar ${linhas.length} produto(s)`}
        </Button>
      </div>
    </form>
  );
}
