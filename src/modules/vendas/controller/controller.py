from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from src.modules.vendas.dto.dto import (
    VendaCreate,
    VendaUpdate,
    VendaResponse,
    ItemVendaResponse,
)
from src.modules.vendas.usecase.vendas_usecase import (
    RegistrarVendaUseCase,
    ListarVendasUseCase,
    ListarItensVendaUseCase,
    AtualizarVendaUseCase,
    ConfirmarPagamentoVendaUseCase,
    CancelarVendaUseCase,
    BuscarVendaComItensUseCase,
    ListarVendasNaoPagasUseCase
)
from src.modules.vendas.vendas_dependencies import (
    get_registrar_venda_usecase,
    get_listar_vendas_usecase,
    get_listar_itens_venda_usecase,
    get_atualizar_venda_usecase,
    get_confirmar_pagamento_usecase,
    get_cancelar_venda_usecase,
    get_buscar_venda_com_itens_usecase,
    get_listar_vendas_nao_pagas_usecase,
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


@router.put("/{venda_id}")
def atualizar_venda(
    venda_id: int,
    data: VendaUpdate,
    usecase: AtualizarVendaUseCase = Depends(get_atualizar_venda_usecase),
):
    usecase.executar(venda_id, data)
    return {"message": "Venda atualizada com sucesso."}


@router.post("/{venda_id}/confirmar-pagamento")
def confirmar_pagamento(
    venda_id: int,
    usecase: ConfirmarPagamentoVendaUseCase = Depends(get_confirmar_pagamento_usecase),
):
    usecase.executar(venda_id)
    return {"message": "Pagamento confirmado."}


@router.post("/{venda_id}/cancelar")
def cancelar_venda(
    venda_id: int,
    usecase: CancelarVendaUseCase = Depends(get_cancelar_venda_usecase),
):
    usecase.executar(venda_id)
    return {"message": "Venda cancelada com sucesso."}


@router.get("/{venda_id}", response_model=dict)
def buscar_venda_com_itens(
    venda_id: int,
    usecase: BuscarVendaComItensUseCase = Depends(get_buscar_venda_com_itens_usecase),
):
    result = usecase.executar(venda_id)
    if not result:
        raise HTTPException(status_code=404, detail="Venda não encontrada.")
    return result

@router.get("/pendentes-pagamento", response_model=list[VendaResponse])
def listar_vendas_pendentes_pagamento(
    usecase: ListarVendasNaoPagasUseCase = Depends(get_listar_vendas_nao_pagas_usecase),
):
    return usecase.executar()