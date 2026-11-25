"""Rodopar -> snapshots diários no banco do sistema."""
from datetime import date, timedelta

from sqlalchemy import delete, insert, select

from app.core.db import sessao_sistema
from app.integracao.rodopar_reader import buscar_ctes_por_dia
from app.models import Cliente, SnapshotCliente


def sincronizar(dias: int = 400) -> int:
    inicio = date.today() - timedelta(days=dias)
    df = buscar_ctes_por_dia(inicio)
    if df.empty:
        return 0

    with sessao_sistema() as s:
        existentes = set(s.scalars(select(Cliente.codigo_rodopar)))
        s.add_all(Cliente(codigo_rodopar=c) for c in df["cliente_codigo"].unique() if c not in existentes)
        s.flush()
        mapa = {c.codigo_rodopar: c.id for c in s.scalars(select(Cliente))}

        s.execute(delete(SnapshotCliente).where(SnapshotCliente.data >= inicio))
        linhas = [
            {"cliente_id": mapa[r.cliente_codigo], "data": r.data, "qtd_cte": int(r.qtd_cte),
             "peso": None if r.peso != r.peso else float(r.peso),
             "frete": None if r.frete != r.frete else float(r.frete)}
            for r in df.itertuples()
        ]
        for i in range(0, len(linhas), 1000):
            s.execute(insert(SnapshotCliente), linhas[i:i + 1000])
        s.commit()
    return len(linhas)
