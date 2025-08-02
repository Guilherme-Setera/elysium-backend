from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

from src.modules.estoque.dto.dto import (
    MovimentacaoCreate,
    EstoqueAtualResponse,
    EstoqueBaixoResponse,
    OperacaoResponse,
    ProdutoCreate,
    ProdutoResponse,
    ProdutoPrecoResponse,
    PrecoAtualResponse,
    CustoOperacionalCreate,
    CustoOperacionalResponse,
    CustoEstoqueResponse
)


class IEstoqueRepository(ABC):
    @abstractmethod
    def registrar_movimentacao(self, data: MovimentacaoCreate) -> int:
        ...

    @abstractmethod
    def listar_estoque_atual(self, data_referencia: date) -> List[EstoqueAtualResponse]:
        ...

    @abstractmethod
    def listar_estoque_baixo(self) -> List[EstoqueBaixoResponse]:
        ...

    @abstractmethod
    def listar_operacoes(self) -> List[OperacaoResponse]:
        ...

    @abstractmethod
    def cadastrar_produto(self, produto: ProdutoCreate) -> int:
        ...

    @abstractmethod
    def cadastrar_produtos_em_lote(self, produtos: List[ProdutoCreate]) -> List[int]:
        ...

    @abstractmethod
    def listar_produtos(self) -> List[ProdutoResponse]:
        ...

    @abstractmethod
    def desativar_produto(self, id: int) -> bool:
        ...

    # ✅ NOVOS MÉTODOS PARA PREÇOS

    @abstractmethod
    def inserir_preco_produto(self, produto_id: int, preco_custo: float, preco_venda: float, data: date) -> int:
        ...

    @abstractmethod
    def encerrar_precos_produto(self, id: int) -> None:
        ...

    @abstractmethod
    def buscar_preco_atual(self, produto_id: int, data_base: date) -> Optional[PrecoAtualResponse]:
        ...

    @abstractmethod
    def listar_precos_produto(self, produto_id: int) -> List[ProdutoPrecoResponse]:
        ...

    @abstractmethod
    def inserir_custo_operacional(self, data: CustoOperacionalCreate) -> int:
        ...

    @abstractmethod
    def listar_custos_operacionais(self, data_inicio: date, data_fim: date) -> List[CustoOperacionalResponse]:
        ... 

    @abstractmethod
    def listar_custos_estoque_por_data(self, data_inicio: date, data_fim: date) -> List[CustoEstoqueResponse]:
        ...    