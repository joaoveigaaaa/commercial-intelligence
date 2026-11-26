from app.core.db import engine_sistema
from app.models import Base

if __name__ == "__main__":
    Base.metadata.create_all(engine_sistema())
    print("Tabelas criadas.")
