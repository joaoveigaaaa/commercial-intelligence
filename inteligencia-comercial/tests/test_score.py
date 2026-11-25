from datetime import date, timedelta

import numpy as np
import pandas as pd

from app.analise.score import calcular_cliente, classificar

HOJE = date(2026, 11, 24)


def _cliente(ritmo_base, ritmo_recente, semanas=30, seed=0, sem_cte_dias=0):
    rng = np.random.default_rng(seed)
    linhas = []
    for i in range(semanas * 7):
        dia = HOJE - timedelta(days=semanas * 7 - i + sem_cte_dias)
        taxa = ritmo_recente if (semanas * 7 - i) <= 28 else ritmo_base
        n = rng.poisson(taxa)
        if n:
            linhas.append({"data": dia, "qtd_cte": n})
    return pd.DataFrame(linhas)


def test_cliente_estavel_fica_perto_de_zero():
    s = calcular_cliente(_cliente(2.0, 2.0), HOJE)
    assert s.indice is not None and s.indice > -1.5


def test_cliente_em_queda_tem_indice_menor():
    estavel = calcular_cliente(_cliente(2.0, 2.0), HOJE)
    queda = calcular_cliente(_cliente(2.0, 0.3, seed=1), HOJE)
    assert queda.indice < estavel.indice
    assert queda.ritmo < -2


def test_historico_curto_nao_gera_indice():
    s = calcular_cliente(_cliente(2.0, 2.0, semanas=5), HOJE)
    assert s.ritmo is None


def test_classificacao_por_percentis():
    idx = pd.Series([0.2, 0.1, -0.2, -1.5, -3.0, -5.0, np.nan])
    c = classificar(idx)
    assert c.iloc[-1] == "sem_historico"
    assert c.iloc[5] == "critico"
    assert c.iloc[0] == "saudavel"
