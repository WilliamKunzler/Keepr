"""Pacote de models.

Importar este pacote registra todas as classes no metadata do SQLAlchemy,
o que é necessário pra db.create_all() conhecer e criar as tabelas.
"""
from .usuario import Usuario, Cliente, Administrador
from .categoria import Categoria
from .produto import Produto, ProdutoValidade, ProdutoGarantia
from .garantia import Garantia
from .comprovante import Comprovante
from .notificacao import Notificacao
from .relatorio import Relatorio
from .factories import ProdutoFactory

__all__ = [
    "Usuario",
    "Cliente",
    "Administrador",
    "Categoria",
    "Produto",
    "ProdutoValidade",
    "ProdutoGarantia",
    "Garantia",
    "Comprovante",
    "Notificacao",
    "Relatorio",
    "ProdutoFactory",
]
