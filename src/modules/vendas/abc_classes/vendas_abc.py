from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List

from src.modules.vendas.dto.dto import (
    VendaCreate,
    VendaUpdate,
    ItemVendaCreate,
    ItemVendaResponse,
    VendaResponse,
    RegistrarPagamentoDTO,
    VendaHistoricoConsolidadoFiltro,
    VendaHistoricoConsolidadoItem,
)

class IVendaRepository(ABC):
    @abstractmethod
    def inserir_venda(self, venda: VendaCreate, total: float) -> int:
        ...

    @abstractmethod
    def inserir_item_venda(self, venda_id: int, item: ItemVendaCreate) -> int:
        ...

    @abstractmethod
    def buscar_vendas(self) -> List[VendaResponse]:
        ...

    @abstractmethod
    def buscar_itens_por_venda_id(self, venda_id: int) -> List[ItemVendaResponse]:
        ...

    @abstractmethod
    def registrar_saida_por_venda(self, produto_id: int, quantidade: int, data_mov: datetime, venda_id: int) -> int:
        ...

    @abstractmethod
    def registrar_entrada_por_devolucao(
        self,
        produto_id: int,
        quantidade: int,
        data_mov: datetime,
        venda_id: Optional[int] = None,
    ) -> Optional[int]:
        ...

    @abstractmethod
    def atualizar_venda(self, venda_id: int, venda: VendaUpdate, total: float) -> None:
        ...

    @abstractmethod
    def confirmar_pagamento(self, venda_id: int) -> None:
        ...

    @abstractmethod
    def cancelar_venda(self, venda_id: int, itens: List[ItemVendaResponse]) -> None:
        ...

    @abstractmethod
    def buscar_venda_por_id(self, venda_id: int) -> Optional[VendaResponse]:
        ...

    @abstractmethod
    def deletar_itens_da_venda(self, venda_id: int) -> None:
        ...

    @abstractmethod
    def deletar_movimentacoes_por_venda(self, venda_id: int) -> None:
        ...

    @abstractmethod
    def listar_vendas_nao_pagas(self) -> List[VendaResponse]:
        ...

    @abstractmethod
    def registrar_pagamento_venda(self, data: RegistrarPagamentoDTO) -> bool:
        ...

    @abstractmethod
    def desabilitar_triggers_recalculo(self) -> None:
        ...

    @abstractmethod
    def habilitar_triggers_recalculo(self) -> None:
        ...

    @abstractmethod
    def listar_historico_consolidado(
        self, filtro: VendaHistoricoConsolidadoFiltro
    ) -> List[VendaHistoricoConsolidadoItem]:
        ...
