from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.connection import get_db
from src.modules.vendas.repository.vendas_repository import VendasRepository
from src.modules.vendas.usecase.vendas_usecase import (
    RegistrarVendaUseCase,
    ListarVendasUseCase,
    BuscarVendaPorIdUseCase,
    AtualizarVendaUseCase,
    ExcluirVendaUseCase,
    GerarPainelResumoUseCase,
    GerarRelatorioResumoUseCase,
    GerarRelatorioDetalhadoProdutosUseCase,
    RegistrarLogAlteracaoUseCase,
    ListarLogsVendaUseCase
)


def get_vendas_repository(
    session: AsyncSession = Depends(get_db),
) -> VendasRepository:
    return VendasRepository(session)


def get_registrar_venda_usecase(
    repo: VendasRepository = Depends(get_vendas_repository)
) -> RegistrarVendaUseCase:
    return RegistrarVendaUseCase(repo)


def get_listar_vendas_usecase(
    repo: VendasRepository = Depends(get_vendas_repository)
) -> ListarVendasUseCase:
    return ListarVendasUseCase(repo)


def get_buscar_venda_por_id_usecase(
    repo: VendasRepository = Depends(get_vendas_repository)
) -> BuscarVendaPorIdUseCase:
    return BuscarVendaPorIdUseCase(repo)


def get_atualizar_venda_usecase(
    repo: VendasRepository = Depends(get_vendas_repository)
) -> AtualizarVendaUseCase:
    return AtualizarVendaUseCase(repo)


def get_excluir_venda_usecase(
    repo: VendasRepository = Depends(get_vendas_repository)
) -> ExcluirVendaUseCase:
    return ExcluirVendaUseCase(repo)


def get_painel_resumo_usecase(
    repo: VendasRepository = Depends(get_vendas_repository)
) -> GerarPainelResumoUseCase:
    return GerarPainelResumoUseCase(repo)


def get_relatorio_resumo_usecase(
    repo: VendasRepository = Depends(get_vendas_repository)
) -> GerarRelatorioResumoUseCase:
    return GerarRelatorioResumoUseCase(repo)


def get_relatorio_detalhado_produtos_usecase(
    repo: VendasRepository = Depends(get_vendas_repository)
) -> GerarRelatorioDetalhadoProdutosUseCase:
    return GerarRelatorioDetalhadoProdutosUseCase(repo)


def get_registrar_log_alteracao_usecase(
    repo: VendasRepository = Depends(get_vendas_repository)
) -> RegistrarLogAlteracaoUseCase:
    return RegistrarLogAlteracaoUseCase(repo)


def get_listar_logs_venda_usecase(
    repo: VendasRepository = Depends(get_vendas_repository)
) -> ListarLogsVendaUseCase:
    return ListarLogsVendaUseCase(repo)
