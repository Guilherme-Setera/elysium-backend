import os
from datetime import date
from typing import Optional
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.modules.estoque.abc_classes.materia_prima_abc import IMateriasPrimaRepository
from src.modules.estoque.dto.dto_materia_prima import (
    MateriaPrimaCreate,
    MateriaPrimaResponse,
    MateriaPrimaUpdate,
    PrecoMateriaPrimaResponse,
    PrecoMateriaPrimaUnitarioResponse,
    EstoqueMateriaPrimaAtualResponse,
    MovimentacaoMateriaPrimaCreate,
    MateriaPrimaPrecoCreate,
)

BASE_DIR: str = os.path.dirname(__file__)
QUERIES_FOLDER: str = os.path.join(BASE_DIR, "queries", "postgres_materia_prima")


class MateriaPrimaRepository(IMateriasPrimaRepository):
    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def cadastrar_materia_prima(self, materia: MateriaPrimaCreate) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_materia_prima.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()

        params = {
            "nome": materia.nome,
            "descricao": materia.descricao,
            "estoque_minimo_unidade": materia.estoque_minimo_unidade,
            "estoque_minimo": getattr(materia, "estoque_minimo", None),
            "medida_base": materia.medida_base,
            "is_grama": materia.is_grama,
            "is_ml": materia.is_ml,
            "unidade": materia.unidade,
            "densidade": materia.densidade,
        }

        result = self.session.execute(text(query), params).fetchone()
        self.session.commit()
        return int(result[0]) if result and result[0] is not None else -1

    def inativar_materia_prima(self, id: int) -> bool:
        query_path = os.path.join(QUERIES_FOLDER, "inativar_materia_prima.sql")
        query = open(query_path).read()

        result = self.session.execute(text(query), {"id": id})
        self.session.commit()

        rowcount = getattr(result, "rowcount", None)
        return rowcount is not None and rowcount > 0

    def listar_materias_prima(self) -> list[MateriaPrimaResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_materias_prima.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()

        rows = self.session.execute(text(query)).fetchall()

        return [
            MateriaPrimaResponse(
                id=row[0],
                nome=row[1],
                descricao=row[2],
                ativo=row[3],
                estoque_minimo=row[4],
                medida_base=row[5],
                unidade_base=row[6],
                densidade=row[7],
            )
            for row in rows
        ]
    
    def atualizar_materia_prima(self, materia_prima_id: int, data: MateriaPrimaUpdate) -> int:
        path = os.path.join(QUERIES_FOLDER, "update_materia_prima.sql")
        with open(path, "r", encoding="utf-8") as f:
            query = f.read()

        unidade = getattr(data, "unidade", None)
        is_grama, is_ml = None, None
        if unidade == "g":
            is_grama, is_ml = True, False
        elif unidade == "ml":
            is_grama, is_ml = False, True

        params = {
            "materia_prima_id": materia_prima_id,
            "nome": getattr(data, "nome", None),
            "descricao": getattr(data, "descricao", None),
            "ativo": getattr(data, "ativo", None),
            "estoque_minimo_unidade": getattr(data, "estoque_minimo_unidade", None),
            "medida_base": getattr(data, "medida_base", None),
            "unidade": unidade,
            "is_grama": is_grama if is_grama is not None else getattr(data, "is_grama", None),
            "is_ml": is_ml if is_ml is not None else getattr(data, "is_ml", None),
        }

        row = self.session.execute(text(query), params).fetchone()
        self.session.commit()
        return int(row[0]) if row else -1
        
    def encerrar_precos_materia_prima(self, id: int) -> None:
        query_path = os.path.join(QUERIES_FOLDER, "encerrar_preco_materia_prima.sql")
        query = open(query_path).read()
        self.session.execute(text(query), {"id": id})
        self.session.commit()
    
    def registrar_movimentacao_materia_prima(self, data: MovimentacaoMateriaPrimaCreate) -> int:
        data_ref = getattr(data, "data_referencia", None) or date.today()

        mov_query_path = os.path.join(QUERIES_FOLDER, "insert_movimentacao_estoque_materia_prima.sql")
        with open(mov_query_path, "r", encoding="utf-8") as f:
            mov_query = f.read()

        mov_params = {
            "materia_prima_id": data.materia_prima_id,
            "quantidade_unidade": getattr(data, "quantidade", 0),
            "operacao_id": data.operacao_id,
            "data_mov": data_ref,
            "preco_custo": getattr(data, "preco_custo", None),
        }

        mov_result = self.session.execute(text(mov_query), mov_params).fetchone()
        if not mov_result:
            self.session.rollback()
            return -1

        self.session.commit()
        return int(mov_result[0])
    
    def buscar_preco_materia_prima(
        self, materia_prima_id: int, data_base
    ) -> Optional[PrecoMateriaPrimaResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_preco_materia_prima.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()

        row = self.session.execute(
            text(query),
            {"materia_prima_id": materia_prima_id, "data_base": data_base},
        ).mappings().fetchone()

        if not row:
            return None

        return PrecoMateriaPrimaResponse(
            nome=row["nome"],
            preco_custo=row["preco_custo"],
            estoque_unidade=row["estoque_unidade"],
            estoque_medida=row["estoque_medida"],
        )
    
    def listar_precos_materia_prima(self, materia_prima_id: int) -> list[PrecoMateriaPrimaUnitarioResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_preco_materia_prima_unitario.sql")
        query = open(query_path).read()

        rows = self.session.execute(
            text(query),
            {"materia_prima_id": materia_prima_id},
        ).fetchall()

        return [
            PrecoMateriaPrimaUnitarioResponse(
                id=row[0],
                materia_prima_id=row[1],
                data_referencia=row[2],
                preco_custo=row[3],
                data_fim=row[4] if len(row) > 4 else None,
            )
            for row in rows
        ]

    def listar_estoque_materia_prima_atual(self, data_referencia: date) -> list[EstoqueMateriaPrimaAtualResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_estoque_materia_prima_atual.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()

        result = self.session.execute(text(query), {"data_referencia": data_referencia})
        rows = result.fetchall()

        return [
            EstoqueMateriaPrimaAtualResponse(
                materia_prima_id=row[0],
                nome_materia_prima=row[1],
                unidade_base=row[2],
                medida_base=float(row[3]) if row[3] is not None else 0.0,
                saldo_estoque=float(row[4]) if row[4] is not None else 0.0,
                preco_custo=float(row[5]) if row[5] is not None else None,
                data_movimentacao=row[6],
                lote=int(row[7]) if row[7] is not None else None,
            )
            for row in rows
        ]

    def inserir_preco_materia_prima(self, data: MateriaPrimaPrecoCreate) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_materia_prima_preco.sql")
        query = open(query_path).read()

        result = self.session.execute(
            text(query),
            {
                "materia_prima_id": data.materia_prima_id,
                "data_referencia": data.data_referencia,
                "preco_custo": data.preco_custo,
                "data_fim": data.data_fim,
            },
        ).fetchone()

        self.session.commit()
        return result[0] if result else -1
