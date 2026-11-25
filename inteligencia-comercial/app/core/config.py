from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    sistema_db_url: str = ""
    rodopar_db_url: str = ""

    rodopar_view_cte: str = "vw_cte"
    rodopar_coluna_cliente: str = "PAGDOC"
    rodopar_coluna_data: str = "DATDOC"
    rodopar_coluna_peso: str = "PESO"
    rodopar_coluna_frete: str = "TOTFRE"
    rodopar_coluna_situacao: str = "SITUAC"
    rodopar_situacoes_validas: str = ""

    anthropic_api_key: str = ""
    jwt_secret: str = "trocar"

    @property
    def situacoes_validas(self) -> list[str]:
        return [s.strip() for s in self.rodopar_situacoes_validas.split(",") if s.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
