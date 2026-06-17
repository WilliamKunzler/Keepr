import { createContext, useCallback, useContext, useRef, useState } from "react";

import { Button } from "../components/Button";
import { Modal } from "../components/Modal";

const ConfirmContext = createContext(null);

const PADRAO = {
  titulo: "Tem certeza?",
  texto: "",
  confirmar: "Confirmar",
  cancelar: "Cancelar",
  perigo: false,
};

/**
 * Provider de confirmação. Renderiza um único Modal reutilizável e expõe,
 * via useConfirm(), uma função `confirmar(opts)` que devolve uma Promise<boolean>:
 *
 *   const confirmar = useConfirm();
 *   if (await confirmar({ titulo, texto, perigo: true })) { ... }
 */
export function ConfirmProvider({ children }) {
  const [estado, setEstado] = useState(null);
  const resolverRef = useRef(null);

  const confirmar = useCallback((opts = {}) => {
    return new Promise((resolve) => {
      resolverRef.current = resolve;
      setEstado({ ...PADRAO, ...opts });
    });
  }, []);

  const responder = useCallback((resultado) => {
    resolverRef.current?.(resultado);
    resolverRef.current = null;
    setEstado(null);
  }, []);

  return (
    <ConfirmContext.Provider value={confirmar}>
      {children}
      {estado && (
        <Modal
          open
          onClose={() => responder(false)}
          title={estado.titulo}
          footer={
            <>
              <Button variant="ghost" onClick={() => responder(false)}>
                {estado.cancelar}
              </Button>
              <Button
                variant={estado.perigo ? "danger" : "primary"}
                onClick={() => responder(true)}
              >
                {estado.confirmar}
              </Button>
            </>
          }
        >
          <p className="text-sm text-ink-700 leading-relaxed whitespace-pre-line">
            {estado.texto}
          </p>
        </Modal>
      )}
    </ConfirmContext.Provider>
  );
}

export function useConfirm() {
  const ctx = useContext(ConfirmContext);
  if (!ctx) throw new Error("useConfirm precisa estar dentro de ConfirmProvider");
  return ctx;
}
