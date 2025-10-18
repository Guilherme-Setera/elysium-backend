# src/modules/auth/security/token_utils.py
import datetime as dt
from datetime import timezone
from typing import Any, Literal, cast

from fastapi import Response
from jose import jwt
from src.infra.config.config import settings

# --- Config de cookie ---
ACCESS_COOKIE_NAME = getattr(settings, "ACCESS_COOKIE_NAME", "access_token")
COOKIE_SECURE = bool(getattr(settings, "COOKIE_SECURE", False))

_raw_samesite = str(getattr(settings, "COOKIE_SAMESITE", "lax")).lower()
COOKIE_SAMESITE: Literal["lax", "strict", "none"] = cast(
    Literal["lax", "strict", "none"],
    {"lax": "lax", "strict": "strict", "none": "none"}.get(_raw_samesite, "lax"),
)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = int((dt.datetime.now(timezone.utc) + dt.timedelta(minutes=settings.JWT_TOKEN_EXPIRE_MINUTES)).timestamp())
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = int((dt.datetime.now(timezone.utc) + dt.timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)).timestamp())
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_refresh_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

def set_access_cookie(response: Response, token: str) -> None:
    max_age = int(settings.JWT_TOKEN_EXPIRE_MINUTES) * 60
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=token,
        max_age=max_age,
        expires=max_age,
        path="/",
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
    )

def clear_access_cookie(response: Response) -> None:
    response.delete_cookie(
        key=ACCESS_COOKIE_NAME,
        path="/",
        samesite=COOKIE_SAMESITE,
    )
