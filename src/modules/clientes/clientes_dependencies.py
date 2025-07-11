from fastapi import Depends
from sqlalchemy.orm import Session

from src.infra.db.connection import get_db
from src.modules.clientes.usecase.clientes_usecase import ClientesUseCase
from src.modules.clientes.repository.cliente_repository import ClienteRepository


def get_clientes_usecase(session: Session = Depends(get_db)) -> ClientesUseCase:
    repo = ClienteRepository(session)
    return ClientesUseCase(repo)
