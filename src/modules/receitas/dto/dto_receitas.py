from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal, ROUND_FLOOR
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator
import json


class ReceitaItemMateriaPrimaCreate(BaseModel):
    materia_prima_id: int
    quantidade_unidade: Decimal = Field(default=Decimal("1"), ge=Decimal("0"))
    quantidade_medida: Decimal = Field(..., ge=Decimal("0"))
    is_grama: Optional[bool] = True

    @property
    def quantidade_total(self) -> Decimal:
        return (self.quantidade_unidade or Decimal("1")) * self.quantidade_medida


class ReceitaItemMateriaPrimaResponse(BaseModel):
    materia_prima_id: int
    nome_materia_prima: str
    quantidade_unidade: float
    quantidade_medida: float
    is_grama: Optional[bool]


class ReceitaItemProducaoCreate(BaseModel):
    item_id: int
    quantidade: Decimal = Field(..., gt=Decimal("0"))

    @property
    def quantidade_itens_int(self) -> int:
        return int(self.quantidade.to_integral_value(rounding=ROUND_FLOOR))


class ReceitaItemProducaoResponse(BaseModel):
    item_id: int
    nome_item: str
    quantidade: float
    unidade: str
    descartavel: bool = True


class ReceitaCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    ativo: Optional[bool] = True
    meia_receita: Optional[bool] = False
    produto_id: int
    materias_primas: Optional[List[ReceitaItemMateriaPrimaCreate]] = None
    itens_producao: Optional[List[ReceitaItemProducaoCreate]] = None

    @model_validator(mode="after")
    def _pelo_menos_um_item(self) -> "ReceitaCreate":
        if not self.materias_primas and not self.itens_producao:
            raise ValueError("Informe ao menos um item (matéria-prima ou item de produção).")
        return self

    def to_sql_params(self) -> Dict[str, Any]:
        itens_payload: List[Dict[str, Any]] = []
        for mp in self.materias_primas or []:
            qtd = mp.quantidade_total
            itens_payload.append({
                "materia_prima_id": mp.materia_prima_id,
                "quantidade": str(qtd)
            })
        for ip in self.itens_producao or []:
            itens_payload.append({
                "item_producao_id": ip.item_id,
                "quantidade_itens": ip.quantidade_itens_int
            })
        return {
            "produto_id": self.produto_id,
            "nome": self.nome,
            "descricao": self.descricao,
            "itens": json.dumps(itens_payload)
        }


class ReceitaInsertResponse(BaseModel):
    id: int


class ReceitaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None
    meia_receita: Optional[bool] = None


class ReceitaResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    ativo: bool
    meia_receita: bool
    produto_id: int
    produto_nome: Optional[str] = None
    materias_primas: List[ReceitaItemMateriaPrimaResponse]
    itens_producao: List[ReceitaItemProducaoResponse]


class ConsumoMateriaPrima(BaseModel):
    materia_prima_id: int
    quantidade: Decimal = Field(..., gt=Decimal("0"))
    unidade: Optional[str] = None
    custo_total: Optional[Decimal] = Field(default=None, ge=Decimal("0"))


class ConsumoItemProducao(BaseModel):
    item_producao_id: int
    quantidade_itens: int = Field(..., gt=0)
    custo_total: Optional[Decimal] = Field(default=None, ge=Decimal("0"))


class ProdutoFinalInfo(BaseModel):
    quantidade_unidades: int = Field(..., gt=0)
    preco_venda: Optional[Decimal] = Field(default=None, ge=Decimal("0"))


class FazerReceitaBody(BaseModel):
    quantidade: Optional[Decimal] = Field(default=None, gt=Decimal("0"))
    data_mov: Optional[date] = None
    is_meia_receita: Optional[bool] = False
    preco_venda: Optional[Decimal] = Field(default=None, ge=Decimal("0"))
    consumos: Optional[Dict[str, List[Dict[str, Any]]]] = None
    produto_final: Optional[ProdutoFinalInfo] = None
    idempotency_key: Optional[str] = None


class FazerReceitaInput(BaseModel):
    receita_id: int
    quantidade: Optional[Decimal] = Field(default=None, gt=Decimal("0"))
    data_mov: Optional[date] = None
    is_meia_receita: Optional[bool] = False
    preco_venda: Optional[Decimal] = Field(default=None, ge=Decimal("0"))
    consumos: Optional[Dict[str, List[Dict[str, Any]]]] = None
    produto_final: Optional[ProdutoFinalInfo] = None
    idempotency_key: Optional[str] = None


class FazerReceitaResponse(BaseModel):
    produto_mov_id: int
    consumos_reg: int
    produto_preco_id: int


class PrecoMateriaPrimaResponse(BaseModel):
    nome: str
    preco_custo: Decimal
    estoque_unidade: Decimal
    estoque_medida: Decimal


class PrecoMateriaPrimaUnitarioResponse(BaseModel):
    id: int
    materia_prima_id: int
    data_referencia: date
    preco_custo: Decimal
    data_fim: Optional[date] = None


class ReceitaMovimentacaoFiltro(BaseModel):
    receita_id: Optional[int] = None
    produto_id: Optional[int] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None


class ReceitaMovimentacaoResponse(BaseModel):
    id: int
    receita_id: int
    receita_nome: str
    produto_id: int
    produto_nome: str
    data_execucao: datetime
    quantidade_materia_prima: Decimal
    custo_materia_prima: Decimal
    quantidade_itens_producao: int
    custo_itens_producao: Decimal
    produto_estoque_id: Optional[int] = None
    quantidade_produto: int
    is_meia_receita: bool
    custo_total_producao: Decimal
    custo_unitario_produto: Decimal
