"""Repository de Garantia.

Como Garantia está sempre amarrada a um Produto, as queries por usuário
fazem join via Produto.
"""
from app.models.garantia import Garantia
from app.models.produto import Produto
from app.repositories.base_repo import BaseRepository


class GarantiaRepository(BaseRepository[Garantia]):
    model = Garantia

    def listar_por_usuario(self, usuario_id: int) -> list[Garantia]:
        return (
            Garantia.query
            .join(Produto, Garantia.produto_id == Produto.id)
            .filter(Produto.usuario_id == usuario_id)
            .all()
        )
