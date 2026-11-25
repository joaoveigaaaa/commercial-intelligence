from datetime import date

from sqlalchemy import Float, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Cliente(Base):
    __tablename__ = "cliente"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo_rodopar: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    nome: Mapped[str | None] = mapped_column(String(200))
    cnpj: Mapped[str | None] = mapped_column(String(20))
    ativo: Mapped[bool] = mapped_column(default=True)


class SnapshotCliente(Base):
    """Totais diários de CT-e por cliente, vindos do Rodopar."""

    __tablename__ = "snapshot_cliente"
    __table_args__ = (UniqueConstraint("cliente_id", "data"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("cliente.id"), index=True)
    data: Mapped[date] = mapped_column(index=True)
    qtd_cte: Mapped[int]
    peso: Mapped[float | None] = mapped_column(Numeric(14, 3))
    frete: Mapped[float | None] = mapped_column(Numeric(14, 2))


class IndiceCliente(Base):
    """Resultado do índice de desvio por cliente, com cada sinal guardado separado."""

    __tablename__ = "indice_cliente"
    __table_args__ = (UniqueConstraint("cliente_id", "data_calculo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("cliente.id"), index=True)
    data_calculo: Mapped[date] = mapped_column(index=True)
    indice: Mapped[float | None] = mapped_column(Float)
    sinal_ritmo: Mapped[float | None] = mapped_column(Float)
    sinal_recencia: Mapped[float | None] = mapped_column(Float)
    sinal_tendencia: Mapped[float | None] = mapped_column(Float)
    classificacao: Mapped[str] = mapped_column(String(20))
