"""Utilitários compartilhados."""
from datetime import datetime, timezone


def utcnow() -> datetime:
    """UTC atual, *naïve* (sem tzinfo).

    Substitui o `datetime.utcnow()` (deprecado a partir do Python 3.12)
    preservando o comportamento original: as colunas `db.DateTime` são naïve e
    o `.isoformat()` usado nos `to_dict()` continua sem offset de fuso.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
