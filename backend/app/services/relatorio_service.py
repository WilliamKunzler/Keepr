from typing import Any

from app.models.categoria import Categoria
from app.models.garantia import Garantia
from app.models.produto import Produto, ProdutoValidade, ProdutoGarantia
from app.models.relatorio import Relatorio
from app.models.usuario import Usuario
from app.repositories.relatorio_repo import RelatorioRepository
from app.utils import utcnow


class RelatorioService:
    def __init__(self, repo: RelatorioRepository):
        self.repo = repo

    def gerar(self, tipo: str, administrador_id: int) -> Relatorio:
        gerador = self._geradores.get(tipo)
        if gerador is None:
            raise ValueError(f"Tipo de relatório desconhecido: {tipo!r}")

        conteudo = gerador(self)
        relatorio = Relatorio(
            tipo=tipo,
            administrador_id=administrador_id,
            data_geracao=utcnow(),
        )
        relatorio.conteudo = conteudo
        return self.repo.save(relatorio)

    def _produtos_por_categoria(self) -> dict[str, Any]:
        categorias = Categoria.query.all()
        sem_categoria = Produto.query.filter_by(categoria_id=None).count()
        return {
            "total_produtos": Produto.query.count(),
            "por_categoria": [
                {
                    "categoria": c.nome,
                    "quantidade": len(c.produtos),
                    "validade": sum(1 for p in c.produtos if p.tipo == "validade"),
                    "garantia": sum(1 for p in c.produtos if p.tipo == "garantia"),
                }
                for c in categorias
            ],
            "sem_categoria": sem_categoria,
        }

    def _produtos_vencendo(self) -> dict[str, Any]:
        produtos = ProdutoValidade.query.all()
        em_risco = [p for p in produtos if p.esta_em_risco(7)]
        vencidos = [p for p in produtos if p.esta_vencido()]
        return {
            "total_validade": len(produtos),
            "em_risco_7_dias": len(em_risco),
            "vencidos": len(vencidos),
            "itens_em_risco": [
                {"id": p.id, "nome": p.nome, "dias": p.dias_para_vencer()}
                for p in em_risco
            ],
        }

    def _garantias_vencendo(self) -> dict[str, Any]:
        produtos = ProdutoGarantia.query.all()
        em_risco = [p for p in produtos if p.esta_em_risco(30)]
        return {
            "total_garantia": len(produtos),
            "garantias_em_risco_30_dias": len(em_risco),
            "itens_em_risco": [
                {
                    "id": p.id,
                    "nome": p.nome,
                    "dias_restantes": p.garantia.dias_restantes() if p.garantia else None,
                }
                for p in em_risco
            ],
        }

    def _resumo_geral(self) -> dict[str, Any]:
        return {
            "usuarios": Usuario.query.count(),
            "produtos": Produto.query.count(),
            "validade": ProdutoValidade.query.count(),
            "garantia": ProdutoGarantia.query.count(),
            "garantias": Garantia.query.count(),
            "categorias": Categoria.query.count(),
        }

    _geradores = {
        "produtos_por_categoria": _produtos_por_categoria,
        "produtos_vencendo": _produtos_vencendo,
        "garantias_vencendo": _garantias_vencendo,
        "resumo_geral": _resumo_geral,
    }
