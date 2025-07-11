from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from typing import Callable
from src.modules.auth.security.token_utils import decode_access_token
from src.modules.auth.repository.auth_repository import AuthRepository
from infra.db.connection import get_postgres_cursor
from psycopg2.extensions import cursor as PGCursor

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/autenticacao/auth_form")


def validate_token(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        if not sub or not sub.startswith("username:"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        username = sub.split("username:")[1]
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def validate_token_with_roles(allowed_roles: list[str]) -> Callable[..., str]:
    def dependency(
        token: str = Depends(oauth2_scheme),
        cursor: PGCursor = Depends(get_postgres_cursor)
    ) -> str:
        try:
            payload = decode_access_token(token)
            sub = payload.get("sub")
            if not sub or not sub.startswith("username:"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            username = sub.split("username:")[1]
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

        repository = AuthRepository(cursor)
        users_dict, roles_dict = repository.get_users_details()

        user_roles = [
            role for role, users in roles_dict.items() if username in users
        ]

        if not any(role in allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Usuário '{username}' sem permissão (requer {allowed_roles})"
            )

        return username

    return dependency
