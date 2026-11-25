"""Índice de desvio por cliente, baseado no comportamento dele mesmo (unidade: CT-e).

Cada sinal é medido em "desvios" em relação ao padrão do próprio cliente:
  0  = comportamento normal para ele
  <0 = abaixo do esperado (quanto mais negativo, mais fora do padrão)
Os níveis (crítico/alto/atenção) saem dos percentis da carteira, não de cortes fixos.
Os pesos abaixo são ponto de partida e devem ser calibrados com o histórico real.
"""
from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
import pandas as pd
from scipy import stats

JANELA_RECENTE = 4       # semanas comparadas com a base
JANELA_TENDENCIA = 12    # semanas usadas na regressão
MIN_SEMANAS_BASE = 8     # histórico mínimo anterior à janela recente
MIN_DIAS_ATIVOS = 5      # para estimar o intervalo habitual entre CT-es
LIMITE_SINAL = 6.0
PESOS = {"ritmo": 0.5, "recencia": 0.3, "tendencia": 0.2}


@dataclass
class Sinais:
    ritmo: float | None
    recencia: float | None
    tendencia: float | None
    indice: float | None
    semanas_historico: int


def _ultimo_domingo(hoje: date) -> date:
    return hoje - timedelta(days=(hoje.weekday() + 1) % 7)


def serie_semanal(df: pd.DataFrame, hoje: date) -> pd.Series:
    """df: colunas data, qtd_cte (um cliente). Semanas completas (seg–dom), zeros incluídos."""
    if df.empty:
        return pd.Series(dtype=float)
    s = df.assign(data=pd.to_datetime(df["data"])).set_index("data")["qtd_cte"].resample("W-SUN").sum()
    fim = pd.Timestamp(_ultimo_domingo(hoje))
    s = s[s.index <= fim]
    if s.empty:
        return pd.Series(dtype=float)
    return s.reindex(pd.date_range(s.index.min(), fim, freq="W-SUN"), fill_value=0).astype(float)


def _sigma(base: pd.Series | np.ndarray) -> float:
    """Desvio da base, com piso de Poisson para clientes de volume pequeno/estável."""
    mu = float(np.mean(base))
    piso = np.sqrt(mu) if mu > 0 else 1.0
    return max(float(np.std(base, ddof=1)) if len(base) > 1 else 0.0, piso)


def sinal_ritmo(semanal: pd.Series) -> float | None:
    if len(semanal) < JANELA_RECENTE + MIN_SEMANAS_BASE:
        return None
    base, recente = semanal.iloc[:-JANELA_RECENTE], semanal.iloc[-JANELA_RECENTE:]
    z = (recente.mean() - base.mean()) / (_sigma(base) / np.sqrt(JANELA_RECENTE))
    return float(np.clip(z, -LIMITE_SINAL, LIMITE_SINAL))


def sinal_recencia(df: pd.DataFrame, hoje: date) -> float | None:
    datas = sorted(pd.to_datetime(df.loc[df["qtd_cte"] > 0, "data"]).dt.date.unique())
    if len(datas) < MIN_DIAS_ATIVOS:
        return None
    intervalos = np.diff([d.toordinal() for d in datas])
    habitual = max(float(np.median(intervalos)), 1.0)
    sem_cte = max((hoje - datas[-1]).days, 0)
    razao = sem_cte / habitual
    if razao <= 1:
        return 0.0
    return float(-min(np.log2(razao), LIMITE_SINAL))


def sinal_tendencia(semanal: pd.Series) -> float | None:
    if len(semanal) < JANELA_TENDENCIA:
        return None
    y = semanal.iloc[-JANELA_TENDENCIA:].to_numpy()
    reg = stats.linregress(np.arange(len(y)), y)
    if reg.pvalue > 0.10:  # sem tendência consistente = ruído
        return 0.0
    z = reg.slope * (len(y) - 1) / _sigma(y)
    return float(np.clip(z, -LIMITE_SINAL, LIMITE_SINAL))


def combinar(ritmo, recencia, tendencia) -> float | None:
    valores = {"ritmo": ritmo, "recencia": recencia, "tendencia": tendencia}
    ativos = {k: v for k, v in valores.items() if v is not None}
    if not ativos:
        return None
    peso_total = sum(PESOS[k] for k in ativos)
    return float(sum(PESOS[k] * v for k, v in ativos.items()) / peso_total)


def calcular_cliente(df: pd.DataFrame, hoje: date) -> Sinais:
    semanal = serie_semanal(df, hoje)
    r, c, t = sinal_ritmo(semanal), sinal_recencia(df, hoje), sinal_tendencia(semanal)
    return Sinais(r, c, t, combinar(r, c, t), len(semanal))


def classificar(indices: pd.Series, piso: float = -1.0,
                cortes: tuple[float, float, float] = (0.05, 0.15, 0.35)) -> pd.Series:
    """Classifica pelos percentis da carteira. Só entra em risco quem também está abaixo do piso."""
    validos = indices.dropna()
    out = pd.Series("sem_historico", index=indices.index, dtype=object)
    if validos.empty:
        return out
    q_crit, q_alto, q_aten = (validos.quantile(q) for q in cortes)
    for idx, v in validos.items():
        if v < piso and v <= q_crit:
            out[idx] = "critico"
        elif v < piso and v <= q_alto:
            out[idx] = "alto"
        elif v < piso and v <= q_aten:
            out[idx] = "atencao"
        else:
            out[idx] = "saudavel"
    return out
