"""Fixtures compartilhadas dos testes.

Os testes de regras de negócio, factory, models e EventBus são **puros** (não
tocam banco). Os testes de service usam um **PostgreSQL de teste** (`keepr_test`,
definido em `TestConfig`) — schema recriado a cada teste para isolamento.

Pré-requisito dos testes de service:
    CREATE DATABASE keepr_test;   (ou defina TEST_DATABASE_URL)
"""
import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db as _db
from app.models.usuario import Cliente


@pytest.fixture(scope="session")
def app():
    """Aplicação única para a sessão de testes (TestConfig → keepr_test)."""
    application = create_app(TestConfig)
    yield application


@pytest.fixture()
def db(app):
    """Schema limpo por teste: cria as tabelas, entrega a sessão, derruba no fim."""
    with app.app_context():
        _db.drop_all()
        _db.create_all()
        try:
            yield _db
        finally:
            _db.session.remove()
            _db.drop_all()


@pytest.fixture()
def usuario(db):
    """Um Cliente persistido — dono dos produtos nos testes de service."""
    u = Cliente(nome="Teste", email="teste@exemplo.com")
    u.set_senha("senha123")
    db.session.add(u)
    db.session.commit()
    return u
