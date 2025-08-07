from datetime import date
from pydantic import BaseModel, EmailStr
from typing import Optional


class ClienteBase(BaseModel):
    nome: str
    celular: str
    endereco: Optional[str] = None
    email: Optional[str] = None
    cpf: Optional[str] = None
    descricao: Optional[str] = None


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(ClienteBase):
    pass


class ClienteResponse(ClienteBase):
    id: int
    descricao: Optional[str] = None
    dt_start: Optional[date] = None
