from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UnicodeText
from sqlalchemy.orm import Mapped, mapped_column

from app.models.alerta import agora
from app.models.base import Base

COLUNAS = ["novo_alerta", "em_analise", "contato_feito", "em_negociacao", "recuperado", "perdido"]


class CardKanban(Base):
    __tablename__ = "card_kanban"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("cliente.id"), index=True)
    coluna: Mapped[str] = mapped_column(String(30), default="novo_alerta", index=True)
    responsavel: Mapped[str | None] = mapped_column(String(100))
    notas: Mapped[str | None] = mapped_column(UnicodeText)
    motivo_perda: Mapped[str | None] = mapped_column(String(200))
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=agora)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=agora, onupdate=agora)
