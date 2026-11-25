"""Duas conexões separadas: banco do sistema (leitura/escrita) e Rodopar (somente leitura)."""
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.config import get_settings


@lru_cache
def engine_sistema() -> Engine:
    return create_engine(
        get_settings().sistema_db_url, pool_pre_ping=True, fast_executemany=True
    )


@lru_cache
def engine_rodopar() -> Engine:
    # READ UNCOMMITTED evita bloquear o ERP (equivale a NOLOCK). Use também um login
    # com permissão apenas de SELECT nas views liberadas.
    return create_engine(
        get_settings().rodopar_db_url, pool_pre_ping=True, isolation_level="READ UNCOMMITTED"
    )


def sessao_sistema() -> Session:
    return Session(engine_sistema())
