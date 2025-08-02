import urllib.parse
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, model_validator


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local",  # apenas usado localmente
        env_nested_delimiter="__",
        extra="allow"
    )

    PROJECT_NAME: str = "Ambrosia API"
    PROJECT_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "local"  # usado para condicional, logs etc.

    # PostgreSQL
    POSTGRES_SERVER: str
    POSTGRES_DATABASE: str
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str

    # SQL Server (opcional)
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
        if self.ORIGINS.strip() == "*":
            return []
        return [origin.strip() for origin in self.ORIGINS.split(";") if origin.strip()]

    @computed_field
    @property
    def POSTGRES_CONN_SQLALCHEMY(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DATABASE}?sslmode=require"
        )

    @computed_field
    @property
    def POSTGRES_CONN_PSYCO(self) -> str:
        return (
            f"host={self.POSTGRES_SERVER} "
            f"dbname={self.POSTGRES_DATABASE} "
            f"user={self.POSTGRES_USERNAME} "
            f"password={self.POSTGRES_PASSWORD} "
            f"sslmode=require"
        )

    @computed_field
    @property
    def SQLSERVER_CONN(self) -> str:
        username = urllib.parse.quote_plus(self.SQLSERVER_USERNAME)
        password = urllib.parse.quote_plus(self.SQLSERVER_PASSWORD)
        return (
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server={self.SQLSERVER_SERVER};"
            f"Database={self.SQLSERVER_DATABASE};"
            f"Uid={username};"
            f"Pwd={password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=yes;"
            f"Connection Timeout=30;"
        )

    @model_validator(mode="after")
    def validar_postgres_obrigatorio(self):
        if not all([
            self.POSTGRES_SERVER,
            self.POSTGRES_DATABASE,
            self.POSTGRES_USERNAME,
            self.POSTGRES_PASSWORD,
            self.JWT_SECRET_KEY
        ]):
            raise ValueError("Todos os campos obrigatórios do PostgreSQL/JWT precisam estar definidos.")
        return self


settings = ApiSettings()  # type: ignore
