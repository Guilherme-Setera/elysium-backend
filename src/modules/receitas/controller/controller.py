from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.modules.receitas.usecase.receitas_usecase import ReceitasUseCase, EstoqueInsuficienteError
from src.modules.receitas.receitas_dependencies import get_receitas_usecase
from src.modules.receitas.dto.dto_receitas import (
    ReceitaCreate,
    ReceitaResponse,
    FazerReceitaInput,
    FazerReceitaResponse,
    ReceitaMovimentacaoResponse,
    FazerReceitaBody,
)

router = APIRouter(prefix="/receitas", tags=["Receitas"])

@router.post("/", response_model=int, status_code=status.HTTP_201_CREATED)
def criar_receita(
    data: ReceitaCreate,
    usecase: ReceitasUseCase = Depends(get_receitas_usecase),
) -> int:
    try:
        return usecase.inserir_receita(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post(
    "/{receita_id}/fazer",
    response_model=FazerReceitaResponse,
    status_code=status.HTTP_201_CREATED,
)
def fazer_receita(
    receita_id: int,
    data: FazerReceitaBody,
    usecase: ReceitasUseCase = Depends(get_receitas_usecase),
) -> FazerReceitaResponse:
    payload = FazerReceitaInput(
        receita_id=receita_id,
        quantidade=data.quantidade,
        data_mov=data.data_mov,
        is_meia_receita=data.is_meia_receita,
        preco_venda=data.preco_venda,
    )
    try:
        return usecase.fazer_receita(payload)
    except EstoqueInsuficienteError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Estoque insuficiente para itens de produção.", "faltas": getattr(e, "faltas", [])},
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[ReceitaResponse])
def listar_receitas(
    receita_id: Optional[int] = Query(None),
    produto_id: Optional[int] = Query(None),
    usecase: ReceitasUseCase = Depends(get_receitas_usecase),
) -> List[ReceitaResponse]:
    return usecase.listar_receitas(
        receita_id=receita_id,
        produto_id=produto_id,
    )

@router.get("/com-precos", response_model=List[ReceitaMovimentacaoResponse])
def listar_receitas_com_precos(
    receita_id: Optional[int] = Query(None),
    produto_id: Optional[int] = Query(None),
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    usecase: ReceitasUseCase = Depends(get_receitas_usecase),
) -> List[ReceitaMovimentacaoResponse]:
    return usecase.listar_receitas_com_precos(
        receita_id=receita_id,
        produto_id=produto_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

@router.get("/{receita_id}", response_model=ReceitaResponse)
def obter_receita_por_id(
    receita_id: int,
    usecase: ReceitasUseCase = Depends(get_receitas_usecase),
) -> ReceitaResponse:
    itens = usecase.listar_receitas(receita_id=receita_id)
    if not itens:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receita não encontrada")
    return itens[0]
