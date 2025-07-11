import os
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.modules.estoque.dto.dto import (
    MovimentacaoCreate,
    EstoqueAtualResponse,
    EstoqueBaixoResponse,
    OperacaoResponse
)
from src.modules.estoque.abc_classes.estoque_abc import IEstoqueRepository

BASE_DIR: str = os.path.dirname(__file__)
QUERIES_FOLDER: str = os.path.join(BASE_DIR, "queries", "postgres")


class EstoqueRepository(IEstoqueRepository):
    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def registrar_entrada(self, data: MovimentacaoCreate) -> int:
        query_path: str = os.path.join(QUERIES_FOLDER, "insert_entrada_estoque.sql")
        query: str = open(query_path).read()

        result = self.session.execute(text(query), {
            "produto_id": data.produto_id,
            "quantidade": data.quantidade,
            "operacao_id": data.operacao_id
        }).fetchone()

        self.session.commit()
        return result[0] if result else -1

    def listar_estoque_atual(self) -> list[EstoqueAtualResponse]:
        query_path: str = os.path.join(QUERIES_FOLDER, "select_estoque_atual.sql")
        query: str = open(query_path).read()

        rows = self.session.execute(text(query)).fetchall()

        return [
            EstoqueAtualResponse(
                produto_id=row[0],
                nome_produto=row[1],
                saldo_estoque=row[2]
            )
            for row in rows
        ]

    def listar_estoque_baixo(self) -> list[EstoqueBaixoResponse]:
        query_path: str = os.path.join(QUERIES_FOLDER, "select_estoque_baixo.sql")
        query: str = open(query_path).read()

        rows = self.session.execute(text(query)).fetchall()

        return [
            EstoqueBaixoResponse(
                produto_id=row[0],
                nome_produto=row[1],
                saldo_estoque=row[2],
                estoque_minimo=row[3]
            )
            for row in rows
        ]

    def listar_operacoes(self) -> list[OperacaoResponse]:
        query_path: str = os.path.join(QUERIES_FOLDER, "select_operacoes.sql")
        query: str = open(query_path).read()

        rows = self.session.execute(text(query)).fetchall()

        return [
            OperacaoResponse(
                id=row[0],
                descricao=row[1],
                tipo=row[2]
            )
            for row in rows
        ]
