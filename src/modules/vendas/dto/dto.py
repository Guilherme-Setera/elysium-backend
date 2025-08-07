from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ItemVendaCreate(BaseModel):
    produto_id: int
    quantidade: int
    preco_unitario: float


class ItemVendaResponse(BaseModel):
    id: int
    venda_id: int
    produto_id: int
    nome_produto: str
    quantidade: int
    preco_unitario: float
    subtotal: float


class VendaCreate(BaseModel):
    cliente_id: Optional[int]
    forma_pagamento_id: int
    data_venda: Optional[datetime] = None
    data_pagamento: Optional[datetime] = None
    observacao: Optional[str] = None
    itens: List[ItemVendaCreate]


class VendaUpdate(BaseModel):
    id: int  # identificação da venda a ser atualizada
    cliente_id: Optional[int]
    forma_pagamento_id: int
    data_venda: Optional[datetime] = None
    data_pagamento: Optional[datetime] = None
    observacao: Optional[str] = None
    itens: List[ItemVendaCreate]


class VendaResponse(BaseModel):
    id: int
    cliente_id: Optional[int]
    nome_cliente: Optional[str]
    forma_pagamento_id: int
    forma_pagamento: str
    data_venda: datetime
    data_pagamento: Optional[datetime]
    total: float
    observacao: Optional[str]
    pago: bool
    cancelada: bool


class ConfirmacaoPagamento(BaseModel):
    venda_id: int
