from app.models.produto import Produto, ProdutoValidade, ProdutoGarantia
from app.repositories.base_repo import BaseRepository


class ProdutoRepository(BaseRepository[Produto]):
    model = Produto

    def listar_por_usuario(self, usuario_id: int) -> list[Produto]:
        return Produto.query.filter_by(usuario_id=usuario_id).all()

    def get_do_usuario(self, produto_id: int, usuario_id: int) -> Produto | None:
        """Lookup que já valida ownership. Evita vazar produto de outro usuário."""
        produto = self.get(produto_id)
        if produto is None or produto.usuario_id != usuario_id:
            return None
        return produto

    def buscar_por_nome(self, usuario_id: int, termo: str) -> list[Produto]:
        padrao = f"%{termo}%"
        return (
            Produto.query
            .filter(Produto.usuario_id == usuario_id, Produto.nome.ilike(padrao))
            .all()
        )

    def listar_validade_em_risco(
        self, usuario_id: int, dias_antecedencia: int = 7
    ) -> list[ProdutoValidade]:
        produtos = ProdutoValidade.query.filter_by(usuario_id=usuario_id).all()
        return [p for p in produtos if p.esta_em_risco(dias_antecedencia)]

    def listar_garantia_em_risco(
        self, usuario_id: int, dias_antecedencia: int = 30
    ) -> list[ProdutoGarantia]:
        produtos = ProdutoGarantia.query.filter_by(usuario_id=usuario_id).all()
        return [p for p in produtos if p.esta_em_risco(dias_antecedencia)]
