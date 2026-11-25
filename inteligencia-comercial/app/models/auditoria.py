from datetime import datetime

from sqlalchemy import DateTime, String, UnicodeText
from sqlalchemy.orm import Mapped, mapped_column

from app.models.alerta import agora
from app.models.base import Base


class Auditoria(Base):
    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario: Mapped[str] = mapped_column(String(100), index=True)
    acao: Mapped[str] = mapped_column(String(60))  # ex.: ferramenta_ia, relatorio, login
    detalhe: Mapped[str | None] = mapped_column(UnicodeText)
    criada_em: Mapped[datetime] = mapped_column(DateTime, default=agora, index=True)
