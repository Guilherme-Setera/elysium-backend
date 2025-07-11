import datetime as dt
from datetime import timezone
from jose import jwt
from src.infra.config.config import settings


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = int(
        (dt.datetime.now(timezone.utc) + dt.timedelta(minutes=settings.JWT_TOKEN_EXPIRE_MINUTES)).timestamp()
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = int(
        (dt.datetime.now(timezone.utc) + dt.timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_refresh_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])