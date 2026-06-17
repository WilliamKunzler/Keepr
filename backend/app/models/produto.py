from datetime import date

from app.extensions import db
from app.utils import utcnow


class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    tipo = db.Column(db.String(20), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=utcnow)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"))
    comprovante_id = db.Column(
        db.Integer, db.ForeignKey("comprovantes.id"), nullable=True
    )

    # Colunas específicas de subclasses — nullable em STI
    data_validade = db.Column(db.Date, nullable=True)
    numero_serie = db.Column(db.String(80), nullable=True)
    data_compra = db.Column(db.Date, nullable=True)

    categoria = db.relationship("Categoria", back_populates="produtos")
    garantia = db.relationship(
        "Garantia", back_populates="produto", uselist=False, cascade="all, delete-orphan"
    )
    comprovante = db.relationship("Comprovante", back_populates="produtos")

    __mapper_args__ = {
        "polymorphic_on": tipo,
        "polymorphic_identity": "produto",
    }

    def esta_em_risco(self, dias_antecedencia: int = 30) -> bool:
        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "tipo": self.tipo,
            "categoria_id": self.categoria_id,
            "categoria": self.categoria.nome if self.categoria else None,
            "usuario_id": self.usuario_id,
            "data_cadastro": self.data_cadastro.isoformat() if self.data_cadastro else None,
        }

    def __repr__(self) -> str:
        return f"<Produto {self.nome} ({self.tipo})>"


class ProdutoValidade(Produto):
    __mapper_args__ = {"polymorphic_identity": "validade"}

    def esta_vencido(self) -> bool:
        return bool(self.data_validade and self.data_validade < date.today())

    def dias_para_vencer(self) -> int | None:
        if not self.data_validade:
            return None
        return (self.data_validade - date.today()).days

    def esta_em_risco(self, dias_antecedencia: int = 7) -> bool:
        dias = self.dias_para_vencer()
        return dias is not None and 0 <= dias <= dias_antecedencia

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "data_validade": self.data_validade.isoformat() if self.data_validade else None,
            "vencido": self.esta_vencido(),
            "dias_para_vencer": self.dias_para_vencer(),
        })
        return base


class ProdutoGarantia(Produto):
    __mapper_args__ = {"polymorphic_identity": "garantia"}

    def possui_garantia_ativa(self) -> bool:
        return bool(self.garantia and self.garantia.esta_vigente())

    def esta_em_risco(self, dias_antecedencia: int = 30) -> bool:
        if not self.garantia:
            return False
        dias = self.garantia.dias_restantes()
        return dias is not None and 0 <= dias <= dias_antecedencia

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "numero_serie": self.numero_serie,
            "data_compra": self.data_compra.isoformat() if self.data_compra else None,
            "possui_garantia_ativa": self.possui_garantia_ativa(),
            "garantia": self.garantia.to_dict() if self.garantia else None,
        })
        return base
