"""Testes das Regras de Negócio (RN01–RN13) no nível de validação.

A maioria das RNs é garantida pelos schemas Pydantic (entrada da API) e pela
ProdutoFactory (RN13). São testes puros — não dependem de banco.
"""
from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.models.factories import ProdutoFactory
from app.models.produto import ProdutoValidade, ProdutoGarantia
from app.schemas.comprovante import ConfirmarComprovante
from app.schemas.produto import (
    ProdutoValidadeCreate,
    ProdutoGarantiaCreate,
    ProdutoUpdate,
)

HOJE = date.today()


# RN01 — todo produto deve possuir um nome válido
def test_rn01_nome_vazio_invalido():
    with pytest.raises(ValidationError):
        ProdutoValidadeCreate(nome="", data_validade=HOJE)


def test_rn01_nome_valido_aceito():
    dto = ProdutoValidadeCreate(nome="Leite", data_validade=HOJE)
    assert dto.nome == "Leite"


# RN02 — controlados por validade exigem data de vencimento
def test_rn02_validade_sem_data_invalido():
    with pytest.raises(ValidationError):
        ProdutoValidadeCreate(nome="Leite")


# RN03 — controlados por garantia exigem data de compra
def test_rn03_garantia_sem_data_compra_invalido():
    with pytest.raises(ValidationError):
        ProdutoGarantiaCreate(nome="TV", garantia_meses=12)


# RN04 — garantia em meses, entre 1 e 120
@pytest.mark.parametrize("meses", [0, -5, 121, 999])
def test_rn04_garantia_meses_fora_do_intervalo(meses):
    with pytest.raises(ValidationError):
        ProdutoGarantiaCreate(nome="TV", data_compra=HOJE, garantia_meses=meses)


def test_rn04_garantia_meses_valida():
    dto = ProdutoGarantiaCreate(nome="TV", data_compra=HOJE, garantia_meses=24)
    assert dto.garantia_meses == 24


# RN05 — um produto pertence a apenas uma categoria principal (escalar, não lista)
def test_rn05_categoria_principal_unica():
    dto = ProdutoValidadeCreate(nome="Leite", data_validade=HOJE, categoria_id=3)
    assert isinstance(dto.categoria_id, int)
    assert dto.categoria_id == 3


# RN08 — não permitir datas inválidas
def test_rn08_data_compra_futura_invalida():
    with pytest.raises(ValidationError):
        ProdutoGarantiaCreate(
            nome="TV", data_compra=HOJE + timedelta(days=10), garantia_meses=12
        )


def test_rn08_validade_muito_antiga_invalida():
    with pytest.raises(ValidationError):
        ProdutoValidadeCreate(nome="Leite", data_validade=HOJE - timedelta(days=400))


def test_rn08_update_data_compra_futura_invalida():
    with pytest.raises(ValidationError):
        ProdutoUpdate(data_compra=HOJE + timedelta(days=5))


# RN12 — editar informações extraídas; confirmar exige ao menos 1 item
def test_rn12_confirmar_lista_vazia_invalida():
    with pytest.raises(ValidationError):
        ConfirmarComprovante(produtos=[])


def test_rn12_confirmar_aceita_produtos_editados():
    c = ConfirmarComprovante(
        produtos=[
            {"tipo": "validade", "nome": "Leite editado", "data_validade": HOJE.isoformat()},
            {
                "tipo": "garantia",
                "nome": "Cafeteira",
                "data_compra": HOJE.isoformat(),
                "garantia_meses": 24,
            },
        ]
    )
    assert len(c.produtos) == 2
    assert c.produtos[0].nome == "Leite editado"


# RN13 — cadastro manual quando o tipo não é reconhecido
def test_rn13_factory_tipo_desconhecido_levanta_erro():
    with pytest.raises(ValueError):
        ProdutoFactory.criar("medicamento", nome="Dipirona")


def test_rn13_factory_tipos_validos():
    a = ProdutoFactory.criar("validade", nome="Leite", data_validade=HOJE)
    e = ProdutoFactory.criar("garantia", nome="TV", data_compra=HOJE)
    assert isinstance(a, ProdutoValidade)
    assert isinstance(e, ProdutoGarantia)
