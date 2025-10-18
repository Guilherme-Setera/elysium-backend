from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Any
from datetime import date

from src.modules.itens_producao.dto.dto_itens_producao import (
    ItemConsumoCreate,
    ItemConsumoUpdate,
    MovimentacaoItemProducaoEntradaCreate,
    MovimentacaoItemProducaoResponse,
    EstoqueAtualItemProducaoResponse
)


class IItensProducaoRepository(ABC):

    @abstractmethod
    def cadastrar_item_consumo(self, data: ItemConsumoCreate) -> int:
        ...

    @abstractmethod
    def atualizar_item_consumo(self, item_consumo_id: int, data: ItemConsumoUpdate) -> int:
        ...

    @abstractmethod
    def desativar_item_consumo(self, item_consumo_id: int) -> int:
        ...
    
    @abstractmethod
    def listar_itens_producao(self, somente_ativos: bool | None = None) -> list[dict]: ...

    @abstractmethod
    def registrar_entrada_item_producao(self, data: MovimentacaoItemProducaoEntradaCreate) -> int: ...

    @abstractmethod
    def listar_movimentacoes_itens_producao(
        self,
        dia_limite: date,
    ) -> list[MovimentacaoItemProducaoResponse]:
        ...

    @abstractmethod
    def listar_estoque_atual_itens_producao(
        self,
        data_referencia: date,
    ) -> list[EstoqueAtualItemProducaoResponse]:
        ...    