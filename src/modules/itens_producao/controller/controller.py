from typing import Optional, Literal
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.modules.itens_producao.dto.dto_itens_producao import (
    ItemConsumoCreate,
    ItemConsumoUpdate,
    ItemConsumoResponse,
    MovimentacaoItemProducaoEntradaCreate,
    MovimentacaoItemProducaoResponse,
    EstoqueAtualItemProducaoResponse,
)

from src.modules.itens_producao.itens_producao_dependencies import (
    get_uc_cadastrar,
    get_uc_atualizar,
    get_uc_desativar,
    get_uc_listar_itens,
    get_uc_registrar_mov,
    get_uc_listar_movs,
    get_listar_estoque_atual_itens_producao,
)

from src.modules.itens_producao.usecase.itens_producao_usecase import (
    CadastrarItemConsumo,
    AtualizarItemConsumo,
    DesativarItemConsumo,
    ListarItensProducao,
    RegistrarEntradaItemProducao,
    ListarMovimentacoesItensProducao,
    ListarEstoqueAtualItensProducao,
)

router = APIRouter(prefix="/itens-producao", tags=["Itens de Produção"])


@router.post("/", response_model=int, status_code=status.HTTP_201_CREATED)
def criar_item_consumo(
    data: ItemConsumoCreate,
    uc: CadastrarItemConsumo = Depends(get_uc_cadastrar),
) -> int:
    try:
        novo_id = uc(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if novo_id < 0:
        raise HTTPException(status_code=500, detail="Falha ao cadastrar item")
    return novo_id


@router.put("/{item_id}", response_model=bool)
def atualizar_item_consumo(
    item_id: int,
    data: ItemConsumoUpdate,
    uc: AtualizarItemConsumo = Depends(get_uc_atualizar),
) -> Literal[True]:
    try:
        atualizado_id = uc(item_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if atualizado_id < 0:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return True


@router.delete("/{item_id}", response_model=bool)
def desativar_item_consumo(
    item_id: int,
    uc: DesativarItemConsumo = Depends(get_uc_desativar),
) -> Literal[True]:
    atualizado_id = uc(item_id)
    if atualizado_id < 0:
        raise HTTPException(status_code=404, detail="Item não encontrado ou já desativado")
    return True


@router.get("/", response_model=list[ItemConsumoResponse])
def listar_itens_producao(
    somente_ativos: Optional[bool] = Query(default=None),
    uc: ListarItensProducao = Depends(get_uc_listar_itens),
) -> list[ItemConsumoResponse]:
    return uc(somente_ativos)


@router.post("/movimentacoes", response_model=int, status_code=status.HTTP_201_CREATED)
def registrar_entrada_item_producao(
    data: MovimentacaoItemProducaoEntradaCreate,
    uc: RegistrarEntradaItemProducao = Depends(get_uc_registrar_mov),
) -> int:
    try:
        novo_id = uc(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if novo_id < 0:
        raise HTTPException(status_code=500, detail="Falha ao registrar entrada")
    return novo_id


@router.get("/movimentacoes", response_model=list[MovimentacaoItemProducaoResponse])
def listar_movimentacoes_itens_producao(
    dia: date = Query(..., description="Dia limite no formato YYYY-MM-DD"),
    uc: ListarMovimentacoesItensProducao = Depends(get_uc_listar_movs),
) -> list[MovimentacaoItemProducaoResponse]:
    return uc(dia)

@router.get(
    "/estoque-atual",
    response_model=list[EstoqueAtualItemProducaoResponse],
)
def listar_estoque_atual_itens_producao(
    data_referencia: date = Query(..., description="YYYY-MM-DD"),
    uc: ListarEstoqueAtualItensProducao = Depends(get_listar_estoque_atual_itens_producao),
) -> list[EstoqueAtualItemProducaoResponse]:
    return uc(data_referencia)