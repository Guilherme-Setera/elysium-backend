from fastapi import APIRouter
from psycopg2.extensions import cursor as PGCursor
from src.repository.utils import db_connection, get_query_postgres

infra = APIRouter(prefix="/api/infra", tags=["infra"])

@infra.get("/healthcheck_postgres")
def check_postgres() -> dict:
    try:
        with db_connection(True) as conn:
            with conn.cursor() as cursor: 
                query = get_query_postgres("healthcheck.sql")
                cursor.execute(query)
        return {"status": "ok", "db": "postgres"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
