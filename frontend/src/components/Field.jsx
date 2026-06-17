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
