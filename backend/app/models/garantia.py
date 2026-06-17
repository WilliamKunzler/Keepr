from datetime import date

from dateutil.relativedelta import relativedelta

from app.extensions import db


class Garantia(db.Model):
    __tablename__ = "garantias"

    id = db.Column(db.Integer, primary_key=True)
    data_inicio = db.Column(db.Date, nullable=False)
    meses = db.Column(db.Integer, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    observacoes = db.Column(db.String(255))

    produto_id = db.Column(
        db.Integer, db.ForeignKey("produtos.id"), nullable=False, unique=True
    )
    produto = db.relationship("Produto", back_populates="garantia")

    @staticmethod
    def calcular_data_fim(data_inicio: date, meses: int) -> date:
        return data_inicio + relativedelta(months=meses)

    def esta_vigente(self) -> bool:
        return self.data_fim >= date.today()

    def esta_vencida(self) -> bool:
        return not self.esta_vigente()

    def esta_vencendo(self, dias_antecedencia: int = 30) -> bool:
        """Garantia vigente porém dentro da janela de alerta (PDF: estaVencendo)."""
        dias = self.dias_restantes()
        return dias is not None and 0 <= dias <= dias_antecedencia

    def dias_restantes(self) -> int | None:
        if not self.data_fim:
            return None
        return (self.data_fim - date.today()).days

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "data_inicio": self.data_inicio.isoformat() if self.data_inicio else None,
            "data_fim": self.data_fim.isoformat() if self.data_fim else None,
            "meses": self.meses,
            "vigente": self.esta_vigente(),
            "dias_restantes": self.dias_restantes(),
            "observacoes": self.observacoes,
        }

    def __repr__(self) -> str:
        return f"<Garantia produto={self.produto_id} fim={self.data_fim}>"
