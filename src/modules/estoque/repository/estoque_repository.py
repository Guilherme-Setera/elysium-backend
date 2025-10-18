import os
from datetime import date, datetime
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import HTTPException

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
    CustoEstoqueResponse,
    CategoriaCustoResponse,
    MovimentacaoUpdate
)
from src.modules.estoque.abc_classes.estoque_abc import IEstoqueRepository

BASE_DIR: str = os.path.dirname(__file__)
QUERIES_FOLDER: str = os.path.join(BASE_DIR, "queries", "postgres")


class EstoqueRepository(IEstoqueRepository):
    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def cadastrar_produto(self, produto: ProdutoCreate) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_produto.sql")
        query = open(query_path).read()

        result = self.session.execute(text(query), {
            "nome": produto.nome,
            "descricao": produto.descricao,
            "validade": produto.validade,
            "ativo": produto.ativo,
            "estoque_minimo": produto.estoque_minimo
        }).fetchone()

        self.session.commit()
        return result[0] if result else -1

    def cadastrar_produtos_em_lote(self, produtos: list[ProdutoCreate]) -> list[int]:
        if not produtos:
            return []

        query_path = os.path.join(QUERIES_FOLDER, "insert_produtos_em_lote.sql")
        base_query = open(query_path).read()

        values = []
        params = {}

        for idx, p in enumerate(produtos):
            values.append(f"(:nome{idx}, :descricao{idx}, :validade{idx}, :ativo{idx}, :estoque_minimo{idx})")
            params[f'nome{idx}'] = p.nome
            params[f'descricao{idx}'] = p.descricao
            params[f'validade{idx}'] = p.validade
            params[f'ativo{idx}'] = p.ativo
            params[f'estoque_minimo{idx}'] = p.estoque_minimo

        query = base_query.replace("{valores}", ",\n    ".join(values))

        result = self.session.execute(text(query), params)
        ids = [row[0] for row in result.fetchall()]
        self.session.commit()
        return ids

    def registrar_movimentacao(self, data: MovimentacaoCreate) -> int:
        mov_query_path = os.path.join(QUERIES_FOLDER, "insert_movimentacao_estoque_produtos.sql")
        mov_query = open(mov_query_path).read()

        data_mov = data.data_mov or datetime.now()

        mov_result = self.session.execute(text(mov_query), {
            "produto_id": data.produto_id,
            "quantidade": data.quantidade,
            "operacao_id": data.operacao_id,
            "venda_id": data.venda_id,
            "data_mov": data_mov,
            "lote_numero": data.lote_numero,
            "data_validade": data.data_validade,
            "preco_custo": data.preco_custo,
            "preco_venda": data.preco_venda,
            "tipo": data.tipo
        }).fetchone()

        self.session.commit()
        return mov_result[0] if mov_result else -1

    def atualizar_movimentacao(self, id: int, data: MovimentacaoUpdate) -> int:
        upd_sql = open(os.path.join(QUERIES_FOLDER, "update_movimentacao_estoque_produtos.sql")).read()
        insert_preco_sql = open(os.path.join(QUERIES_FOLDER, "insert_produto_preco.sql")).read()

        with self.session.begin():
            row = self.session.execute(
                text(upd_sql),
                {
                    "id": id,
                    "produto_id": data.produto_id,
                    "tipo": data.tipo,
                    "quantidade": data.quantidade,
                    "data_mov": data.data_mov,
                    "operacao_id": data.operacao_id,
                    "venda_id": data.venda_id,
                    "lote_numero": data.lote_numero,
                    "data_validade": data.data_validade,
                    "preco_custo": data.preco_custo,
                    "preco_venda": data.preco_venda,
                },
            ).fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Movimentação não encontrada ou vinculada a venda.")

            mov_id, produto_id, tipo, data_mov, _op_id = row
            data_ref = (data_mov.date() if hasattr(data_mov, "date") else data_mov) or date.today()

            if data.preco_custo is not None and data.preco_venda is not None:
                if (tipo or "").lower() != "entrada":
                    raise HTTPException(status_code=400, detail="Preço só pode ser ajustado em movimentações de entrada.")
                self.encerrar_precos_produto(produto_id)
                self.session.execute(
                    text(insert_preco_sql),
                    {
                        "produto_id": produto_id,
                        "data_referencia": data_ref,
                        "preco_custo": data.preco_custo,
                        "preco_venda": data.preco_venda,
                    },
                )

            return int(mov_id)

    def inserir_preco_produto(self, produto_id: int, preco_custo: float, preco_venda: float, data: date) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_produto_preco.sql")
        query = open(query_path).read()

        result = self.session.execute(text(query), {
            "produto_id": produto_id,
            "data_referencia": data,
            "preco_custo": preco_custo,
            "preco_venda": preco_venda,
        }).fetchone()

        self.session.commit()
        return result[0] if result else -1

    def buscar_preco_atual(self, produto_id: int, data_base: date) -> Optional[PrecoAtualResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_preco_atual.sql")
        query = open(query_path).read()

        row = self.session.execute(text(query), {
            "produto_id": produto_id,
            "data_base": data_base,
        }).fetchone()

        if row:
            return PrecoAtualResponse(
                nome=row[0],
                preco_custo=row[1],
                preco_venda=row[2],
                estoque=row[3]
            )
        return None

    def listar_precos_produto(self, produto_id: int) -> list[ProdutoPrecoResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_precos_produto.sql")
        query = open(query_path).read()

        rows = self.session.execute(text(query), {"produto_id": produto_id}).fetchall()

        return [
            ProdutoPrecoResponse(
                id=row[0],
                produto_id=row[1],
                data_referencia=row[2],
                preco_custo=row[3],
                preco_venda=row[4],
                data_fim=row[5] if len(row) > 5 else None
            )
            for row in rows
        ]

    def encerrar_precos_produto(self, id: int) -> None:
        query_path = os.path.join(QUERIES_FOLDER, "encerrar_preco_produto.sql")
        query = open(query_path).read()
        self.session.execute(text(query), {"id": id})
        self.session.commit()

    def desativar_produto(self, id: int) -> bool:
        self.encerrar_precos_produto(id)

        query_path = os.path.join(QUERIES_FOLDER, "desativar_produto.sql")
        query = open(query_path).read()

        result = self.session.execute(text(query), {"id": id})
        self.session.commit()

        rowcount = getattr(result, 'rowcount', None)
        return rowcount is not None and rowcount > 0

    def listar_estoque_atual(self, data_referencia: date) -> list[EstoqueAtualResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_estoque_atual.sql")
        with open(query_path, encoding="utf-8") as f:
            query = f.read()

        # ✅ passe somente o bind que a SQL espera
        result = self.session.execute(
            text(query),
            {"data_referencia": data_referencia}
        )
        rows = result.fetchall()

        responses: list[EstoqueAtualResponse] = []
        for row in rows:
            responses.append(
                EstoqueAtualResponse(
                    produto_id=row.produto_id,
                    nome_produto=row.nome_produto,
                    saldo_estoque=row.saldo_estoque,
                    preco_custo=row.preco_custo,
                    preco_venda=row.preco_venda,
                    data_movimentacao=row.data_movimentacao,
                    ultima_mov_id=row.ultima_mov_id,
                    ultima_quantidade=row.ultima_quantidade,
                    tipo_ultima=row.tipo_ultima,
                    operacao_id_ultima=row.operacao_id_ultima,
                    lote_ultimo=row.lote_ultimo,
                )
            )
        return responses


    def listar_estoque_baixo(self) -> list[EstoqueBaixoResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_estoque_baixo.sql")
        query = open(query_path).read()

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
        query_path = os.path.join(QUERIES_FOLDER, "select_operacoes.sql")
        query = open(query_path).read()

        rows = self.session.execute(text(query)).fetchall()

        return [
            OperacaoResponse(
                id=row[0],
                descricao=row[1],
                tipo=row[2]
            )
            for row in rows
        ]

    def listar_produtos(self) -> list[ProdutoResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_produtos.sql")
        query = open(query_path).read()

        rows = self.session.execute(text(query)).fetchall()

        return [
            ProdutoResponse(
                id=row[0],
                nome=row[1],
                descricao=row[2],
                validade=row[3],
                ativo=row[4],
                estoque_minimo=row[5]
            )
            for row in rows
        ]

    def inserir_custo_operacional(self, data: CustoOperacionalCreate) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_custo_operacional.sql")
        with open(query_path) as f:
            query = f.read()
        result = self.session.execute(
            text(query),
            {
                "categoria_id": data.categoria_id,
                "valor": data.valor,
                "data_referencia": data.data_referencia,
                "observacao": data.observacao,
            }
        ).fetchone()

        self.session.commit()
        return result[0] if result else -1

    def listar_custos_operacionais(self, data_inicio: date, data_fim: date) -> list[CustoOperacionalResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_custos_operacionais_por_data.sql")
        with open(query_path) as f:
            query = f.read()

        rows = self.session.execute(
            text(query),
            {
                "data_inicio": data_inicio,
                "data_fim": data_fim
            }
        ).fetchall()

        return [
            CustoOperacionalResponse(
                id=row[0],
                categoria_id=row[1],
                nome_categoria=row[2],
                valor=row[3],
                data_referencia=row[4],
                observacao=row[5]
            )
            for row in rows
        ]

    def listar_custos_estoque_por_data(self, data_inicio: date, data_fim: date) -> list[CustoEstoqueResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_custos_estoque_por_data.sql")
        query = open(query_path).read()

        rows = self.session.execute(text(query), {
            "data_inicio": data_inicio,
            "data_fim": data_fim
        }).fetchall()

        return [
            CustoEstoqueResponse(
                produto_id=row[0],
                nome_produto=row[1],
                data_movimentacao=row[2].date(),
                quantidade=row[3],
                preco_custo=row[4],
                custo_total=row[5]
            )
            for row in rows
        ]

    def inserir_categoria_custo(self, nome: str) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_categoria_custo.sql")
        query = open(query_path).read()

        result = self.session.execute(text(query), {"nome": nome}).fetchone()
        self.session.commit()

        return result[0] if result else -1

    def listar_categorias_custo(self) -> list[CategoriaCustoResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_categorias_custo.sql")
        query = open(query_path).read()

        rows = self.session.execute(text(query)).fetchall()

        return [CategoriaCustoResponse(id=row[0], nome=row[1]) for row in rows]
