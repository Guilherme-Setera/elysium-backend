from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from src.modules.receitas.dto.dto_receitas import (
    ReceitaCreate,
    ReceitaResponse,
    FazerReceitaInput,
    FazerReceitaResponse,
    ReceitaMovimentacaoResponse,
)


class IReceitasRepository(ABC):
    @abstractmethod
    def inserir_receita(self, data: ReceitaCreate) -> int:
        raise NotImplementedError

    @abstractmethod
    def fazer_receita(self, data: FazerReceitaInput) -> FazerReceitaResponse:
        raise NotImplementedError

    @abstractmethod
    def listar_receitas(
        self,
        receita_id: Optional[int] = None,
        apenas_ativas: Optional[bool] = None,
        produto_id: Optional[int] = None,
    ) -> List[ReceitaResponse]:
        raise NotImplementedError

    @abstractmethod
    def listar_receitas_com_precos(
        self,
        receita_id: Optional[int] = None,
        produto_id: Optional[int] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
    ) -> List[ReceitaMovimentacaoResponse]:
        raise NotImplementedError
