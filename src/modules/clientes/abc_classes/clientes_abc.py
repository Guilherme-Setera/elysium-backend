from abc import ABC, abstractmethod
from src.modules.clientes.dto.dto import ClienteCreate, ClienteResponse


class IClienteRepository(ABC):
    @abstractmethod
    def cadastrar_cliente(self, cliente: ClienteCreate) -> int:
        ...

    @abstractmethod
    def cadastrar_clientes_em_lote(self, clientes: list[ClienteCreate]) -> list[int]:
        ...

    @abstractmethod
    def atualizar_cliente(
        self,
        cliente_id: int,
        nome: str,
        celular: str,
        endereco: str,
        email: str | None = None,
        cpf: str | None = None
    ) -> int:
        ...

    @abstractmethod
    def desativar_cliente(self, cliente_id: int) -> int:
        ...

    @abstractmethod
    def listar_clientes_ativos(self) -> list[ClienteResponse]:
        ...
