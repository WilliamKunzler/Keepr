// Classes literais — Tailwind purga classes dinâmicas.
const ESTILOS = {
  ativa: {
    rotulo: "Ativa",
    classe: "bg-status-ativa/10 text-status-ativa border-status-ativa/30",
    bolinha: "bg-status-ativa",
  },
  vencendo: {
    rotulo: "Vencendo",
    classe: "bg-status-vencendo/10 text-status-vencendo border-status-vencendo/30",
    bolinha: "bg-status-vencendo",
  },
  vencida: {
    rotulo: "Vencida",
    classe: "bg-status-vencida/10 text-status-vencida border-status-vencida/30",
    bolinha: "bg-status-vencida",
  },
};

export function statusProduto(p) {
  if (p.tipo === "validade") {
    if (p.vencido) return "vencida";
    if (p.dias_para_vencer != null && p.dias_para_vencer <= 7) return "vencendo";
    return "ativa";
  }
  if (p.tipo === "garantia") {
    const g = p.garantia;
    if (!g || !g.vigente) return "vencida";
    if (g.dias_restantes != null && g.dias_restantes <= 30) return "vencendo";
    return "ativa";
  }
  return "ativa";
}

export function StatusBadge({ status, rotulo, className = "" }) {
  const conf = ESTILOS[status] || ESTILOS.ativa;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-xs font-medium ${conf.classe} ${className}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${conf.bolinha}`} />
      {rotulo || conf.rotulo}
    </span>
  );
}
