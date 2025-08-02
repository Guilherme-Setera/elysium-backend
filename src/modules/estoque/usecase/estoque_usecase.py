from datetime import date
from typing import List, Optional

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
from src.modules.estoque.abc_classes.estoque_abc import IEstoqueRepository


class EstoqueUseCase:
    def __init__(self, repo: IEstoqueRepository) -> None:
        self.repo: IEstoqueRepository = repo

    def registrar_movimentacao(self, data: MovimentacaoCreate) -> int:
        return self.repo.registrar_movimentacao(data)

    def listar_estoque_atual(self, data_referencia: date) -> List[EstoqueAtualResponse]:
        return self.repo.listar_estoque_atual(data_referencia)

    def listar_estoque_baixo(self) -> List[EstoqueBaixoResponse]:
        return self.repo.listar_estoque_baixo()

    def listar_operacoes(self) -> List[OperacaoResponse]:
        return self.repo.listar_operacoes()

    def cadastrar_produto(self, produto: ProdutoCreate) -> int:
        return self.repo.cadastrar_produto(produto)

    def cadastrar_produtos_em_lote(self, produtos: List[ProdutoCreate]) -> List[int]:
        return self.repo.cadastrar_produtos_em_lote(produtos)

    def listar_produtos(self) -> List[ProdutoResponse]:
        return self.repo.listar_produtos()

    def desativar_produto(self, id: int) -> bool:
        return self.repo.desativar_produto(id)

    # ✅ NOVOS MÉTODOS DE PREÇO

    def inserir_preco_produto(self, produto_id: int, preco_custo: float, preco_venda: float, data_referencia: date) -> int:
        return self.repo.inserir_preco_produto(produto_id, preco_custo, preco_venda, data_referencia)

    def buscar_preco_atual(self, produto_id: int, data_base: date) -> Optional[PrecoAtualResponse]:
        return self.repo.buscar_preco_atual(produto_id, data_base)

    def listar_precos_produto(self, produto_id: int) -> List[ProdutoPrecoResponse]:
        return self.repo.listar_precos_produto(produto_id)
    
    def inserir_custo_operacional(self, data: CustoOperacionalCreate) -> int:
        return self.repo.inserir_custo_operacional(data)

    def listar_custos_operacionais(self, data_inicio: date, data_fim: date) -> List[CustoOperacionalResponse]:
        return self.repo.listar_custos_operacionais(data_inicio, data_fim)

    def listar_custos_estoque_por_data(self, data_inicio: date, data_fim: date) -> List[CustoEstoqueResponse]:
        return self.repo.listar_custos_estoque_por_data(data_inicio, data_fim)