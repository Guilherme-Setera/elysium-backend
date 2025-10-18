from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from src.modules.receitas.abc_classes.receitas_abc import IReceitasRepository
from src.modules.receitas.dto.dto_receitas import (
    ReceitaCreate,
    ReceitaResponse,
    FazerReceitaInput,
    FazerReceitaResponse,
    ReceitaMovimentacaoResponse,
)

class EstoqueInsuficienteError(Exception):
    def __init__(self, faltas: List[dict]):
        self.faltas = faltas
        nomes = ", ".join(
            f"{f['nome']} (estoque {f['estoque_atual']}, precisa {f['consumo_necessario']})"
            for f in faltas
        )
        super().__init__(f"Estoque insuficiente: {nomes}")

class ReceitasUseCase:
    def __init__(self, repo: IReceitasRepository) -> None:
        self.repo = repo

    def inserir_receita(self, data: ReceitaCreate) -> int:
        if not data.nome or not str(data.nome).strip():
            raise ValueError("Nome é obrigatório.")
        if data.produto_id is None or int(data.produto_id) <= 0:
            raise ValueError("produto_id é obrigatório e deve ser > 0.")
        return self.repo.inserir_receita(data)

    def fazer_receita(self, data: FazerReceitaInput) -> FazerReceitaResponse:
        if data.quantidade is None or Decimal(str(data.quantidade)) <= 0:
            raise ValueError("Quantidade deve ser maior que zero.")
        return self.repo.fazer_receita(data)

    def listar_receitas(
        self,
        receita_id: Optional[int] = None,
        apenas_ativas: Optional[bool] = None,
        produto_id: Optional[int] = None,
    ) -> List[ReceitaResponse]:
        return self.repo.listar_receitas(
            receita_id=receita_id,
            apenas_ativas=apenas_ativas,
            produto_id=produto_id,
        )

    def listar_receitas_com_precos(
        self,
        receita_id: Optional[int] = None,
        produto_id: Optional[int] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
    ) -> List[ReceitaMovimentacaoResponse]:
        if receita_id is not None and int(receita_id) <= 0:
            raise ValueError("receita_id deve ser > 0.")
        if produto_id is not None and int(produto_id) <= 0:
            raise ValueError("produto_id deve ser > 0.")
        if data_inicio and data_fim and data_inicio > data_fim:
            raise ValueError("data_inicio não pode ser maior que data_fim.")
        return self.repo.listar_receitas_com_precos(
            receita_id=receita_id,
            produto_id=produto_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )
