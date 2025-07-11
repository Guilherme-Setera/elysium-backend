from fastapi import Depends
from src.modules.estoque.dto.dto import (
    MovimentacaoCreate,
    EstoqueAtualResponse,
    EstoqueBaixoResponse,
    OperacaoResponse
)
from src.modules.estoque.abc_classes.estoque_abc import IEstoqueRepository
from src.modules.estoque.repository.estoque_repository import EstoqueRepository
from src.infra.db.connection import get_db
from sqlalchemy.orm import Session


class EstoqueUseCase:
    def __init__(self, repo: IEstoqueRepository) -> None:
        self.repo: IEstoqueRepository = repo

    def registrar_entrada(self, data: MovimentacaoCreate) -> int:
        return self.repo.registrar_entrada(data)

    def listar_estoque_atual(self) -> list[EstoqueAtualResponse]:
        return self.repo.listar_estoque_atual()

    def listar_estoque_baixo(self) -> list[EstoqueBaixoResponse]:
        return self.repo.listar_estoque_baixo()

    def listar_operacoes(self) -> list[OperacaoResponse]:
        return self.repo.listar_operacoes()



def get_estoque_usecase(session: Session = Depends(get_db)) -> EstoqueUseCase:
    repo = EstoqueRepository(session)
    return EstoqueUseCase(repo)
