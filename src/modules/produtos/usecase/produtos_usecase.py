from datetime import date
from typing import Optional, List

from src.modules.produtos.repository.produtos_repository import ProdutosRepository
from src.modules.produtos.controller.dto import (
    ProdutoCadastro,
    ProdutoUpdate,
    ProdutoResponse,
    ProdutoPrecoResponse,
    ProdutoUpdateComId
)

class ProdutosUseCase:
    def __init__(self, repository: ProdutosRepository):
        self.repository = repository

    def cadastrar_produto(self, data: ProdutoCadastro) -> int:
        return self.repository.cadastrar_produto(data)

    def listar_produtos(self, data_referencia: Optional[date] = None) -> List[ProdutoResponse]:
        return self.repository.listar_produtos(data_referencia=data_referencia)

    def listar_precos_produto(self, produto_id: int) -> List[ProdutoPrecoResponse]:
        return self.repository.listar_precos_produto(produto_id)

    def inserir_novo_preco(self, produto_id: int, data_referencia: date, preco_custo: float, preco_venda: float) -> bool:
        linhas_afetadas = self.repository.inserir_novo_preco(produto_id, data_referencia, preco_custo, preco_venda)
        return linhas_afetadas > 0

    def desativar_produto(self, produto_id: int) -> bool:
        linhas_afetadas = self.repository.desativar_produto(produto_id)
        return linhas_afetadas > 0

    def atualizar_produto(self, produto_id: int, data: ProdutoUpdate) -> bool:
        linhas_afetadas = self.repository.atualizar_produto(produto_id, data)
        return linhas_afetadas > 0

    def atualizar_produtos_em_lote(self, updates: list[ProdutoUpdateComId]) -> int:
        count = 0
        for item in updates:
            rowcount = self.repository.atualizar_produto(item.id, item)
            count += rowcount
        return count

    def buscar_produto_por_id(self, produto_id: int, data_referencia: Optional[date] = None) -> Optional[ProdutoResponse]:
        return self.repository.buscar_produto_por_id(produto_id, data_referencia)
