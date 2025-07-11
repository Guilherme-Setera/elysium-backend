from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

class ItemVendaCreate(BaseModel):
    produto_id: int
    quantidade: int
    preco_unitario: Decimal

class VendaCreate(BaseModel):
    cliente_id: int | None= None
    forma_pagamento: str
    itens: list[ItemVendaCreate]

class ItemVendaResponse(BaseModel):
    id: int
    produto_id: int
    nome_produto: str
    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal

class VendaResponse(BaseModel):
    id: int
    cliente_id: int | None= None
    cliente_nome: str | None = None
    data_venda: datetime
    total: Decimal
    forma_pagamento: str
    itens: list[ItemVendaResponse]

class ResumoVendasPorData(BaseModel):
    data: date
    total_vendas: int
    valor_total: Decimal

class PainelResumoResponse(BaseModel):
    total_diario: Decimal
    total_mensal: Decimal
    quantidade_vendas: int

class VendaUpdate(BaseModel):
    forma_pagamento: str | None= None
    cliente_id: int | None= None

class LogVendaResponse(BaseModel):
    id: int
    venda_id: int
    campo_alterado: str
    valor_anterior: str
    valor_novo: str
    data_alteracao: datetime

class VendaDetalhadaResponse(BaseModel):
    id: int
    cliente_id: int | None = None
    data_venda: datetime
    total: Decimal
    forma_pagamento: str
    itens: list[ItemVendaResponse]    

class RelatorioDetalhadoProduto(BaseModel):
    produto_id: int
    nome_produto: str
    total_vendido: int
    total_faturado: Decimal    

class VendaListagemResponse(BaseModel):
    id: int
    data_venda: datetime
    total: Decimal
    forma_pagamento: str
    cliente_nome: str | None = None
