import os
from datetime import date
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

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
    CategoriaCustoResponse

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
        # Usa a data fornecida, ou fallback para hoje
        data_ref = data.data_referencia or date.today()

        # 1. Registrar movimentação
        mov_query_path = os.path.join(QUERIES_FOLDER, "insert_movimentacao_estoque.sql")
        mov_query = open(mov_query_path).read()

        mov_result = self.session.execute(text(mov_query), {
            "produto_id": data.produto_id,
            "quantidade": data.quantidade,
            "operacao_id": data.operacao_id,
            "data_mov": data_ref
        }).fetchone()

        # 2. Se houver preço informado, encerrar anterior e inserir novo
        if data.preco_custo is not None and data.preco_venda is not None:
            self.encerrar_precos_produto(data.produto_id)

            preco_query_path = os.path.join(QUERIES_FOLDER, "insert_produto_preco.sql")
            preco_query = open(preco_query_path).read()

            self.session.execute(text(preco_query), {
                "produto_id": data.produto_id,
                "data_referencia": data_ref,
                "preco_custo": data.preco_custo,
                "preco_venda": data.preco_venda,
            })

        self.session.commit()
        return mov_result[0] if mov_result else -1


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
        query = open(query_path).read()

        result = self.session.execute(text(query), {"data_referencia": data_referencia})
        rows = result.fetchall()

        return [
            EstoqueAtualResponse(
                produto_id=row[0],
                nome_produto=row[1],
                saldo_estoque=row[2],
                preco_custo=row[3],
                preco_venda=row[4],
                data_movimentacao=row[5].date(),
            )
            for row in rows
        ]

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
        print("[LOG] Data recebida para salvar:", data.data_referencia, type(data.data_referencia))
        result = self.session.execute(
            text(query),
            {
                "categoria_id": data.categoria_id,  # agora usamos o ID da categoria
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

        # ✅ Log de depuração das datas
        print("[DEBUG] Datas recebidas no listar_custos_operacionais:")
        print(f"  → data_inicio: {data_inicio} ({type(data_inicio)})")
        print(f"  → data_fim: {data_fim} ({type(data_fim)})")

        rows = self.session.execute(
            text(query),
            {
                "data_inicio": data_inicio,
                "data_fim": data_fim
            }
        ).fetchall()

        # ✅ Log de retorno das linhas
        print("[DEBUG] Linhas retornadas:")
        for row in rows:
            print(f"  → data_referencia: {row[4]} ({type(row[4])})")

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