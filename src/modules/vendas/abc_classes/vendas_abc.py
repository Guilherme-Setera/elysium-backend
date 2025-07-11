from abc import ABC, abstractmethod
from datetime import date
from typing import  Optional

from src.modules.vendas.dto.dto import (
    VendaCreate,
    VendaUpdate,
    VendaResponse,
    VendaDetalhadaResponse,
    ResumoVendasPorData,
    PainelResumoResponse,
    RelatorioDetalhadoProduto,
    LogVendaResponse,
    
)


class IVendasRepository(ABC):

    @abstractmethod
    async def listar_vendas(
        self,
        cliente_id: Optional[int],
        data_inicio: Optional[date],
        data_fim: Optional[date],
        forma_pagamento: Optional[str]
    ) -> list[VendaResponse]:
        pass

    @abstractmethod
    async def buscar_venda_por_id(self, venda_id: int) -> Optional[VendaResponse]:
        pass

    @abstractmethod
    async def registrar_venda(self, payload: VendaCreate) -> int:
        pass

    @abstractmethod
    async def atualizar_venda(self, venda_id: int, payload: VendaUpdate) -> None:
        pass
    
    @abstractmethod
    async def excluir_venda(self, venda_id: int) -> None:
        pass

    @abstractmethod
    async def gerar_relatorio_resumo(
        self, data_inicio: date, data_fim: date
    ) -> list[ResumoVendasPorData]:
        pass

    @abstractmethod
    async def gerar_relatorio_detalhado_produtos(
        self, data_inicio: date, data_fim: date
    ) -> list[RelatorioDetalhadoProduto]:
        pass

    @abstractmethod
    async def registrar_log_alteracao(
        self,
        venda_id: int,
        campo: str,
        valor_anterior: str,
        valor_novo: str,
        usuario: str
    ) -> None:
        pass

    @abstractmethod
    async def listar_logs_venda(
        self,
        venda_id: Optional[int],
        data_inicio: Optional[date],
        data_fim: Optional[date]
    ) -> list[LogVendaResponse]:
        pass

    @abstractmethod
    async def painel_resumo(
        self,
        inicio: date,
        fim: date
    ) -> PainelResumoResponse:
        pass
