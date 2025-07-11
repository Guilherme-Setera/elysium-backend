from typing import Generator
import psycopg2
from psycopg2.extensions import connection as PGConnection, cursor as PGCursor
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.infra.config.config import settings

# SQLAlchemy engine e session
engine: Engine = create_engine(settings.POSTGRES_CONN_SQLALCHEMY) 
SessionLocal: sessionmaker[Session] = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Conexão psycopg2 bruta
def get_postgres_connection() -> PGConnection:
    conn = psycopg2.connect(settings.POSTGRES_CONN_PSYCO)
    conn.autocommit = settings.AUTOCOMMIT
    return conn

# Cursor psycopg2 bruto
def get_postgres_cursor() -> Generator[PGCursor, None, None]:
    conn = get_postgres_connection()
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        conn.close()

# Sessão ORM padrão para FastAPI
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
