"""Schemas Pydantic de Relatorio."""
from typing import Literal

from pydantic import BaseModel


class RelatorioCreate(BaseModel):
    """O Administrador escolhe que tipo de snapshot gerar."""

    tipo: Literal[
        "produtos_por_categoria",
        "produtos_vencendo",
        "garantias_vencendo",
        "resumo_geral",
    ]
