"""Repository de Comprovante."""
from app.models.comprovante import Comprovante
from app.repositories.base_repo import BaseRepository


class ComprovanteRepository(BaseRepository[Comprovante]):
    model = Comprovante

    def listar_por_usuario(self, usuario_id: int) -> list[Comprovante]:
        return (
            Comprovante.query
            .filter_by(usuario_id=usuario_id)
            .order_by(Comprovante.data_upload.desc())
            .all()
        )

    def get_do_usuario(self, comprovante_id: int, usuario_id: int) -> Comprovante | None:
        c = self.get(comprovante_id)
        if c is None or c.usuario_id != usuario_id:
            return None
        return c
