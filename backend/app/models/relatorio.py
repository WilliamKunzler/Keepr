"""Model Relatorio.

Definido no diagrama de classes do PDF (Figura 2) como entidade gerada pelo
Administrador via `gerarRelatorio()`. Armazena snapshots agregados em JSON
no campo `conteudo` — assim o relatório pode ser exportado depois (PDF, CSV)
sem precisar recomputar nem depender da fotografia do banco no momento.
"""
import json

from app.extensions import db
from app.utils import utcnow


class Relatorio(db.Model):
    __tablename__ = "relatorios"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(40), nullable=False)
    data_geracao = db.Column(db.DateTime, default=utcnow, nullable=False)
    conteudo_json = db.Column(db.Text, nullable=False)

    administrador_id = db.Column(
        db.Integer, db.ForeignKey("usuarios.id"), nullable=False
    )

    @property
    def conteudo(self) -> dict:
        return json.loads(self.conteudo_json) if self.conteudo_json else {}

    @conteudo.setter
    def conteudo(self, value: dict) -> None:
        self.conteudo_json = json.dumps(value, default=str)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tipo": self.tipo,
            "data_geracao": self.data_geracao.isoformat() if self.data_geracao else None,
            "administrador_id": self.administrador_id,
            "conteudo": self.conteudo,
        }

    def __repr__(self) -> str:
        return f"<Relatorio {self.tipo} em {self.data_geracao}>"
