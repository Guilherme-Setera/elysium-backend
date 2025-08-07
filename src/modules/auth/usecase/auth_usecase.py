from fastapi import HTTPException, status
from contextlib import suppress

from src.modules.auth.models.schemas import TokenRequest, Token, UserOut
from src.modules.auth.repository.auth_repository import AuthRepository
from src.modules.auth.security import password_utils, token_utils
from src.infra.db.connection import get_postgres_cursor


def validate_and_create_access_token(req: TokenRequest) -> Token:
    gen = get_postgres_cursor()
    cursor = next(gen)
    try:
        repository = AuthRepository(cursor)
        users_dict, _ = repository.get_users_details()

        user_data = users_dict.get(req.username)

        if not user_data or not password_utils.verify_password(req.password, user_data["pwd_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou senha incorretos"
            )

        access_token = token_utils.create_access_token({"sub": req.username})

        print('[DEBUG] Dados do usuário retornado:', user_data["nome"])
        print('[DEBUG] Token retornado:', access_token)

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserOut(full_name=user_data["nome"])
        )

    finally:
        with suppress(StopIteration):
            next(gen)
