# modules/vendas/repository/interfaces.py

from abc import ABC, abstractmethod
from datetime import datetime
from src.modules.vendas.dto.dto import VendaCreate, ItemVendaCreate
from typing import Sequence


class IVendaRepository(ABC):

    @abstractmethod
    def inserir_venda(self, venda: VendaCreate, total: float) -> int:
        ...

    @abstractmethod
    def inserir_item_venda(self, venda_id: int, item: ItemVendaCreate) -> None:
        ...

    @abstractmethod
    def buscar_vendas(self) -> Sequence[dict]:
        ...

    @abstractmethod
    def buscar_itens_por_venda_id(self, venda_id: int) -> Sequence[dict]:
        ...

    @abstractmethod
    def registrar_saida_por_venda(self, produto_id: int, quantidade: int, data_mov: datetime) -> int:
        ...