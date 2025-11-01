from fastapi import Depends
from sqlalchemy.orm import Session

from src.infra.db.connection import get_db
from src.modules.vendas.abc_classes.vendas_abc import IVendaRepository
from src.modules.estoque.abc_classes.estoque_abc import IEstoqueRepository

from src.modules.vendas.repository.vendas_repository import VendaRepository
from src.modules.estoque.repository.estoque_repository import EstoqueRepository

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
    ListarHistoricoConsolidadoUseCase,
    )


def get_registrar_venda_usecase(session: Session = Depends(get_db)) -> RegistrarVendaUseCase:
    venda_repo: IVendaRepository = VendaRepository(session)
    estoque_repo: IEstoqueRepository = EstoqueRepository(session)
    return RegistrarVendaUseCase(venda_repo, estoque_repo)


def get_listar_vendas_usecase(session: Session = Depends(get_db)) -> ListarVendasUseCase:
    venda_repo: IVendaRepository = VendaRepository(session)
    return ListarVendasUseCase(venda_repo)


def get_listar_itens_venda_usecase(session: Session = Depends(get_db)) -> ListarItensVendaUseCase:
    venda_repo: IVendaRepository = VendaRepository(session)
    return ListarItensVendaUseCase(venda_repo)

def get_atualizar_venda_usecase(session: Session = Depends(get_db)) -> AtualizarVendaUseCase:
    venda_repo: IVendaRepository = VendaRepository(session)
    return AtualizarVendaUseCase(venda_repo)


def get_confirmar_pagamento_usecase(session: Session = Depends(get_db)) -> ConfirmarPagamentoVendaUseCase:
    venda_repo: IVendaRepository = VendaRepository(session)
    return ConfirmarPagamentoVendaUseCase(venda_repo)


def get_cancelar_venda_usecase(session: Session = Depends(get_db)) -> CancelarVendaUseCase:
    venda_repo: IVendaRepository = VendaRepository(session)
    return CancelarVendaUseCase(venda_repo)


def get_buscar_venda_com_itens_usecase(session: Session = Depends(get_db)) -> BuscarVendaComItensUseCase:
    venda_repo: IVendaRepository = VendaRepository(session)
    return BuscarVendaComItensUseCase(venda_repo)

def get_listar_vendas_nao_pagas_usecase(session: Session = Depends(get_db)) -> ListarVendasNaoPagasUseCase:
    venda_repo: IVendaRepository = VendaRepository(session)
    return ListarVendasNaoPagasUseCase(venda_repo)

def get_registrar_pagamento_venda_usecase(session: Session = Depends(get_db)) -> RegistrarPagamentoVendaUseCase:
    venda_repo: IVendaRepository = VendaRepository(session)
    return RegistrarPagamentoVendaUseCase(venda_repo)

def get_listar_historico_consolidado_usecase(session: Session = Depends(get_db)) -> ListarHistoricoConsolidadoUseCase:
    venda_repo: IVendaRepository = VendaRepository(session)
    return ListarHistoricoConsolidadoUseCase(venda_repo)