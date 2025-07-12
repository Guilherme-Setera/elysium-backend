from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,  # <-- Não usa mais .env
        env_nested_delimiter="__",
        extra="allow"
    )

    PROJECT_NAME: str = "Ambrosia API"
    PROJECT_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "local"

    # PostgreSQL (Neon)
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
    ORIGINS: list[str] = ["*"]

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
        return (
            "Driver={ODBC Driver 18 for SQL Server};"
            f"Server={self.SQLSERVER_SERVER};"
            f"Database={self.SQLSERVER_DATABASE};"
            f"Uid={self.SQLSERVER_USERNAME};"
            f"Pwd={self.SQLSERVER_PASSWORD};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
            "Connection Timeout=30;"
        )


settings = ApiSettings()  # type: ignore
