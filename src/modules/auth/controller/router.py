from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.modules.auth.models.schemas import TokenRequest, Token
from src.modules.auth.usecase.auth_usecase import validate_and_create_access_token

router = APIRouter(prefix="/api/autenticacao", tags=["Autenticação"])


@router.post("/auth", response_model=Token)
def autorizar_json(req: TokenRequest) -> Token:
    return validate_and_create_access_token(req)


@router.post("/auth_form", response_model=Token)
def autorizar_form(req: OAuth2PasswordRequestForm = Depends()) -> Token:
    token_request = TokenRequest(username=req.username, password=req.password)
    return validate_and_create_access_token(token_request)
