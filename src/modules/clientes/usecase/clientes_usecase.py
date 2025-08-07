from fastapi import Depends
from src.infra.db.connection import get_db
from sqlalchemy.orm import Session

from src.modules.clientes.repository.cliente_repository import ClienteRepository
from src.modules.clientes.abc_classes.clientes_abc import IClienteRepository
from src.modules.clientes.dto.dto import (
    ClienteCreate,
    ClienteUpdate,
    ClienteResponse
)


class ClientesUseCase:
    def __init__(self, repo: IClienteRepository) -> None:
        self.repo: IClienteRepository = repo

    def criar_cliente(self, cliente: ClienteCreate) -> int:
        return self.repo.cadastrar_cliente(cliente)
    
    def criar_clientes_em_lote(self, clientes: list[ClienteCreate]) -> list[int]:
        return self.repo.cadastrar_clientes_em_lote(clientes)
    
    def atualizar_cliente(self, cliente_id: int, data: ClienteUpdate) -> bool:
        linhas_afetadas = self.repo.atualizar_cliente(
            cliente_id=cliente_id,
            nome=data.nome,
            celular=data.celular,
            endereco=data.endereco,
            email=data.email,
            cpf=data.cpf,
            descricao=data.descricao,
        )
        return linhas_afetadas > 0

    def desativar_cliente(self, cliente_id: int) -> bool:
        linhas_afetadas: int = self.repo.desativar_cliente(cliente_id)
        return linhas_afetadas > 0

    def listar_clientes(self) -> list[ClienteResponse]:
        return self.repo.listar_clientes_ativos()


def get_usecase(session: Session = Depends(get_db)) -> ClientesUseCase:
    repo = ClienteRepository(session)
    return ClientesUseCase(repo)
