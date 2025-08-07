from pydantic import BaseModel
from datetime import date
from typing import Optional

class CategoriaCustoCreate(BaseModel):
    nome: str

class CategoriaCustoResponse(BaseModel):
    id: int
    nome: str


class MovimentacaoCreate(BaseModel):
    produto_id: int
    quantidade: float
    operacao_id: int
    preco_custo: float | None = None
    preco_venda: float | None = None
    data_referencia: date


class EstoqueAtualResponse(BaseModel):
    produto_id: int
    nome_produto: str
    saldo_estoque: int
    preco_custo: float | None = None
    preco_venda: float | None = None
    data_movimentacao: Optional[date] = None


class EstoqueBaixoResponse(BaseModel):
    produto_id: int
    nome_produto: str
    saldo_estoque: int
    estoque_minimo: int | None = None


class OperacaoResponse(BaseModel):
    id: int
    descricao: str
    tipo: str

class ProdutoCreate(BaseModel):
    nome: str
    descricao: str | None = None
    validade: date | None = None
    ativo: Optional[bool] = True
    estoque_minimo: Optional[int] = None


class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    validade: Optional[date] = None
    ativo: bool
    estoque_minimo: int | None = None


class ProdutoPrecoResponse(BaseModel):
    id: int
    produto_id: int
    data_referencia: date
    preco_custo: float
    preco_venda: float
    data_fim: Optional[date] = None


class PrecoAtualResponse(BaseModel):
    nome: str
    preco_custo: float
    preco_venda: float
    estoque: int

class PrecoManualInput(BaseModel):
    preco_custo: float
    preco_venda: float
    data_referencia: Optional[date] = None

class CustoOperacionalCreate(BaseModel):
    categoria_id: int
    valor: float
    data_referencia: date
    observacao: Optional[str] = None


class CustoOperacionalResponse(BaseModel):
    id: int
    categoria_id: int
    nome_categoria: Optional[str] = None
    valor: float
    data_referencia: date
    observacao: Optional[str] = None


class CustoEstoqueResponse(BaseModel):
    produto_id: int
    nome_produto: str
    data_movimentacao: date
    quantidade: float
    preco_custo: float
    custo_total: float
