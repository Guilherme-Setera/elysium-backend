# src/infra/config/config.py
import os
import json
import urllib.parse
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, model_validator

_IS_LOCAL = os.getenv("ENVIRONMENT", "local").lower() == "local"


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.local",) if _IS_LOCAL else None,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    PROJECT_NAME: str = "Elysium API"
    PROJECT_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "local"

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DATABASE: str
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_SSLMODE: str | None = None

    SQLSERVER_SERVER: str = ""
    SQLSERVER_DATABASE: str = ""
    SQLSERVER_USERNAME: str = ""
    SQLSERVER_PASSWORD: str = ""

    AUTOCOMMIT: bool = True

    JWT_ALGORITHM: str = "HS256"
    JWT_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_SECRET_KEY: str

    ORIGINS: str = "*"

    @computed_field
    @property
    def origins_list(self) -> list[str]:
        raw = (self.ORIGINS or "").strip()
        if raw in ("", "*"):
            return []
        if raw.startswith("["):
            try:
                data = json.loads(raw)
                if isinstance(data, list) and all(isinstance(x, str) for x in data):
                    return [x.strip() for x in data if x.strip()]
            except Exception:
                pass
        parts = [p.strip() for p in raw.replace(",", ";").split(";")]
        return [p for p in parts if p]

    @computed_field
    @property
    def POSTGRES_CONN_PSYCO(self) -> str:
        parts = [
            f"host={self.POSTGRES_SERVER}",
            f"port={self.POSTGRES_PORT}",
            f"dbname={self.POSTGRES_DATABASE}",
            f"user={self.POSTGRES_USERNAME}",
            f"password={self.POSTGRES_PASSWORD}",
        ]
        sslmode = self._effective_sslmode()
        if sslmode:
            parts.append(f"sslmode={sslmode}")
        return " ".join(parts)

    @computed_field
    @property
    def POSTGRES_CONN_SQLALCHEMY(self) -> str:
        u = urllib.parse.quote_plus(self.POSTGRES_USERNAME)
        p = urllib.parse.quote_plus(self.POSTGRES_PASSWORD)
        q = ""
        sslmode = self._effective_sslmode()
        if sslmode:
            q = f"?sslmode={sslmode}"
        return f"postgresql+psycopg2://{u}:{p}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}{q}"

    @computed_field
    @property
    def SQLSERVER_CONN(self) -> str:
        username = urllib.parse.quote_plus(self.SQLSERVER_USERNAME or "")
        password = urllib.parse.quote_plus(self.SQLSERVER_PASSWORD or "")
        return (
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server={self.SQLSERVER_SERVER};"
            f"Database={self.SQLSERVER_DATABASE};"
            f"Uid={username};"
            f"Pwd={password};"
            f"Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
        )

    def _effective_sslmode(self) -> str | None:
        if self.POSTGRES_SSLMODE:
            return self.POSTGRES_SSLMODE
        if self.ENVIRONMENT.lower() == "local":
            return "disable"
        return None

    @model_validator(mode="after")
    def validar_postgres_obrigatorio(self):
        if not all(
            [
                self.POSTGRES_SERVER,
                self.POSTGRES_DATABASE,
                self.POSTGRES_USERNAME,
                self.POSTGRES_PASSWORD,
                self.JWT_SECRET_KEY,
            ]
        ):
            raise ValueError("Campos obrigatórios de PostgreSQL/JWT ausentes.")
        return self


settings = ApiSettings()  # type: ignore
