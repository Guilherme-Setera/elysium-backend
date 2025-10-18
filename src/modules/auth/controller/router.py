# src/modules/auth/controller/router.py
from fastapi import APIRouter, Depends, Response, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.modules.auth.models.schemas import TokenRequest, Token, RegisterRequest, ChangePasswordRequest, UserOut
from src.modules.auth.usecase.auth_usecase import validate_and_create_access_token, register_user, change_password
from src.modules.auth.security.dependencies import validate_token
from src.modules.auth.security.token_utils import set_access_cookie, clear_access_cookie, decode_access_token

router = APIRouter(prefix="/api/autenticacao", tags=["Autenticação"])

@router.post("/auth", response_model=Token)
def autorizar_json(req: TokenRequest, response: Response) -> Token:
    token = validate_and_create_access_token(req)
    set_access_cookie(response, token.access_token)
    return token

@router.post("/auth_form", response_model=Token)
def autorizar_form(
    response: Response,
    req: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    token_request = TokenRequest(username=req.username, password=req.password)
    token = validate_and_create_access_token(token_request)
    set_access_cookie(response, token.access_token)
    return token

@router.post("/logout")
def logout(response: Response) -> dict:
    clear_access_cookie(response)
    return {"ok": True}

@router.post("/register", response_model=int)
def cadastrar_usuario(req: RegisterRequest) -> int:
    return register_user(req)

@router.put("/change_password")
def alterar_senha(req: ChangePasswordRequest, _: str = Depends(validate_token)) -> dict:
    change_password(req)
    return {"ok": True}

@router.get("/me", response_model=UserOut)
def me(request: Request) -> UserOut:
    from src.modules.auth.security.token_utils import ACCESS_COOKIE_NAME
    token = request.cookies.get(ACCESS_COOKIE_NAME)
    if not token:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
    data = decode_access_token(token)
    full_name = data.get("full_name") or data.get("username") or "Usuário"
    return UserOut(full_name=full_name)
