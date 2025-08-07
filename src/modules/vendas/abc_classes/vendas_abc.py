from abc import ABC, abstractmethod
from datetime import datetime
from typing import Sequence, Optional

from src.modules.vendas.dto.dto import (
    VendaCreate,
    ItemVendaCreate,
    ItemVendaResponse, 
    VendaResponse
)


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
    def registrar_entrada_por_devolucao(self, produto_id: int, quantidade: int, data_mov: datetime) -> int:
        ...

    @abstractmethod
    def atualizar_venda(self, venda_id: int, venda: VendaCreate, total: float) -> None:
        ...

    @abstractmethod
    def confirmar_pagamento(self, venda_id: int) -> None:
        ...

    @abstractmethod
    def cancelar_venda(self, venda_id: int, itens: list[ItemVendaResponse]) -> None:
        ...

    @abstractmethod
    def buscar_venda_por_id(self, venda_id: int) -> Optional[VendaResponse]:
        ...

    @abstractmethod
    def deletar_itens_da_venda(self, venda_id: int) -> None:
        ...


    @abstractmethod
    def listar_vendas_nao_pagas(self) -> list[VendaResponse]:
       ...      