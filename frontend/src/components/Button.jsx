const VARIANTES = {
  primary: "bg-ink-900 text-cream-50 hover:bg-ink-800 disabled:bg-ink-300",
  amber: "bg-amber-accent text-cream-50 hover:bg-amber-accent/90 disabled:bg-amber-soft",
  ghost: "bg-transparent text-ink-900 hover:bg-ink-900/5 border border-ink-300",
  danger: "bg-status-vencida/10 text-status-vencida hover:bg-status-vencida/20 border border-status-vencida/30",
};

export function Button({
  variant = "primary",
  type = "button",
  className = "",
  children,
  ...props
}) {
  const base = "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed";
  return (
    <button type={type} className={`${base} ${VARIANTES[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}
