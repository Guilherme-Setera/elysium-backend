from fastapi import APIRouter
from contextlib import contextmanager
from psycopg2.extensions import cursor as PGCursor
from src.repository.utils import db_connection, get_query_postgres


infra = APIRouter(prefix="/api/infra", tags=["infra"])


@infra.get("/healthcheck_postgres")
def check_postgres() -> str:
    with db_connection(True) as conn:
        cursor: PGCursor = conn.cursor()
        query = get_query_postgres("healthcheck.sql")
        cursor.execute(query)
        conn.close()
        return "Ok"
