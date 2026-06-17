import { useEffect, useState } from "react";

import { Button } from "./Button";

const KEY = "keepr_tutorial_seen";

const STEPS = [
  {
    titulo: "Bem-vindo ao Keepr",
    texto:
      "Guarde notas, acompanhe garantias e nunca mais perca um produto por vencimento. Vamos ver o essencial em 30 segundos.",
    icone: "🏠",
  },
  {
    titulo: "Cadastre seus produtos",
    texto:
      "Em Produtos você adiciona itens manualmente: com data de validade ou com garantia (data de compra + meses de cobertura).",
    icone: "📦",
  },
  {
    titulo: "Envie comprovantes",
    texto:
      "Em Comprovantes você envia a foto da nota fiscal. O sistema lê automaticamente, sugere os produtos e você só confirma.",
    icone: "🧾",
  },
  {
    titulo: "Receba alertas",
    texto:
      "Todo dia o sistema verifica o que está vencendo e gera notificações que aparecem aqui no Dashboard.",
    icone: "🔔",
  },
];

export function Tutorial({ aberto: abertoExterno, onFechar }) {
  const [interno, setInterno] = useState(false);
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (abertoExterno !== undefined) return;
    if (typeof window === "undefined") return;
    if (!localStorage.getItem(KEY)) {
      setInterno(true);
    }
  }, [abertoExterno]);

  const aberto = abertoExterno ?? interno;
  if (!aberto) return null;

  function fechar() {
    localStorage.setItem(KEY, "1");
    setInterno(false);
    setStep(0);
    onFechar?.();
  }

  function proximo() {
    if (step < STEPS.length - 1) setStep(step + 1);
    else fechar();
  }

  const s = STEPS[step];
  const ultimo = step === STEPS.length - 1;

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-ink-900/40 backdrop-blur-sm p-0 sm:p-4">
      <div className="bg-cream-50 w-full max-w-md rounded-t-2xl sm:rounded-2xl shadow-xl">
        <div className="px-6 pt-5 pb-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs text-ink-400">
              Tutorial · {step + 1} de {STEPS.length}
            </span>
            <button
              onClick={fechar}
              className="text-sm text-ink-400 hover:text-ink-700"
            >
              Pular
            </button>
          </div>

          <div className="text-5xl mb-3 leading-none">{s.icone}</div>
          <h2 className="font-display text-2xl font-semibold text-ink-900 leading-tight tracking-tight mb-2">
            {s.titulo}
          </h2>
          <p className="text-sm text-ink-700 leading-relaxed">{s.texto}</p>

          <div className="flex items-center gap-1.5 mt-4">
            {STEPS.map((_, i) => (
              <span
                key={i}
                className={`h-1 rounded-full transition-all ${
                  i === step ? "w-8 bg-ink-900" : "w-4 bg-ink-300"
                }`}
              />
            ))}
          </div>
        </div>

        <div className="px-6 py-3 border-t border-cream-200 flex items-center justify-between gap-2">
          <button
            onClick={() => setStep(Math.max(0, step - 1))}
            disabled={step === 0}
            className="text-sm text-ink-500 hover:text-ink-900 disabled:opacity-0"
          >
            Voltar
          </button>
          <Button onClick={proximo}>{ultimo ? "Começar" : "Próximo"}</Button>
        </div>
      </div>
    </div>
  );
}
