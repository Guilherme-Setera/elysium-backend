from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal
from decimal import Decimal
from datetime import date, datetime

class MateriaPrimaCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    ativo: Optional[bool] = True
    estoque_minimo_unidade: Optional[float] = None
    medida_base: Optional[float] = Field(default=1, gt=0)
    is_grama: Optional[bool] = None
    is_ml: Optional[bool] = None
    unidade: Optional[str] = Field(default=None, pattern="^(g|ml)$")

    densidade: Optional[float] = Field(
        default=None,
        gt=0,
        description="Densidade em g/ml; obrigatória quando unidade='ml'"
    )

    @model_validator(mode="after")
    def _validar_densidade_para_ml(self):
        eh_ml = (self.unidade == "ml") or (self.is_ml is True) or (self.is_grama is False)
        eh_g = (self.unidade == "g") or (self.is_grama is True) or (self.is_ml is False)

        if eh_ml and self.densidade is None:
            raise ValueError("densidade é obrigatória para matérias-primas com unidade 'ml'.")
        if eh_g and self.densidade is not None:
            pass

        return self

class MateriaPrimaResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    ativo: bool
    estoque_minimo: Optional[Decimal] = None
    medida_base: Decimal
    unidade_base: Literal["g", "ml"]
    densidade: Optional[Decimal] = Field(default=None, description="Densidade em g/ml (apenas para matérias-primas em ml)")

class MateriaPrimaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None
    estoque_minimo_unidade: Optional[int] = None
    medida_base: Optional[float] = None
    unidade: Optional[Literal['g', 'ml']] = None
    is_grama: Optional[bool] = None
    is_ml: Optional[bool] = None

class MateriaPrimaPrecoCreate(BaseModel):
    materia_prima_id: int
    data_referencia: date
    preco_custo: float
    data_fim: Optional[date] = None

class MateriaPrimaPrecoResponse(BaseModel):
    id: int
    materia_prima_id: int
    data_referencia: date
    preco_custo: float
    data_fim: Optional[date] = None

class MateriaPrimaPrecoUpdate(BaseModel):
    data_referencia: Optional[date] = None
    preco_custo: Optional[float] = None
    data_fim: Optional[date] = None

class PrecoMateriaPrimaResponse(BaseModel):
    nome: str
    preco_custo: Decimal
    estoque_unidade: Decimal
    estoque_medida: Decimal

class PrecoMateriaPrimaUnitarioResponse(BaseModel):
    id: int
    materia_prima_id: int
    data_referencia: date
    preco_custo: float
    data_fim: Optional[date] = None

class EstoqueMateriaPrimaAtualResponse(BaseModel):
    materia_prima_id: int
    nome_materia_prima: str
    saldo_estoque: float
    preco_custo: Optional[float] = None
    data_movimentacao: Optional[datetime] = None
    unidade_base: Literal['g', 'ml']
    medida_base: float
    lote: Optional[int] = None

class MovimentacaoMateriaPrimaCreate(BaseModel):
    materia_prima_id: int
    quantidade: Decimal = Decimal("0")
    operacao_id: int
    data_referencia: Optional[date] = None
    preco_custo: Optional[Decimal] = None

