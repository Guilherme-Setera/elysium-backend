from fastapi import Depends
from sqlalchemy.orm import Session

from src.infra.db.connection import get_db
from src.modules.vendas.abc_classes.vendas_abc import IVendaRepository
from src.modules.estoque.abc_classes.estoque_abc import IEstoqueRepository

from src.modules.vendas.repository.vendas_repository import VendaRepository
from src.modules.estoque.repository.estoque_repository import EstoqueRepository

from src.modules.vendas.usecase.vendas_usecase import RegistrarVendaUseCase, ListarVendasUseCase, ListarItensVendaUseCase


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
