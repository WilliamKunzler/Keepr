"""Model Categoria.

Cada produto pertence a uma categoria principal (RN05). Categorias são
gerenciadas por administradores.
"""
from app.extensions import db


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    descricao = db.Column(db.String(255))

    produtos = db.relationship("Produto", back_populates="categoria")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
        }

    def __repr__(self) -> str:
        return f"<Categoria {self.nome}>"
