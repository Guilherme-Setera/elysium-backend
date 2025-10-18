import os
from datetime import date
from typing import Optional, List, cast
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.engine import CursorResult

from src.modules.produtos.controller.dto import (
    ProdutoCadastro,
    ProdutoUpdate,
    ProdutoResponse,
    ProdutoPrecoResponse,
)

BASE_DIR: str = os.path.dirname(__file__)
QUERIES_FOLDER: str = os.path.join(BASE_DIR, "queries", "postgres")


class ProdutosRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def cadastrar_produto(self, produto: ProdutoCadastro) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_produto.sql")
        query = open(query_path).read()
        with self.session.begin():
            produto_id = self.session.execute(
                text(query),
                {
                    "nome": produto.nome,
                    "descricao": produto.descricao,
                    "meses_para_vencer": getattr(produto, "meses_para_vencer", None),
                    "ativo": getattr(produto, "ativo", True),
                    "estoque_minimo": getattr(produto, "estoque_minimo", None),
                },
            ).scalar_one()
        return int(produto_id)

    def listar_produtos(self, data_referencia: Optional[date] = None) -> List[ProdutoResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_produtos.sql")
        query: str = open(query_path).read()
        rows = self.session.execute(text(query)).fetchall()
        res: List[ProdutoResponse] = []
        for row in rows:
            m = row._mapping
            res.append(
                ProdutoResponse(
                    id=m["id"],
                    nome=m["nome"],
                    descricao=m.get("descricao"),
                    meses_para_vencer=m.get("meses_para_vencer"),
                    ativo=m["ativo"],
                    estoque_minimo=m.get("estoque_minimo"),
                    preco_custo=m.get("preco_custo"),
                    preco_venda=m.get("preco_venda"),
                    data_preco=m.get("data_preco"),
                )
            )
        return res

    def listar_precos_produto(self, produto_id: int) -> List[ProdutoPrecoResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_precos_produto.sql")
        query: str = open(query_path).read()
        rows = self.session.execute(
            text(query),
            {"produto_id": produto_id},
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
        result = cast(
            CursorResult,
            self.session.execute(
                text(query),
                {
                    "produto_id": produto_id,
                    "data_referencia": data_referencia,
                    "preco_custo": preco_custo,
                    "preco_venda": preco_venda,
                },
            ),
        )
        self.session.commit()
        return result.rowcount

    def desativar_produto(self, produto_id: int) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "desativar_produto.sql")
        query: str = open(query_path).read()
        result = cast(
            CursorResult,
            self.session.execute(
                text(query),
                {"id": produto_id},
            ),
        )
        self.session.commit()
        return result.rowcount

    def atualizar_produto(self, produto_id: int, data: ProdutoUpdate) -> bool:
        dados = vars(data)
        dados["produto_id"] = produto_id

        query_path = os.path.join(QUERIES_FOLDER, "update_produto.sql")
        query = open(query_path).read()

        result = cast(CursorResult, self.session.execute(text(query), dados))
        self.session.commit()
        return result.rowcount > 0

    def buscar_produto_por_id(self, produto_id: int, data_referencia: Optional[date] = None) -> Optional[ProdutoResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_produto_por_id.sql")
        query: str = open(query_path).read()
        row = self.session.execute(
            text(query),
            {"id": produto_id},
        ).fetchone()
        if not row:
            return None
        m = row._mapping
        return ProdutoResponse(
            id=m["id"],
            nome=m["nome"],
            descricao=m.get("descricao"),
            meses_para_vencer=m.get("meses_para_vencer"),
            ativo=m["ativo"],
            estoque_minimo=m.get("estoque_minimo"),
            preco_custo=m.get("preco_custo"),
            preco_venda=m.get("preco_venda"),
            data_preco=m.get("data_preco"),
        )
