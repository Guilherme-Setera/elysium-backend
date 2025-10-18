from fastapi import HTTPException, status
from contextlib import suppress
import pyotp

from src.modules.auth.models.schemas import TokenRequest, Token, UserOut, RegisterRequest, ChangePasswordRequest
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
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha incorretos")
        if bool(user_data.get("totp_enabled", False)):
            code = req.totp_code or ""
            if len(code) < 6:
                raise HTTPException(status_code=status.HTTP_428_PRECONDITION_REQUIRED, detail="mfa_requerido")
            secret = str(user_data.get("totp_secret", ""))
            totp = pyotp.TOTP(secret)
            ok = totp.verify(code, valid_window=1)
            if not ok:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="mfa_invalido")
            import time as _t
            current_interval = int(_t.time() // totp.interval)
            last_interval = int(user_data.get("totp_last_interval", 0))
            if current_interval == last_interval:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="mfa_replay")
            repository.update_totp_last_interval(req.username, current_interval)
        access_token = token_utils.create_access_token({"sub": f"username:{req.username}"})
        return Token(access_token=access_token, token_type="bearer", user=UserOut(full_name=user_data["nome"]))
    finally:
        with suppress(StopIteration):
            next(gen)

def register_user(req: RegisterRequest) -> int:
    gen = get_postgres_cursor()
    cursor = next(gen)
    try:
        repository = AuthRepository(cursor)
        exists = repository.get_user_by_login(req.email)
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="login_em_uso")
        pwd_hash = password_utils.hash_password(req.senha)
        user_id = repository.insert_user(req.nome, req.email, pwd_hash, req.role)
        return user_id
    finally:
        with suppress(StopIteration):
            next(gen)

def change_password(req: ChangePasswordRequest) -> None:
    gen = get_postgres_cursor()
    cursor = next(gen)
    try:
        repository = AuthRepository(cursor)
        user = repository.get_user_by_id(req.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="usuario_nao_encontrado")
        if not password_utils.verify_password(req.senha_atual, user["senha_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="senha_atual_invalida")
        new_hash = password_utils.hash_password(req.senha_nova)
        repository.update_password(req.user_id, new_hash)
    finally:
        with suppress(StopIteration):
            next(gen)
