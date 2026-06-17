"""Schemas Pydantic de Produto.

Validações semânticas (RN08):
- data_validade não pode ser muito no passado (mais de 1 ano)
- data_compra não pode ser no futuro
"""
from datetime import date, timedelta
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = None
    categoria_id: Optional[int] = None


class ProdutoValidadeCreate(ProdutoBase):
    tipo: Literal["validade"] = "validade"
    data_validade: date

    @field_validator("data_validade")
    @classmethod
    def _validade_razoavel(cls, v: date) -> date:
        limite_passado = date.today() - timedelta(days=365)
        if v < limite_passado:
            raise ValueError("data_validade muito antiga (mais de 1 ano atrás)")
        return v


class ProdutoGarantiaCreate(ProdutoBase):
    tipo: Literal["garantia"] = "garantia"
    numero_serie: Optional[str] = None
    data_compra: date
    garantia_meses: int = Field(..., ge=1, le=120)

    @field_validator("data_compra")
    @classmethod
    def _compra_nao_futura(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("data_compra não pode estar no futuro")
        return v


class ProdutoUpdate(BaseModel):
    """Update parcial — não troca `tipo` (subclass STI é imutável)."""

    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descricao: Optional[str] = None
    categoria_id: Optional[int] = None
    data_validade: Optional[date] = None
    numero_serie: Optional[str] = None
    data_compra: Optional[date] = None

    @field_validator("data_compra")
    @classmethod
    def _compra_nao_futura(cls, v: Optional[date]) -> Optional[date]:
        if v and v > date.today():
            raise ValueError("data_compra não pode estar no futuro")
        return v


class ProdutoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: Optional[str]
    tipo: str
    categoria_id: Optional[int]
