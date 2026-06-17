from typing import Any

from app.models.produto import Produto, ProdutoValidade, ProdutoGarantia


class ProdutoFactory:
    _registro: dict[str, type[Produto]] = {
        "validade": ProdutoValidade,
        "garantia": ProdutoGarantia,
    }

    @classmethod
    def registrar(cls, tipo: str, classe: type[Produto]) -> None:
        cls._registro[tipo] = classe

    @classmethod
    def criar(cls, tipo: str, **dados: Any) -> Produto:
        if tipo not in cls._registro:
            raise ValueError(
                f"Tipo de produto desconhecido: {tipo!r}. "
                f"Tipos disponíveis: {list(cls._registro.keys())}"
            )
        classe = cls._registro[tipo]
        return classe(**dados)

    @classmethod
    def tipos_disponiveis(cls) -> list[str]:
        return list(cls._registro.keys())
