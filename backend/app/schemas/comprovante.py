"""Schemas Pydantic de Comprovante.

A confirmação (RF16/RN11) recebe uma lista de produtos que o usuário revisou —
podem ser de validade e/ou garantia, possivelmente misturados.
"""
from typing import Union

from pydantic import BaseModel, Field

from app.schemas.produto import ProdutoValidadeCreate, ProdutoGarantiaCreate


class ConfirmarComprovante(BaseModel):
    """Lista de produtos identificados que o usuário confirmou para cadastro."""

    produtos: list[Union[ProdutoValidadeCreate, ProdutoGarantiaCreate]] = Field(
        ..., min_length=1
    )
