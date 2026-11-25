"""Leitura do Rodopar. Só SELECT, só na view configurada, agregando no servidor."""
import re
from datetime import date

import pandas as pd
from sqlalchemy import bindparam, text

from app.core.config import get_settings
from app.core.db import engine_rodopar

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$")


def _ident(valor: str) -> str:
    """Valida e coloca colchetes em nomes de tabela/coluna vindos da configuração."""
    if not _IDENT.match(valor):
        raise ValueError(f"Identificador inválido na configuração: {valor!r}")
    return ".".join(f"[{parte}]" for parte in valor.split("."))


def buscar_ctes_por_dia(inicio: date) -> pd.DataFrame:
    """Retorna: cliente_codigo, data, qtd_cte, peso, frete (um registro por cliente/dia)."""
    c = get_settings()
    view, cli, dat = _ident(c.rodopar_view_cte), _ident(c.rodopar_coluna_cliente), _ident(c.rodopar_coluna_data)
    peso, frete = _ident(c.rodopar_coluna_peso), _ident(c.rodopar_coluna_frete)

    filtro = ""
    params: dict = {"inicio": inicio}
    if c.situacoes_validas:
        filtro = f"AND {_ident(c.rodopar_coluna_situacao)} IN :sits"
        params["sits"] = c.situacoes_validas

    sql = f"""
        SELECT CAST({cli} AS varchar(40)) AS cliente_codigo,
               CAST({dat} AS date)        AS data,
               COUNT(*)                   AS qtd_cte,
               SUM({peso})                AS peso,
               SUM({frete})               AS frete
        FROM {view}
        WHERE {dat} >= :inicio {filtro}
        GROUP BY CAST({cli} AS varchar(40)), CAST({dat} AS date)
    """
    assert sql.lstrip().upper().startswith("SELECT")  # trava de somente leitura
    stmt = text(sql)
    if "sits" in params:
        stmt = stmt.bindparams(bindparam("sits", expanding=True))

    with engine_rodopar().connect() as conn:
        return pd.read_sql(stmt, conn, params=params)
