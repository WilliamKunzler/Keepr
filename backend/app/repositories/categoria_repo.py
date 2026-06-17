"""Repository de Categoria."""
from app.models.categoria import Categoria
from app.repositories.base_repo import BaseRepository


class CategoriaRepository(BaseRepository[Categoria]):
    model = Categoria

    def get_por_nome(self, nome: str) -> Categoria | None:
        return Categoria.query.filter_by(nome=nome).first()
