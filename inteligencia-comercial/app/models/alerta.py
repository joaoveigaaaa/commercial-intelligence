from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UnicodeText
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


def agora() -> datetime:
    return datetime.now(timezone.utc)


class Alerta(Base):
    """Cada alerta vira uma 'mensagem' na conversa do cliente."""

    __tablename__ = "alerta"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("cliente.id"), index=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=agora, index=True)
    tipo: Mapped[str] = mapped_column(String(40))
    titulo: Mapped[str] = mapped_column(String(200))
    corpo: Mapped[str] = mapped_column(UnicodeText)
    dados_json: Mapped[str | None] = mapped_column(UnicodeText)
    lido: Mapped[bool] = mapped_column(default=False)
