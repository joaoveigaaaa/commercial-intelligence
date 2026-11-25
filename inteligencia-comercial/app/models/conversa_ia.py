from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UnicodeText
from sqlalchemy.orm import Mapped, mapped_column

from app.models.alerta import agora
from app.models.base import Base


class ConversaIA(Base):
    __tablename__ = "conversa_ia"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario: Mapped[str] = mapped_column(String(100), index=True)
    titulo: Mapped[str | None] = mapped_column(String(200))
    criada_em: Mapped[datetime] = mapped_column(DateTime, default=agora)


class MensagemIA(Base):
    __tablename__ = "mensagem_ia"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversa_id: Mapped[int] = mapped_column(ForeignKey("conversa_ia.id"), index=True)
    papel: Mapped[str] = mapped_column(String(20))  # user | assistant
    conteudo: Mapped[str] = mapped_column(UnicodeText)  # JSON dos blocos de conteúdo
    criada_em: Mapped[datetime] = mapped_column(DateTime, default=agora)
