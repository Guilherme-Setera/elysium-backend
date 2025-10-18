from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from src.modules.vendas.dto.dto import (
    VendaCreate,
    VendaUpdate,
    VendaResponse,
    ItemVendaResponse,
    RegistrarPagamentoDTO,
)
from src.modules.vendas.usecase.vendas_usecase import (
    RegistrarVendaUseCase,
    ListarVendasUseCase,
    ListarItensVendaUseCase,
    AtualizarVendaUseCase,
    ConfirmarPagamentoVendaUseCase,
    CancelarVendaUseCase,
    BuscarVendaComItensUseCase,
    ListarVendasNaoPagasUseCase,
    RegistrarPagamentoVendaUseCase,
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
    get_registrar_pagamento_venda_usecase,
)

router = APIRouter(prefix="/vendas", tags=["Vendas"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=VendaResponse)
def registrar_venda(
    data: VendaCreate,
    usecase: RegistrarVendaUseCase = Depends(get_registrar_venda_usecase),
) -> VendaResponse:
    venda_id = usecase.executar(data)
    venda = usecase.venda_repo.buscar_venda_por_id(venda_id)
    if not venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada após inserção.")
    return venda


@router.get("/", response_model=List[VendaResponse])
def listar_vendas(
    usecase: ListarVendasUseCase = Depends(get_listar_vendas_usecase),
) -> List[VendaResponse]:
    return usecase.executar()


@router.get("/pendentes-pagamento", response_model=List[VendaResponse])
def listar_vendas_pendentes_pagamento(
    usecase: ListarVendasNaoPagasUseCase = Depends(get_listar_vendas_nao_pagas_usecase),
) -> List[VendaResponse]:
    return usecase.executar()


@router.post("/{venda_id}/registrar-pagamento")
def registrar_pagamento(
    venda_id: int,
    data: RegistrarPagamentoDTO,
    usecase: RegistrarPagamentoVendaUseCase = Depends(get_registrar_pagamento_venda_usecase),
):
    if venda_id != data.venda_id:
        raise HTTPException(status_code=400, detail="ID da venda no corpo e na URL não coincidem.")
    ok = usecase.executar(data)
    if not ok:
        raise HTTPException(status_code=404, detail="Venda não encontrada.")
    return {"message": "Pagamento registrado com sucesso."}


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
