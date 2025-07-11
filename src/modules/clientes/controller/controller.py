from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, status

from src.modules.clientes.dto.dto import ClienteCreate, ClienteUpdate, ClienteResponse
from src.modules.clientes.usecase.clientes_usecase import ClientesUseCase
from src.modules.clientes.clientes_dependencies import get_clientes_usecase

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("/", response_model=int, status_code=status.HTTP_201_CREATED)
def criar_cliente(
    data: ClienteCreate,
    usecase: ClientesUseCase = Depends(get_clientes_usecase)
) -> int:
    return usecase.criar_cliente(data)


@router.post("/batch", response_model=list[int], status_code=status.HTTP_201_CREATED)
def criar_clientes_em_lote(
    data: list[ClienteCreate],
    usecase: ClientesUseCase = Depends(get_clientes_usecase)
) -> list[int]:
    return usecase.criar_clientes_em_lote(data)


@router.put("/{cliente_id}", response_model=bool)
def atualizar_cliente(
    cliente_id: int,
    data: ClienteUpdate,
    usecase: ClientesUseCase = Depends(get_clientes_usecase)
) -> Literal[True]:
    atualizado = usecase.atualizar_cliente(cliente_id, data)
    if not atualizado:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return True


@router.delete("/{cliente_id}", response_model=bool)
def desativar_cliente(
    cliente_id: int,
    usecase: ClientesUseCase = Depends(get_clientes_usecase)
) -> Literal[True]:
    desativado = usecase.desativar_cliente(cliente_id)
    if not desativado:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return True


@router.get("/", response_model=list[ClienteResponse])
def listar_clientes(
    usecase: ClientesUseCase = Depends(get_clientes_usecase)
) -> list[ClienteResponse]:
    return usecase.listar_clientes()
