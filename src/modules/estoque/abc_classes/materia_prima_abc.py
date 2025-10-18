# src/modules/materias_prima/abc_classes/materias_prima_abc.py
from abc import ABC, abstractmethod
from typing import Optional
from datetime import date

from src.modules.estoque.dto.dto_materia_prima import (
    MateriaPrimaCreate,
    MateriaPrimaResponse,
    MateriaPrimaUpdate,
    MateriaPrimaPrecoCreate,
    PrecoMateriaPrimaResponse,
    PrecoMateriaPrimaUnitarioResponse,
    EstoqueMateriaPrimaAtualResponse,
    MovimentacaoMateriaPrimaCreate,
)

class IMateriasPrimaRepository(ABC):

    @abstractmethod
    def cadastrar_materia_prima(self, materia: MateriaPrimaCreate) -> int:
        ...

    @abstractmethod
    def inativar_materia_prima(self, id: int) -> bool: ...

    @abstractmethod
    def listar_materias_prima(self) -> list[MateriaPrimaResponse]: ...

    @abstractmethod
    def atualizar_materia_prima(self, materia_prima_id: int, data: MateriaPrimaUpdate) -> int:
        ...
        
    @abstractmethod
    def registrar_movimentacao_materia_prima(
        self, 
        data: MovimentacaoMateriaPrimaCreate
    ) -> int:
        ...

    @abstractmethod
    def inserir_preco_materia_prima(self, data: MateriaPrimaPrecoCreate) -> int: ...

    @abstractmethod
    def encerrar_precos_materia_prima(self, id: int) -> None: ...

    @abstractmethod
    def buscar_preco_materia_prima(self, materia_prima_id: int, data_base: date) -> Optional[PrecoMateriaPrimaResponse]: ...

    @abstractmethod
    def listar_precos_materia_prima(self, materia_prima_id: int) -> list[PrecoMateriaPrimaUnitarioResponse]: ...

    @abstractmethod
    def listar_estoque_materia_prima_atual(self, data_referencia: date) -> list[EstoqueMateriaPrimaAtualResponse]: ...
