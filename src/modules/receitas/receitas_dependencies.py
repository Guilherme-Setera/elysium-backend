from fastapi import Depends
from sqlalchemy.orm import Session

from src.infra.db.connection import get_db

from src.modules.receitas.abc_classes.receitas_abc import IReceitasRepository
from src.modules.receitas.repository.receitas_repository import ReceitasRepository
from src.modules.receitas.usecase.receitas_usecase import ReceitasUseCase


def get_receitas_usecase(session: Session = Depends(get_db)) -> ReceitasUseCase:
    repo: IReceitasRepository = ReceitasRepository(session)
    return ReceitasUseCase(repo)
