import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Trash, UserCircle, Bell, CheckCircle, WarningCircle } from "@phosphor-icons/react";

import { Button } from "../components/Button";
import { useAuth } from "../contexts/AuthContext";
import { useConfirm } from "../contexts/ConfirmContext";
import { usuarios as api } from "../api/endpoints";

export function Usuarios() {
  const { usuario: atual } = useAuth();
  const qc = useQueryClient();
  const confirmar = useConfirm();

  // feedback por usuário: { [id]: "ok" | "erro" | "nenhum" }
  const [feedback, setFeedback] = useState({});

  const lista = useQuery({
    queryKey: ["usuarios"],
    queryFn: () => api.list(),
  });

  const excluir = useMutation({
    mutationFn: (id) => api.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["usuarios"] }),
  });

  const notificar = useMutation({
    mutationFn: (id) => api.notificarVencimentos(id),
    onSuccess: (data, id) => {
      const estado = data.produtos_em_risco === 0 ? "nenhum" : "ok";
      setFeedback((prev) => ({ ...prev, [id]: estado }));
      if (data.produtos_em_risco > 0) {
        qc.invalidateQueries({ queryKey: ["notificacoes"] });
      }
      setTimeout(() => setFeedback((prev) => ({ ...prev, [id]: undefined })), 4000);
    },
    onError: (_err, id) => {
      setFeedback((prev) => ({ ...prev, [id]: "erro" }));
      setTimeout(() => setFeedback((prev) => ({ ...prev, [id]: undefined })), 4000);
    },
  });

  async function onDelete(u) {
    const ok = await confirmar({
      titulo: `Excluir ${u.nome}`,
      texto:
        "Isso remove também todos os produtos, comprovantes, notificações e " +
        "relatórios dele.\n\nEsta ação é irreversível.",
      confirmar: "Excluir usuário",
      perigo: true,
    });
    if (ok) excluir.mutate(u.id);
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink-900 tracking-tight">
          Usuários
        </h1>
        <p className="text-sm text-ink-500 mt-1">Contas cadastradas no sistema.</p>
      </div>

      {lista.isLoading ? (
        <p className="text-sm text-ink-400">Carregando…</p>
      ) : lista.data?.length === 0 ? (
        <div className="bg-cream-50 border border-dashed border-cream-200 rounded-xl py-10 text-center">
          <p className="text-sm text-ink-500">Nenhum usuário.</p>
        </div>
      ) : (
        <ul className="space-y-2">
          {lista.data.map((u) => {
            const ehVoce = u.id === atual?.id;
            const fb = feedback[u.id];
            const notificando = notificar.isPending && notificar.variables === u.id;

            return (
              <li
                key={u.id}
                className="bg-white border border-cream-200 rounded-xl p-3 flex items-center justify-between gap-3 shadow-sm"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-9 h-9 rounded-full bg-ink-100 flex items-center justify-center shrink-0 text-ink-500">
                    <UserCircle size={22} weight="fill" />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-display text-base font-semibold text-ink-900 leading-tight truncate">
                        {u.nome}
                      </h3>
                      <span
                        className={`text-xs px-2 py-0.5 rounded ${
                          u.tipo === "admin"
                            ? "bg-amber-accent/15 text-amber-accent"
                            : "bg-ink-900/5 text-ink-500"
                        }`}
                      >
                        {u.tipo === "admin" ? "Administrador" : "Cliente"}
                      </span>
                      {ehVoce && (
                        <span className="text-xs text-ink-400">você</span>
                      )}
                    </div>
                    <p className="text-[11px] text-ink-500 mt-0.5 truncate">{u.email}</p>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  {/* Botão Notificar Vencimentos */}
                  <button
                    onClick={() => notificar.mutate(u.id)}
                    disabled={notificando}
                    title="Verificar produtos em risco e enviar notificações"
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition-all ${
                      fb === "ok"
                        ? "bg-green-50 border-green-300 text-green-700"
                        : fb === "nenhum"
                        ? "bg-ink-50 border-ink-200 text-ink-500"
                        : fb === "erro"
                        ? "bg-red-50 border-red-300 text-red-700"
                        : "bg-amber-50 border-amber-300 text-amber-700 hover:bg-amber-100"
                    } disabled:opacity-60 disabled:cursor-not-allowed`}
                  >
                    {fb === "ok" ? (
                      <CheckCircle size={13} weight="fill" />
                    ) : fb === "erro" ? (
                      <WarningCircle size={13} weight="fill" />
                    ) : (
                      <Bell size={13} weight={fb === "nenhum" ? "regular" : "fill"} />
                    )}
                    {notificando
                      ? "Verificando…"
                      : fb === "ok"
                      ? "Notificações enviadas"
                      : fb === "nenhum"
                      ? "Nenhum item em risco"
                      : fb === "erro"
                      ? "Erro ao notificar"
                      : "Notificar Vencimentos"}
                  </button>

                  <Button
                    variant="danger"
                    onClick={() => onDelete(u)}
                    disabled={ehVoce || excluir.isPending}
                    className="!py-1 !text-xs"
                    title={ehVoce ? "Você não pode excluir a própria conta" : undefined}
                  >
                    <Trash size={13} /> Excluir
                  </Button>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
