# src/infra/db/connection.py

from __future__ import annotations
from contextlib import contextmanager
from typing import Generator, Optional

import psycopg2
from psycopg2.extensions import connection as PGConnection, cursor as PGCursor
from psycopg2.extras import RealDictCursor
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine.url import URL

from src.infra.config.config import settings  # <-- use o settings central

APP_NAME = "elysium-backend"

def _sqlalchemy_url() -> str:
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=settings.POSTGRES_USERNAME,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DATABASE,
        query={"sslmode": settings.POSTGRES_SSLMODE or "disable", "application_name": APP_NAME},
    )
    return str(url)

def _psycopg2_dsn() -> str:
    parts = {
        "host": settings.POSTGRES_SERVER,
        "port": str(settings.POSTGRES_PORT),
        "dbname": settings.POSTGRES_DATABASE,
        "user": settings.POSTGRES_USERNAME,
        "password": settings.POSTGRES_PASSWORD,
        "sslmode": settings.POSTGRES_SSLMODE or "disable",
        "application_name": APP_NAME,
    }
    def esc(v: str) -> str:
        return v.replace("\\", "\\\\").replace("'", "\\'")
    kv = [f"{k}='{esc(v)}'" for k, v in parts.items() if v]
    return " ".join(kv)

SQLALCHEMY_DATABASE_URL = settings.POSTGRES_CONN_SQLALCHEMY
engine: Engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

def get_postgres_connection() -> PGConnection:
    import psycopg2
    return psycopg2.connect(settings.POSTGRES_CONN_PSYCO)

@contextmanager
def get_postgres_cursor() -> Generator[PGCursor, None, None]:
    conn: Optional[PGConnection] = None
    cur: Optional[PGCursor] = None
    try:
        conn = get_postgres_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        yield cur
        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
