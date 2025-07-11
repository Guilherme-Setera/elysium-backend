from fastapi import APIRouter, Depends, Query, Path, Body
from typing import Optional
from datetime import date

from src.modules.vendas.dto.dto import (
    VendaCreate,
    VendaUpdate,
    VendaResponse,
    PainelResumoResponse,
    ResumoVendasPorData,
    RelatorioDetalhadoProduto,
    LogVendaResponse
)

from src.modules.vendas.vendas_dependencies import (
    get_registrar_venda_usecase,
    get_listar_vendas_usecase,
    get_buscar_venda_por_id_usecase,
    get_atualizar_venda_usecase,
    get_excluir_venda_usecase,
    get_painel_resumo_usecase,
    get_relatorio_resumo_usecase,
    get_relatorio_detalhado_produtos_usecase,
    get_registrar_log_alteracao_usecase,
    get_listar_logs_venda_usecase
)

router = APIRouter(prefix="/vendas", tags=["Vendas"])


@router.post("/", response_model=int)
async def registrar_venda(
    payload: VendaCreate = Body(...),
    usecase = Depends(get_registrar_venda_usecase)
):
    return await usecase.execute(payload)


@router.get("/", response_model=list[VendaResponse])
async def listar_vendas(
    cliente_id: Optional[int] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    forma_pagamento: Optional[str] = Query(None),
    usecase = Depends(get_listar_vendas_usecase)
):
    return await usecase.execute(cliente_id, data_inicio, data_fim, forma_pagamento)


@router.get("/{venda_id}", response_model=VendaResponse)
async def buscar_venda_por_id(
    venda_id: int = Path(...),
    usecase = Depends(get_buscar_venda_por_id_usecase)
):
    return await usecase.execute(venda_id)


@router.put("/{venda_id}")
async def atualizar_venda(
    venda_id: int = Path(...),
    payload: VendaUpdate = Body(...),
    usecase = Depends(get_atualizar_venda_usecase)
):
    await usecase.execute(venda_id, payload)
    return {"detail": "Venda atualizada com sucesso."}


@router.delete("/{venda_id}")
async def excluir_venda(
    venda_id: int = Path(...),
    usecase = Depends(get_excluir_venda_usecase)
):
    await usecase.execute(venda_id)
    return {"detail": "Venda excluída com sucesso."}

@router.get("/painel-resumo/", response_model=PainelResumoResponse)
async def painel_resumo(
    inicio: date = Query(...),
    fim: date = Query(...),
    usecase = Depends(get_painel_resumo_usecase)
):
    return await usecase.execute(inicio, fim)


@router.get("/relatorio-resumo/", response_model=list[ResumoVendasPorData])
async def relatorio_resumo(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    usecase = Depends(get_relatorio_resumo_usecase)
):
    return await usecase.execute(data_inicio, data_fim)


@router.get("/relatorio-produtos/", response_model=list[RelatorioDetalhadoProduto])
async def relatorio_detalhado_produtos(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    usecase = Depends(get_relatorio_detalhado_produtos_usecase)
):
    return await usecase.execute(data_inicio, data_fim)

@router.post("/{venda_id}/logs")
async def registrar_log_alteracao(
    venda_id: int = Path(...),
    campo: str = Body(...),
    valor_anterior: str = Body(...),
    valor_novo: str = Body(...),
    usuario: str = Body(...),
    usecase = Depends(get_registrar_log_alteracao_usecase)
):
    await usecase.execute(venda_id, campo, valor_anterior, valor_novo, usuario)
    return {"detail": "Log registrado com sucesso."}


@router.get("/logs/", response_model=list[LogVendaResponse])
async def listar_logs_venda(
    venda_id: Optional[int] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    usecase = Depends(get_listar_logs_venda_usecase)
):
    return await usecase.execute(venda_id, data_inicio, data_fim)
