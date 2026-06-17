"""Schemas Pydantic de Categoria."""
from typing import Optional

from pydantic import BaseModel, Field


class CategoriaCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=80)
    descricao: Optional[str] = Field(None, max_length=255)


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=80)
    descricao: Optional[str] = Field(None, max_length=255)
