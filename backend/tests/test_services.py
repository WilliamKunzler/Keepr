"""Testes dos services (com banco PostgreSQL de teste).

Cobrem o Facade (ProdutoService), RF02/RF03, o RelatorioService e a integração
do Observer (InAppSubscriber persistindo Notificacao).
"""
from datetime import date, timedelta

import pytest

from app.models.garantia import Garantia
from app.models.notificacao import Notificacao
from app.models.produto import ProdutoAlimenticio, ProdutoEletronico
from app.repositories.produto_repo import ProdutoRepository
from app.repositories.relatorio_repo import RelatorioRepository
from app.schemas.produto import (
    ProdutoAlimenticioCreate,
    ProdutoEletronicoCreate,
    ProdutoUpdate,
)
from app.services.events import EventBus
from app.services.notificacao_service import InAppSubscriber
from app.services.produto_service import ProdutoService
from app.services.relatorio_service import RelatorioService

HOJE = date.today()


def _produto_service():
    return ProdutoService(repo=ProdutoRepository())


# --- Facade: cadastro -------------------------------------------------------

def test_facade_cadastra_eletronico_com_garantia(db, usuario):
    """ProdutoService coordena Factory + Repository + cascade da Garantia."""
    dto = ProdutoEletronicoCreate(nome="Notebook", data_compra=date(2025, 1, 10), garantia_meses=24)
    produto = _produto_service().cadastrar_produto_eletronico(dto, usuario.id)

    assert produto.id is not None
    assert produto.garantia is not None
    assert produto.garantia.data_fim == date(2027, 1, 10)


def test_facade_cadastra_alimenticio(db, usuario):
    dto = ProdutoAlimenticioCreate(nome="Leite", data_validade=HOJE + timedelta(days=5))
    produto = _produto_service().cadastrar_produto_alimenticio(dto, usuario.id)

    assert produto.id is not None
    assert produto.tipo == "alimenticio"
    assert produto.usuario_id == usuario.id


# --- RF02: edição recalcula garantia ----------------------------------------

def test_rf02_atualizar_data_compra_recalcula_garantia(db, usuario):
    svc = _produto_service()
    produto = svc.cadastrar_produto_eletronico(
        ProdutoEletronicoCreate(nome="TV", data_compra=date(2025, 1, 1), garantia_meses=12),
        usuario.id,
    )
    assert produto.garantia.data_fim == date(2026, 1, 1)

    svc.atualizar(produto, ProdutoUpdate(data_compra=date(2025, 6, 1)))
    assert produto.garantia.data_fim == date(2026, 6, 1)


# --- RF03: exclusão remove produto e garantia (cascade) ---------------------

def test_rf03_excluir_remove_produto_e_garantia(db, usuario):
    svc = _produto_service()
    produto = svc.cadastrar_produto_eletronico(
        ProdutoEletronicoCreate(nome="Geladeira", data_compra=HOJE, garantia_meses=12),
        usuario.id,
    )
    produto_id, garantia_id = produto.id, produto.garantia.id

    svc.excluir(produto)

    assert db.session.get(ProdutoEletronico, produto_id) is None
    assert db.session.get(Garantia, garantia_id) is None


# --- RelatorioService -------------------------------------------------------

def test_relatorio_resumo_geral(db, usuario):
    _produto_service().cadastrar_produto_alimenticio(
        ProdutoAlimenticioCreate(nome="Leite", data_validade=HOJE + timedelta(days=5)),
        usuario.id,
    )
    relatorio = RelatorioService(repo=RelatorioRepository()).gerar("resumo_geral", usuario.id)

    assert relatorio.id is not None
    assert relatorio.conteudo["produtos"] == 1
    assert relatorio.conteudo["usuarios"] == 1


def test_relatorio_tipo_desconhecido_levanta_erro(db, usuario):
    svc = RelatorioService(repo=RelatorioRepository())
    with pytest.raises(ValueError):
        svc.gerar("inexistente", usuario.id)


# --- Observer integrado: InAppSubscriber persiste Notificacao ---------------

def test_observer_inapp_persiste_notificacao(db, usuario):
    produto = ProdutoAlimenticio(
        nome="Leite", data_validade=HOJE + timedelta(days=3), usuario_id=usuario.id
    )
    db.session.add(produto)
    db.session.commit()

    bus = EventBus()
    bus.subscribe("produto_vencendo", InAppSubscriber())
    bus.publish("produto_vencendo", {"produto": produto, "dias": 3})

    notificacoes = Notificacao.query.filter_by(usuario_id=usuario.id).all()
    assert len(notificacoes) == 1
    assert "vence em 3" in notificacoes[0].mensagem
    assert notificacoes[0].tipo == "validade_proxima"
