from fastapi import Depends
from sqlalchemy.orm import Session

from src.infra.db.connection import get_db
from src.modules.estoque.repository.estoque_repository import EstoqueRepository
from src.modules.estoque.usecase.estoque_usecase import EstoqueUseCase
from src.modules.estoque.abc_classes.estoque_abc import IEstoqueRepository


def get_estoque_usecase(session: Session = Depends(get_db)) -> EstoqueUseCase:
    repo: IEstoqueRepository = EstoqueRepository(session)
    return EstoqueUseCase(repo)
