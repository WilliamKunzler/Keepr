import { useEffect } from "react";
import { X } from "@phosphor-icons/react";

export function Modal({ open, onClose, title, children, footer }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-ink-900/40 backdrop-blur-sm p-0 sm:p-6">
      <div
        className="bg-cream-50 w-full max-w-lg rounded-t-2xl sm:rounded-xl shadow-xl max-h-[92vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-5 pt-4 pb-2.5 flex items-center justify-between border-b border-cream-200">
          <h2 className="font-display text-lg font-semibold text-ink-900 leading-none">{title}</h2>
          <button
            onClick={onClose}
            className="text-ink-400 hover:text-ink-700 transition-colors p-0.5 rounded"
            aria-label="Fechar"
          >
            <X size={20} />
          </button>
        </div>
        <div className="px-5 py-4 overflow-y-auto flex-1">{children}</div>
        {footer && <div className="px-5 py-3 border-t border-cream-200 flex items-center justify-end gap-2">{footer}</div>}
      </div>
    </div>
  );
}
