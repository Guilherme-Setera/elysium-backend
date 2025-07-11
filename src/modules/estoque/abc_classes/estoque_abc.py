from abc import ABC, abstractmethod
from typing import List
from src.modules.estoque.dto.dto import (
    MovimentacaoCreate,
    EstoqueAtualResponse,
    EstoqueBaixoResponse,
    OperacaoResponse
)


class IEstoqueRepository(ABC):
    @abstractmethod
    def registrar_entrada(self, data: MovimentacaoCreate) -> int:
        ...

    @abstractmethod
    def listar_estoque_atual(self) -> List[EstoqueAtualResponse]:
        ...

    @abstractmethod
    def listar_estoque_baixo(self) -> List[EstoqueBaixoResponse]:
        ...

    @abstractmethod
    def listar_operacoes(self) -> List[OperacaoResponse]:
        ...
