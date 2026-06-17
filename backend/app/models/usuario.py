from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.utils import utcnow


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    criado_em = db.Column(db.DateTime, default=utcnow)

    # Colunas específicas de subclasses — devem ser nullable em STI
    telefone = db.Column(db.String(20), nullable=True)
    nivel_acesso = db.Column(db.Integer, nullable=True)

    __mapper_args__ = {
        "polymorphic_on": tipo,
        "polymorphic_identity": "usuario",
    }

    def set_senha(self, senha: str) -> None:
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "tipo": self.tipo,
        }

    def __repr__(self) -> str:
        return f"<Usuario {self.email} ({self.tipo})>"


class Cliente(Usuario):
    __mapper_args__ = {"polymorphic_identity": "cliente"}


class Administrador(Usuario):
    __mapper_args__ = {"polymorphic_identity": "admin"}

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["nivel_acesso"] = self.nivel_acesso
        return base
