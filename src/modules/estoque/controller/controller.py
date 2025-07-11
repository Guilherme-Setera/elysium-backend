from fastapi import APIRouter, Depends, HTTPException, status
from src.modules.estoque.dto.dto import (
    MovimentacaoCreate,
    EstoqueAtualResponse,
    EstoqueBaixoResponse,
    OperacaoResponse
)
from src.modules.estoque.usecase.estoque_usecase import EstoqueUseCase
from src.modules.estoque.estoque_dependencies import get_estoque_usecase

router = APIRouter(prefix="/estoque", tags=["Estoque"])


@router.post("/entrada", status_code=status.HTTP_201_CREATED)
def registrar_entrada_estoque(
    data: MovimentacaoCreate, usecase: EstoqueUseCase = Depends(get_estoque_usecase)
):
    sucesso = usecase.registrar_entrada(data)
    if not sucesso:
        raise HTTPException(status_code=400, detail="Falha ao registrar entrada")
    return {"detail": "Entrada registrada com sucesso"}


@router.post("/saida", status_code=status.HTTP_201_CREATED)
def registrar_saida_estoque(
    data: MovimentacaoCreate, usecase: EstoqueUseCase = Depends(get_estoque_usecase)
):
    sucesso = usecase.registrar_entrada(data)
    if not sucesso:
        raise HTTPException(status_code=400, detail="Falha ao registrar saída")
    return {"detail": "Saída registrada com sucesso"}


@router.get("/saldo", response_model=list[EstoqueAtualResponse])
def obter_estoque_atual(
    usecase: EstoqueUseCase = Depends(get_estoque_usecase)
) -> list[EstoqueAtualResponse]:
    return usecase.listar_estoque_atual()


@router.get("/baixo", response_model=list[EstoqueBaixoResponse])
def obter_estoque_baixo(
    usecase: EstoqueUseCase = Depends(get_estoque_usecase)
) -> list[EstoqueBaixoResponse]:
    return usecase.listar_estoque_baixo()

@router.get("/operacoes", response_model=list[OperacaoResponse])
def listar_operacoes(
    usecase: EstoqueUseCase = Depends(get_estoque_usecase)
) -> list[OperacaoResponse]:
    return usecase.listar_operacoes()