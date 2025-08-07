from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field

class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    descricao: Optional[str] = Field(None, max_length=500)
    validade: Optional[date] = None
    preco_custo: float = Field(..., gt=0)
    preco_venda: float = Field(..., gt=0)
    data_referencia: Optional[date] = None

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = Field(None, max_length=500)
    validade: Optional[date] = None
    estoque_minimo: Optional[int] = Field(None, ge=0)

class ProdutoUpdateComId(ProdutoUpdate):
    id: int

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
    preco_custo: Optional[float]
    preco_venda: Optional[float]
    data_preco: Optional[date]
    estoque_minimo: Optional[int] 

    class Config:
        orm_mode = True
