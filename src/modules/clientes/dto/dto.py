from pydantic import BaseModel, EmailStr
from typing import Optional


class ClienteBase(BaseModel):
    nome: str
    celular: str
    endereco: str
    email: str | None
    cpf: str | None


class ClienteCreate(ClienteBase):
    nome: str
    celular: str
    endereco: str
    email: str | None
    cpf: str | None


class ClienteUpdate(ClienteBase):
    pass


class ClienteResponse(ClienteBase):
    id: int
