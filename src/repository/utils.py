import os
from typing import Generator
from contextlib import contextmanager
from psycopg2.extensions import connection as PGConnection
import psycopg2
from src.infra.config.config import settings

@contextmanager
def db_connection(autocommit: bool = True) -> Generator[PGConnection, None, None]:
    conn = psycopg2.connect(settings.POSTGRES_CONN_PSYCO)
    conn.autocommit = autocommit
    try:
        yield conn
    finally:
        conn.close()

def get_query_postgres(filename: str) -> str:
    path = os.path.join("src", "repository", "queries", "postgres", filename)
    with open(path, "r", encoding="utf-8") as file:
        return file.read()
