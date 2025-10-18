from typing import Callable
from datetime import date
from fastapi import Depends
from sqlalchemy.orm import Session

from src.infra.db.connection import get_db
from src.modules.itens_producao.abc_classes.abc_classes import IItensProducaoRepository
from src.modules.itens_producao.repository.itens_producao_repository import ItensProducaoRepository
from src.modules.itens_producao.dto.dto_itens_producao import (
    MovimentacaoItemProducaoEntradaCreate,
    EstoqueAtualItemProducaoResponse,)
from src.modules.itens_producao.usecase.itens_producao_usecase import (
    CadastrarItemConsumo,
    AtualizarItemConsumo,
    DesativarItemConsumo,
    ListarItensProducao,
    RegistrarEntradaItemProducao,
    ListarMovimentacoesItensProducao,
    MovimentacaoItemProducaoResponse,
    ListarEstoqueAtualItensProducao,
)


def get_repo(session: Session = Depends(get_db)) -> IItensProducaoRepository:
    return ItensProducaoRepository(session)


def get_uc_cadastrar(repo: IItensProducaoRepository = Depends(get_repo)) -> CadastrarItemConsumo:
    return CadastrarItemConsumo(repo)


def get_uc_atualizar(repo: IItensProducaoRepository = Depends(get_repo)) -> AtualizarItemConsumo:
    return AtualizarItemConsumo(repo)


def get_uc_desativar(repo: IItensProducaoRepository = Depends(get_repo)) -> DesativarItemConsumo:
    return DesativarItemConsumo(repo)


def get_uc_listar_itens(repo: IItensProducaoRepository = Depends(get_repo)) -> ListarItensProducao:
    return ListarItensProducao(repo)


def get_uc_registrar_mov(repo: IItensProducaoRepository = Depends(get_repo)) -> RegistrarEntradaItemProducao:
    return RegistrarEntradaItemProducao(repo)


def get_uc_listar_movs(repo: IItensProducaoRepository = Depends(get_repo)) -> ListarMovimentacoesItensProducao:
    return ListarMovimentacoesItensProducao(repo)


def get_registrar_entrada_item_producao(
    uc: RegistrarEntradaItemProducao = Depends(get_uc_registrar_mov),
) -> Callable[[MovimentacaoItemProducaoEntradaCreate], int]:
    return uc

def get_listar_movimentacoes_itens_producao(
    uc: ListarMovimentacoesItensProducao = Depends(get_uc_listar_movs),
) -> Callable[[date], list[MovimentacaoItemProducaoResponse]]:
    return uc

def get_uc_listar_estoque_atual_itens_producao(
    repo: IItensProducaoRepository = Depends(get_repo),
) -> ListarEstoqueAtualItensProducao:
    return ListarEstoqueAtualItensProducao(repo)

def get_listar_estoque_atual_itens_producao(
    uc: ListarEstoqueAtualItensProducao = Depends(get_uc_listar_estoque_atual_itens_producao),
) -> Callable[[date], list[EstoqueAtualItemProducaoResponse]]:
    return uc