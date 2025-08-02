from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from src.modules.vendas.dto.dto import VendaCreate, VendaResponse, ItemVendaResponse
from src.modules.vendas.usecase.vendas_usecase import RegistrarVendaUseCase, ListarVendasUseCase, ListarItensVendaUseCase
from src.modules.vendas.vendas_dependencies import (
    get_registrar_venda_usecase,
    get_listar_vendas_usecase,
    get_listar_itens_venda_usecase,
)

router = APIRouter(prefix="/vendas", tags=["Vendas"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=int)
def registrar_venda(
    data: VendaCreate,
    usecase: RegistrarVendaUseCase = Depends(get_registrar_venda_usecase),
) -> int:
    return usecase.executar(data)


@router.get("/", response_model=List[VendaResponse])
def listar_vendas(
    usecase: ListarVendasUseCase = Depends(get_listar_vendas_usecase),
) -> List[VendaResponse]:
    return usecase.executar()


@router.get("/{venda_id}/itens", response_model=List[ItemVendaResponse])
def listar_itens_venda(
    venda_id: int,
    usecase: ListarItensVendaUseCase = Depends(get_listar_itens_venda_usecase),
) -> List[ItemVendaResponse]:
    itens = usecase.executar(venda_id)
    if not itens:
        raise HTTPException(status_code=404, detail="Itens não encontrados para essa venda.")
    return itens
