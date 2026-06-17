"""Testes do padrão Factory Method (ProdutoFactory) e da extensibilidade (OCP)."""
from datetime import date

import pytest

from app.models.factories import ProdutoFactory
from app.models.produto import ProdutoAlimenticio, ProdutoEletronico

HOJE = date.today()


def test_factory_cria_subclasse_correta():
    a = ProdutoFactory.criar("alimenticio", nome="Leite", data_validade=HOJE)
    e = ProdutoFactory.criar("eletronico", nome="TV", data_compra=HOJE)
    assert isinstance(a, ProdutoAlimenticio)
    assert isinstance(e, ProdutoEletronico)


def test_factory_tipos_disponiveis():
    tipos = set(ProdutoFactory.tipos_disponiveis())
    assert {"alimenticio", "eletronico"} <= tipos


def test_factory_tipo_desconhecido_levanta_value_error():
    with pytest.raises(ValueError):
        ProdutoFactory.criar("inexistente", nome="X")


def test_factory_ocp_registrar_novo_tipo():
    """OCP: dá pra registrar um tipo novo sem alterar a Factory."""
    class Dummy:
        def __init__(self, **kwargs):
            self.dados = kwargs

    ProdutoFactory.registrar("dummy", Dummy)
    try:
        obj = ProdutoFactory.criar("dummy", nome="Qualquer")
        assert isinstance(obj, Dummy)
        assert obj.dados["nome"] == "Qualquer"
        assert "dummy" in ProdutoFactory.tipos_disponiveis()
    finally:
        ProdutoFactory._registro.pop("dummy", None)
