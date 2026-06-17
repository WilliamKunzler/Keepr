from app.extensions import db
from app.models.usuario import Usuario
from app.repositories.base_repo import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    model = Usuario

    def get_por_email(self, email: str) -> Usuario | None:
        return Usuario.query.filter_by(email=email).first()

    def excluir_em_cascata(self, usuario: Usuario) -> None:
        from app.models.comprovante import Comprovante
        from app.models.notificacao import Notificacao
        from app.models.produto import Produto
        from app.models.relatorio import Relatorio

        # Notificações referenciam usuario_id e produto_id — apagar primeiro.
        Notificacao.query.filter_by(usuario_id=usuario.id).delete()

        # Produtos via ORM (não bulk) para disparar o cascade de Garantia.
        for produto in Produto.query.filter_by(usuario_id=usuario.id).all():
            db.session.delete(produto)

        Comprovante.query.filter_by(usuario_id=usuario.id).delete()
        Relatorio.query.filter_by(administrador_id=usuario.id).delete()

        db.session.delete(usuario)
        db.session.commit()
