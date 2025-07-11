import os
from datetime import date
from typing import Optional, List, cast
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.engine import CursorResult

from src.modules.produtos.controller.dto import ProdutoCreate, ProdutoUpdate, ProdutoResponse, ProdutoPrecoResponse

BASE_DIR: str = os.path.dirname(__file__)
QUERIES_FOLDER: str = os.path.join(BASE_DIR, "queries", "postgres")

class ProdutosRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def cadastrar_produto(self, produto: ProdutoCreate) -> int:
        # 1. Insere o produto
        query_path = os.path.join(QUERIES_FOLDER, "insert_produto.sql")
        query: str = open(query_path).read()
        result = self.session.execute(
            text(query),
            {
                "nome": produto.nome,
                "descricao": produto.descricao,
                "validade": produto.validade
            }
        ).fetchone()
        produto_id = result[0] if result else -1

        # 2. Insere o preço inicial
        query_path_preco = os.path.join(QUERIES_FOLDER, "insert_produto_preco.sql")
        query_preco: str = open(query_path_preco).read()
        self.session.execute(
            text(query_preco),
            {
                "produto_id": produto_id,
                "data_referencia": produto.data_referencia or date.today(),
                "preco_custo": produto.preco_custo,
                "preco_venda": produto.preco_venda
            }
        )
        self.session.commit()
        return produto_id

    def listar_produtos(self, data_referencia: Optional[date] = None) -> List[ProdutoResponse]:
        # Usa a query que aceita data_referencia como parâmetro
        query_path = os.path.join(QUERIES_FOLDER, "select_produtos.sql")
        query: str = open(query_path).read()
        rows = self.session.execute(
            text(query),
            {"data_referencia": data_referencia or date.today()}
        ).fetchall()
        return [
            ProdutoResponse(
                id=row.id,
                nome=row.nome,
                descricao=row.descricao,
                validade=row.validade,
                ativo=row.ativo,
                preco_custo=row.preco_custo,
                preco_venda=row.preco_venda,
                data_preco=row.data_preco,
            )
            for row in rows
        ]

    def listar_precos_produto(self, produto_id: int) -> List[ProdutoPrecoResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_precos_produto.sql")
        query: str = open(query_path).read()
        rows = self.session.execute(
            text(query),
            {"produto_id": produto_id}
        ).fetchall()
        return [
            ProdutoPrecoResponse(
                id=row.id,
                produto_id=row.produto_id,
                data_referencia=row.data_referencia,
                preco_custo=row.preco_custo,
                preco_venda=row.preco_venda,
            )
            for row in rows
        ]

    def inserir_novo_preco(self, produto_id: int, data_referencia: date, preco_custo: float, preco_venda: float) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_produto_preco.sql")
        query: str = open(query_path).read()
        result = cast(CursorResult, self.session.execute(
            text(query),
            {
                "produto_id": produto_id,
                "data_referencia": data_referencia,
                "preco_custo": preco_custo,
                "preco_venda": preco_venda,
            }
        ))
        self.session.commit()
        return result.rowcount

    def desativar_produto(self, produto_id: int) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "desativar_produto.sql")
        query: str = open(query_path).read()
        result = cast(CursorResult, self.session.execute(
            text(query),
            {"id": produto_id}
        ))
        self.session.commit()
        return result.rowcount

    def atualizar_produto(self, produto_id: int, data: ProdutoUpdate) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "update_produto.sql")
        query: str = open(query_path).read()
        result = cast(CursorResult, self.session.execute(
            text(query),
            {
                "id": produto_id,
                "nome": data.nome,
                "descricao": data.descricao,
                "validade": data.validade
            }
        ))
        self.session.commit()
        return result.rowcount

    def buscar_produto_por_id(self, produto_id: int, data_referencia: Optional[date] = None) -> Optional[ProdutoResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_produto_por_id.sql")
        query: str = open(query_path).read()
        row = self.session.execute(
            text(query),
            {
                "id": produto_id,
                "data_referencia": data_referencia or date.today()
            }
        ).fetchone()
        if not row:
            return None
        return ProdutoResponse(
            id=row.id,
            nome=row.nome,
            descricao=row.descricao,
            validade=row.validade,
            ativo=row.ativo,
            preco_custo=row.preco_custo,
            preco_venda=row.preco_venda,
            data_preco=row.data_preco,
        )
