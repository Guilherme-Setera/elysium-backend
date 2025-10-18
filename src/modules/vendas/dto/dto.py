from __future__ import annotations
from pydantic import BaseModel, Field, model_validator
from datetime import datetime, date
from typing import Optional, List


class ItemVendaCreate(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)
    preco_unitario: float = Field(gt=0)


class ItemVendaResponse(BaseModel):
    id: int
    venda_id: int
    produto_id: int
    nome_produto: str
    quantidade: int
    preco_unitario: float
    subtotal: float


class VendaCreate(BaseModel):
    cliente_id: Optional[int] = None
    forma_pagamento_id: Optional[int] = None
    data_venda: Optional[datetime] = None
    data_pagamento: Optional[datetime] = None
    observacao: Optional[str] = None
    itens: List[ItemVendaCreate]
    frete: Optional[float] = Field(default=0.0, ge=0)
    data_entrega: Optional[date] = None
    codigo_rastreio: Optional[str] = None
    valor_pago: Optional[float] = Field(default=0.0, ge=0)
    a_prazo: Optional[bool] = False

    @model_validator(mode="after")
    def _validar_itens(self) -> "VendaCreate":
        if not self.itens:
            raise ValueError("A venda deve conter ao menos um item.")
        return self


class VendaUpdate(BaseModel):
    id: int
    cliente_id: Optional[int] = None
    forma_pagamento_id: Optional[int] = None
    data_venda: Optional[datetime] = None
    data_pagamento: Optional[datetime] = None
    observacao: Optional[str] = None
    itens: Optional[List[ItemVendaCreate]] = None
    frete: Optional[float] = Field(default=None, ge=0)
    data_entrega: Optional[date] = None
    codigo_rastreio: Optional[str] = None
    valor_pago: Optional[float] = Field(default=None, ge=0)
    a_prazo: Optional[bool] = None


class ParcelaResumo(BaseModel):
    numero: int
    vencimento: date
    valor: float
    valor_pago: Optional[float] = None
    pago_em: Optional[date] = None


class VendaResponse(BaseModel):
    id: int
    cliente_id: Optional[int] = None
    nome_cliente: Optional[str] = None
    forma_pagamento_id: Optional[int] = None
    forma_pagamento: Optional[str] = None
    data_venda: datetime
    data_pagamento: Optional[datetime] = None
    total: float
    frete: Optional[float] = 0.0
    valor_pago: float
    observacao: Optional[str] = None
    pago: bool
    cancelada: bool
    status: str
    quitada_em: Optional[datetime] = None
    a_prazo: bool = False
    data_entrega: Optional[date] = None
    codigo_rastreio: Optional[str] = None
    datas_parcelas_pagas: Optional[List[date]] = None
    ultima_parcela_paga: Optional[date] = None
    qtd_parcelas: Optional[int] = None
    qtd_parcelas_pagas: Optional[int] = None
    parcelas: Optional[List[ParcelaResumo]] = None
    itens: Optional[List[ItemVendaResponse]] = None


class ConfirmacaoPagamento(BaseModel):
    venda_id: int


class RegistrarPagamentoDTO(BaseModel):
    venda_id: int
    valor_recebido: float = Field(gt=0)
    data_pagamento: Optional[datetime] = None
