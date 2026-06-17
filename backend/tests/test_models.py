"""Testes dos métodos de domínio dos models (puros, sem banco).

Cobrem RN06, RN07 e RN10, além do polimorfismo de `esta_em_risco()` (LSP).
"""
from datetime import date, timedelta

from app.models.garantia import Garantia
from app.models.produto import ProdutoAlimenticio, ProdutoEletronico

HOJE = date.today()


# --- Garantia ---------------------------------------------------------------

def test_garantia_calcular_data_fim():
    assert Garantia.calcular_data_fim(date(2025, 1, 10), 24) == date(2027, 1, 10)


def test_garantia_vigente_e_vencida():
    vigente = Garantia(data_inicio=HOJE, meses=12, data_fim=HOJE + timedelta(days=30))
    vencida = Garantia(data_inicio=HOJE, meses=12, data_fim=HOJE - timedelta(days=1))
    assert vigente.esta_vigente() is True
    assert vigente.esta_vencida() is False
    assert vencida.esta_vencida() is True
    assert vencida.esta_vigente() is False


def test_garantia_dias_restantes():
    g = Garantia(data_inicio=HOJE, meses=12, data_fim=HOJE + timedelta(days=15))
    assert g.dias_restantes() == 15


# RN07 — alerta antes do fim da garantia
def test_rn07_garantia_esta_vencendo_na_janela():
    perto = Garantia(data_inicio=HOJE, meses=12, data_fim=HOJE + timedelta(days=10))
    longe = Garantia(data_inicio=HOJE, meses=12, data_fim=HOJE + timedelta(days=60))
    assert perto.esta_vencendo(30) is True
    assert longe.esta_vencendo(30) is False


# --- ProdutoAlimenticio -----------------------------------------------------

def test_alimenticio_vencido_e_dias_para_vencer():
    vencido = ProdutoAlimenticio(nome="Iogurte", data_validade=HOJE - timedelta(days=2))
    futuro = ProdutoAlimenticio(nome="Leite", data_validade=HOJE + timedelta(days=5))
    assert vencido.esta_vencido() is True
    assert vencido.dias_para_vencer() == -2
    assert futuro.esta_vencido() is False
    assert futuro.dias_para_vencer() == 5


# RN06 — alerta antes do vencimento
def test_rn06_alimenticio_em_risco():
    risco = ProdutoAlimenticio(nome="Leite", data_validade=HOJE + timedelta(days=3))
    tranquilo = ProdutoAlimenticio(nome="Arroz", data_validade=HOJE + timedelta(days=90))
    assert risco.esta_em_risco(7) is True
    assert tranquilo.esta_em_risco(7) is False


# RN10 — vencidos destacados (to_dict expõe status)
def test_rn10_to_dict_expoe_vencido_e_dias():
    p = ProdutoAlimenticio(nome="Leite", data_validade=HOJE + timedelta(days=3))
    d = p.to_dict()
    assert d["vencido"] is False
    assert d["dias_para_vencer"] == 3


# --- Polimorfismo (LSP) -----------------------------------------------------

def test_polimorfismo_esta_em_risco():
    """Subclasses respondem ao mesmo contrato com critérios próprios."""
    alimenticio = ProdutoAlimenticio(nome="X", data_validade=HOJE + timedelta(days=1))
    eletronico = ProdutoEletronico(nome="Y", data_compra=HOJE)  # sem garantia
    assert alimenticio.esta_em_risco(7) is True
    assert eletronico.esta_em_risco(30) is False
