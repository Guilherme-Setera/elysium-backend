# src/modules/estoque/usecases.py
from __future__ import annotations

from datetime import date
from typing import Optional, List

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

from src.modules.receitas.dto.dto_receitas import (
    ReceitaCreate,
    FazerReceitaInput,
    FazerReceitaResponse,
    ReceitaResponse,
)

from src.modules.estoque.abc_classes.materia_prima_abc import IMateriasPrimaRepository


class MateriasPrimaUseCase:
    def __init__(self, repo: IMateriasPrimaRepository) -> None:
        self.repo: IMateriasPrimaRepository = repo

    def cadastrar_materia_prima(self, data: MateriaPrimaCreate) -> int:
        return self.repo.cadastrar_materia_prima(data)

    def inativar_materia_prima(self, id: int) -> bool:
        return self.repo.inativar_materia_prima(id)

    def listar_materia_prima(self) -> List[MateriaPrimaResponse]:
        return self.repo.listar_materias_prima()

    def atualizar_materia_prima(self, id: int, data: MateriaPrimaUpdate) -> bool:
        """
        Atualiza e retorna True/False para manter compat com quem já esperava bool.
        O repo retorna o id atualizado (>0) ou -1.
        """
        updated_id = self.repo.atualizar_materia_prima(id, data)
        return updated_id > 0

    def registrar_movimentacao_materia_prima(
        self, 
        data: MovimentacaoMateriaPrimaCreate
    ) -> int:
        return self.repo.registrar_movimentacao_materia_prima(data)

    def inserir_preco_materia_prima(self, data: MateriaPrimaPrecoCreate) -> int:
        return self.repo.inserir_preco_materia_prima(data)

    def encerrar_precos_materia_prima(self, id: int) -> None:
        return self.repo.encerrar_precos_materia_prima(id)

    def buscar_preco_materia_prima(
        self, materia_prima_id: int, data_base: date
    ) -> Optional[PrecoMateriaPrimaResponse]:
        return self.repo.buscar_preco_materia_prima(materia_prima_id, data_base)

    def listar_precos_materia_prima(self, materia_prima_id: int) -> List[PrecoMateriaPrimaUnitarioResponse]:
        return self.repo.listar_precos_materia_prima(materia_prima_id)

    def listar_estoque_materia_prima_atual(self, data_referencia: date) -> List[EstoqueMateriaPrimaAtualResponse]:
        return self.repo.listar_estoque_materia_prima_atual(data_referencia)

