"""Model Comprovante.

Guarda metadados da nota fiscal: caminho do arquivo, data de upload, texto
extraído pelo OCR. O arquivo binário em si fica em disco (UPLOAD_FOLDER).

Fluxo (RN11 + RF15):
1. Upload cria Comprovante com `confirmado=False` e a lista preliminar de
   produtos identificados em `itens_identificados` (JSON).
2. Usuário revisa e confirma via POST /comprovantes/<id>/confirmar.
3. Produtos são criados com `comprovante_id` apontando aqui; `confirmado=True`.

Um comprovante pode originar 0..N produtos (NF com vários itens). A relação
inversa fica em `Produto.comprovante_id`.
"""
import json

from app.extensions import db
from app.utils import utcnow


class Comprovante(db.Model):
    __tablename__ = "comprovantes"

    id = db.Column(db.Integer, primary_key=True)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    caminho_arquivo = db.Column(db.String(500), nullable=False)
    data_upload = db.Column(db.DateTime, default=utcnow)
    texto_extraido = db.Column(db.Text)
    valor_total = db.Column(db.Numeric(10, 2))
    confirmado = db.Column(db.Boolean, default=False, nullable=False)
    itens_identificados_json = db.Column(db.Text)

    usuario_id = db.Column(
        db.Integer, db.ForeignKey("usuarios.id"), nullable=False
    )

    produtos = db.relationship("Produto", back_populates="comprovante")

    @property
    def itens_identificados(self) -> list[dict]:
        return json.loads(self.itens_identificados_json) if self.itens_identificados_json else []

    @itens_identificados.setter
    def itens_identificados(self, value: list[dict]) -> None:
        self.itens_identificados_json = json.dumps(value, default=str)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome_arquivo": self.nome_arquivo,
            "url": f"/uploads/{self.nome_arquivo}",
            "data_upload": self.data_upload.isoformat() if self.data_upload else None,
            "texto_extraido": self.texto_extraido,
            "valor_total": float(self.valor_total) if self.valor_total is not None else None,
            "confirmado": self.confirmado,
            "itens_identificados": self.itens_identificados,
            "produtos_ids": [p.id for p in self.produtos],
        }

    def __repr__(self) -> str:
        return f"<Comprovante {self.nome_arquivo}>"
