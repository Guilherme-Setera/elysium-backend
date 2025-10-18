from typing import Optional, Literal
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field


class ItemConsumoCreate(BaseModel):
    nome: str
    ativo: bool = True
    estoque_minimo: Optional[int] = Field(default=None, ge=0)


class ItemConsumoUpdate(BaseModel):
    nome: Optional[str] = None
    ativo: Optional[bool] = None
    estoque_minimo: Optional[int] = Field(default=None, ge=0)
    limpar_estoque_minimo: Optional[bool] = None


class ItemConsumoResponse(BaseModel):
    id: int
    nome: str
    ativo: bool
    estoque_minimo: Optional[int] = None


class MovimentacaoItemProducaoEntradaCreate(BaseModel):
    item_consumo_id: int
    quantidade: int = Field(..., ge=1)
    preco_custo: Decimal = Field(..., ge=0)
    data_movimentacao: Optional[datetime] = None
    is_ativo: bool = True
    descricao: Optional[str] = None


class MovimentacaoItemConsumoResponse(BaseModel):
    id: int
    item_consumo_id: int
    quantidade: int
    data_movimentacao: datetime
    is_entrada: bool
    lote: Optional[int] = None
    preco_custo: Optional[Decimal] = None
    receita_id: Optional[int] = None
    is_ativo: Optional[bool] = None
    descricao: Optional[str] = None

    @property
    def tipo(self) -> Literal["entrada", "saida"]:
        return "entrada" if self.is_entrada else "saida"


class MovimentacaoItemConsumoFiltro(BaseModel):
    item_consumo_id: Optional[int] = None
    data_inicial: Optional[datetime] = None
    data_final: Optional[datetime] = None
    tipo: Optional[Literal["entrada", "saida"]] = None


class MovimentacaoItemConsumoListResponse(BaseModel):
    id: int
    item_consumo_id: int
    nome_item_consumo: str
    quantidade: int
    data_movimentacao: datetime
    is_entrada: bool
    lote: Optional[int] = None
    preco_custo: Optional[Decimal] = None
    receita_id: Optional[int] = None
    is_ativo: Optional[bool] = None
    descricao: Optional[str] = None

    @property
    def tipo(self) -> Literal["entrada", "saida"]:
        return "entrada" if self.is_entrada else "saida"

class MovimentacaoItemProducaoResponse(BaseModel):
    id: int
    item_consumo_id: int
    nome_item: str
    quantidade: int
    preco_custo: Optional[Decimal] = None
    data_movimentacao: datetime
    lote: Optional[int] = None
    is_entrada: bool
    receita_id: Optional[int] = None
    nome_receita: Optional[str] = None
    is_ativo: Optional[bool] = None
    descricao: Optional[str] = None

    @property
    def tipo(self) -> Literal["entrada", "saida"]:
        return "entrada" if self.is_entrada else "saida"


class EstoqueAtualItemProducaoResponse(BaseModel):
    item_producao_id: int
    nome_item_producao: str
    saldo_atual: int
    ultimo_preco_custo: Decimal | None = None
    data_ultima_movimentacao: datetime | None = None
    proximo_lote_fifo: int | None = None