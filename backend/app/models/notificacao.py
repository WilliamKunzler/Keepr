"""Model Notificacao.

Alertas in-app emitidos pelo InAppSubscriber quando jobs detectam produtos
em risco. O usuário consulta via GET /notificacoes.
"""
from app.extensions import db
from app.utils import utcnow


class Notificacao(db.Model):
    __tablename__ = "notificacoes"

    id = db.Column(db.Integer, primary_key=True)
    mensagem = db.Column(db.String(500), nullable=False)
    tipo = db.Column(db.String(40), nullable=False)
    data_envio = db.Column(db.DateTime, default=utcnow)
    lida = db.Column(db.Boolean, default=False)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"))

    def marcar_como_lida(self) -> None:
        self.lida = True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "mensagem": self.mensagem,
            "tipo": self.tipo,
            "data_envio": self.data_envio.isoformat() if self.data_envio else None,
            "lida": self.lida,
            "produto_id": self.produto_id,
        }

    def __repr__(self) -> str:
        return f"<Notificacao {self.tipo} usuario={self.usuario_id}>"
