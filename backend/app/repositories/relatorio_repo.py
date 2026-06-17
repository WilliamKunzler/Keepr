"""Repository de Relatorio."""
from app.models.relatorio import Relatorio
from app.repositories.base_repo import BaseRepository


class RelatorioRepository(BaseRepository[Relatorio]):
    model = Relatorio

    def listar_por_administrador(self, administrador_id: int) -> list[Relatorio]:
        return (
            Relatorio.query
            .filter_by(administrador_id=administrador_id)
            .order_by(Relatorio.data_geracao.desc())
            .all()
        )
