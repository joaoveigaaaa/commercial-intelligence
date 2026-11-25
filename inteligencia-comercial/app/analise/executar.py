"""Calcula e grava o índice de todos os clientes a partir dos snapshots."""
from datetime import date, timedelta

import pandas as pd
from sqlalchemy import delete, select

from app.analise.score import calcular_cliente, classificar
from app.core.db import sessao_sistema
from app.models import IndiceCliente, SnapshotCliente


def calcular_indices(hoje: date | None = None) -> int:
    hoje = hoje or date.today()
    with sessao_sistema() as s:
        linhas = s.execute(
            select(SnapshotCliente.cliente_id, SnapshotCliente.data, SnapshotCliente.qtd_cte)
            .where(SnapshotCliente.data >= hoje - timedelta(days=400))
        ).all()
        if not linhas:
            return 0
        df = pd.DataFrame(linhas, columns=["cliente_id", "data", "qtd_cte"])

        resultados = {cid: calcular_cliente(g, hoje) for cid, g in df.groupby("cliente_id")}
        indices = pd.Series({cid: r.indice for cid, r in resultados.items()}, dtype=float)
        classes = classificar(indices)

        s.execute(delete(IndiceCliente).where(IndiceCliente.data_calculo == hoje))
        s.add_all(
            IndiceCliente(
                cliente_id=int(cid), data_calculo=hoje, indice=r.indice,
                sinal_ritmo=r.ritmo, sinal_recencia=r.recencia, sinal_tendencia=r.tendencia,
                classificacao=classes[cid],
            )
            for cid, r in resultados.items()
        )
        s.commit()
        return len(resultados)
