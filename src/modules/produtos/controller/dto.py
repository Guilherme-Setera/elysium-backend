from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field

class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    descricao: Optional[str] = Field(None, max_length=500)
    validade: Optional[date] = None
    preco_custo: float = Field(..., gt=0)
    preco_venda: float = Field(..., gt=0)
    data_referencia: Optional[date] = None  # Para cadastrar preço inicial em data retroativa (opcional)

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = Field(None, max_length=500)
    validade: Optional[date] = None

class ProdutoPrecoResponse(BaseModel):
    id: int
    produto_id: int
    data_referencia: date
    preco_custo: float
    preco_venda: float

class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    validade: Optional[date]
    ativo: bool
    preco_custo: Optional[float]  # Pode ser None se produto nunca teve preço cadastrado
    preco_venda: Optional[float]  # Pode ser None se produto nunca teve preço cadastrado
    data_preco: Optional[date]    # Data do preço vigente retornado na consulta

    class Config:
        orm_mode = True
