from fastapi import Depends
from sqlalchemy.orm import Session

from src.infra.db.connection import get_db

from src.modules.estoque.repository.estoque_repository import EstoqueRepository
from src.modules.estoque.usecase.estoque_usecase import EstoqueUseCase
from src.modules.estoque.abc_classes.estoque_abc import IEstoqueRepository

from src.modules.estoque.repository.materia_prima_repository import MateriaPrimaRepository
from src.modules.estoque.usecase.materias_prima_usecase import MateriasPrimaUseCase
from src.modules.estoque.abc_classes.materia_prima_abc import IMateriasPrimaRepository


def get_estoque_usecase(session: Session = Depends(get_db)) -> EstoqueUseCase:
    repo: IEstoqueRepository = EstoqueRepository(session)
    return EstoqueUseCase(repo)


def get_materias_prima_usecase(session: Session = Depends(get_db)) -> MateriasPrimaUseCase:
    repo: IMateriasPrimaRepository = MateriaPrimaRepository(session)
    return MateriasPrimaUseCase(repo)
