from __future__ import annotations
from pydantic import BaseModel, model_validator, Field
from decimal import Decimal
from datetime import date, datetime
from typing import Optional, Literal


class CategoriaCustoCreate(BaseModel):
    nome: str


class CategoriaCustoResponse(BaseModel):
    id: int
    nome: str


class MovimentacaoCreate(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)
    operacao_id: int
    venda_id: Optional[int] = None
    preco_custo: Optional[float] = None
    preco_venda: Optional[float] = None
    data_mov: Optional[datetime] = None
    lote_numero: Optional[int] = None
    data_validade: Optional[date] = None
    tipo: Optional[Literal["entrada", "saida"]] = None

    @model_validator(mode="after")
    def validar_regras_tabela(self) -> "MovimentacaoCreate":
        if (self.preco_custo is None) ^ (self.preco_venda is None):
            raise ValueError("Se enviar preço, envie preco_custo e preco_venda juntos.")
        if self.tipo == "saida":
            if self.preco_custo is not None or self.preco_venda is not None:
                raise ValueError("Para 'saida', preco_custo e preco_venda devem ser nulos.")
        elif self.tipo == "entrada":
            if self.preco_custo is not None and self.preco_custo < 0:
                raise ValueError("preco_custo deve ser >= 0 para 'entrada'.")
            if self.preco_venda is not None and self.preco_venda < 0:
                raise ValueError("preco_venda deve ser >= 0 para 'entrada'.")
        if self.data_validade and self.data_mov and self.data_validade < self.data_mov.date():
            raise ValueError("data_validade não pode ser anterior à data_mov.")
        return self


class MovimentacaoUpdate(BaseModel):
    produto_id: Optional[int] = None
    tipo: Optional[Literal["entrada", "saida"]] = None
    quantidade: Optional[int] = Field(default=None, gt=0)
    data_mov: Optional[datetime] = None
    operacao_id: Optional[int] = None
    venda_id: Optional[int] = None
    lote_numero: Optional[int] = None
    data_validade: Optional[date] = None
    preco_custo: Optional[float] = None
    preco_venda: Optional[float] = None

    @model_validator(mode="after")
    def validar_precos(self) -> "MovimentacaoUpdate":
        if (self.preco_custo is None) ^ (self.preco_venda is None):
            raise ValueError("Se enviar preço, envie preco_custo e preco_venda juntos.")
        if self.tipo == "saida":
            if self.preco_custo is not None or self.preco_venda is not None:
                raise ValueError("Para 'saida', preco_custo e preco_venda devem ser nulos.")
        elif self.tipo == "entrada":
            if self.preco_custo is not None and self.preco_custo < 0:
                raise ValueError("preco_custo deve ser >= 0 para 'entrada'.")
            if self.preco_venda is not None and self.preco_venda < 0:
                raise ValueError("preco_venda deve ser >= 0 para 'entrada'.")
        if self.data_validade and self.data_mov and self.data_validade < self.data_mov.date():
            raise ValueError("data_validade não pode ser anterior à data_mov.")
        return self


class EstoqueAtualResponse(BaseModel):
    produto_id: int
    nome_produto: str
    saldo_estoque: int
    preco_custo: Optional[Decimal] = None
    preco_venda: Optional[Decimal] = None
    data_movimentacao: Optional[date] = None
    ultima_mov_id: Optional[int] = None
    ultima_quantidade: Optional[int] = None
    tipo_ultima: Optional[Literal["entrada", "saida"]] = None
    operacao_id_ultima: Optional[int] = None
    lote_ultimo: Optional[int] = None
    model_config = {"from_attributes": True}


class EstoqueBaixoResponse(BaseModel):
    produto_id: int
    nome_produto: str
    saldo_estoque: int
    estoque_minimo: Optional[int] = None


class OperacaoResponse(BaseModel):
    id: int
    descricao: str
    tipo: Literal["entrada", "saida", "ajuste"] 


class ProdutoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    validade: Optional[date] = None
    ativo: Optional[bool] = True
    estoque_minimo: Optional[int] = None


class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    validade: Optional[date] = None
    ativo: bool
    estoque_minimo: Optional[int] = None


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
    quantidade: int
    preco_custo: float
    custo_total: float
