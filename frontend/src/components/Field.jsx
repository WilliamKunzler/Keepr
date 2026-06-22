import { useState } from "react";
import { Eye, EyeSlash } from "@phosphor-icons/react";

export function Field({ label, error, children, hint }) {
  return (
    <label className="block">
      {label && (
        <span className="block text-sm font-medium text-ink-700 mb-1.5">
          {label}
        </span>
      )}
      {children}
      {hint && !error && <span className="block text-xs text-ink-400 mt-1">{hint}</span>}
      {error && <span className="block text-xs text-status-vencida mt-1">{error}</span>}
    </label>
  );
}

export function Input({ className = "", ...props }) {
  return (
    <input
      className={`w-full rounded-md border border-ink-300 bg-cream-50 px-3 py-2 text-sm text-ink-900 placeholder:text-ink-400 focus:border-ink-700 focus:ring-1 focus:ring-ink-700 focus:outline-none ${className}`}
      {...props}
    />
  );
}

export function Select({ className = "", children, ...props }) {
  return (
    <select
      className={`w-full rounded-md border border-ink-300 bg-cream-50 px-3 py-2 text-sm text-ink-900 focus:border-ink-700 focus:ring-1 focus:ring-ink-700 focus:outline-none ${className}`}
      {...props}
    >
      {children}
    </select>
  );
}

export function Textarea({ className = "", ...props }) {
  return (
    <textarea
      className={`w-full rounded-md border border-ink-300 bg-cream-50 px-3 py-2 text-sm text-ink-900 placeholder:text-ink-400 focus:border-ink-700 focus:ring-1 focus:ring-ink-700 focus:outline-none ${className}`}
      {...props}
    />
  );
}

export function PasswordInput({ className = "", ...props }) {
  const [mostrar, setMostrar] = useState(false);
  return (
    <div className="relative">
      <Input
        className={`pr-10 ${className}`}
        {...props}
        type={mostrar ? "text" : "password"}
      />
      <button
        type="button"
        onClick={() => setMostrar((v) => !v)}
        tabIndex={-1}
        aria-label={mostrar ? "Ocultar senha" : "Mostrar senha"}
        title={mostrar ? "Ocultar senha" : "Mostrar senha"}
        className="absolute inset-y-0 right-0 flex items-center px-3 text-ink-400 hover:text-ink-700 transition-colors"
      >
        {mostrar ? <EyeSlash size={18} /> : <Eye size={18} />}
      </button>
    </div>
  );
}
