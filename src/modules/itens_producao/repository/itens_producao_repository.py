# src/modules/itens_producao/repository/produtos_consumo_repository.py
from __future__ import annotations

import os
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Any
from datetime import date

from src.utils.datetime_utils import normalize_input_datetime
from src.modules.itens_producao.abc_classes.abc_classes import IItensProducaoRepository
from src.modules.itens_producao.dto.dto_itens_producao import (
    ItemConsumoCreate,
    ItemConsumoUpdate,
    MovimentacaoItemProducaoEntradaCreate,
    MovimentacaoItemProducaoResponse,
    EstoqueAtualItemProducaoResponse

)

BASE_DIR: str = os.path.dirname(__file__)
QUERIES_FOLDER: str = os.path.join(BASE_DIR, "queries", "postgres")


class ItensProducaoRepository(IItensProducaoRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def cadastrar_item_consumo(self, data: ItemConsumoCreate) -> int:
        path = os.path.join(QUERIES_FOLDER, "insert_produto_consumo.sql")
        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()

        params = {
            "nome": data.nome,
            "ativo": getattr(data, "ativo", None),
            "estoque_minimo": getattr(data, "estoque_minimo", None),
        }

        row = self.session.execute(text(sql), params).fetchone()
        self.session.commit()
        return int(row[0]) if row else -1

    def atualizar_item_consumo(self, item_consumo_id: int, data: ItemConsumoUpdate) -> int:
        path = os.path.join(QUERIES_FOLDER, "update_produto_consumo.sql")
        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()

        params = {
            "item_consumo_id": item_consumo_id,
            "nome": data.nome,
            "ativo": getattr(data, "ativo", None),
            "estoque_minimo": getattr(data, "estoque_minimo", None),
            "limpar_estoque_minimo": getattr(data, "limpar_estoque_minimo", None),
        }

        row = self.session.execute(text(sql), params).fetchone()
        self.session.commit()
        return int(row[0]) if row else -1

    def desativar_item_consumo(self, item_consumo_id: int) -> int:
        path = os.path.join(QUERIES_FOLDER, "desativar_produto_consumo.sql")
        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()

        row = self.session.execute(text(sql), {"id": item_consumo_id}).fetchone()
        self.session.commit()
        return int(row[0]) if row else -1
    
    def listar_itens_producao(self, somente_ativos: bool | None = None) -> list[dict[str, Any]]:
        path = os.path.join(QUERIES_FOLDER, "listar_itens_producao.sql")
        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()

        rows = self.session.execute(
            text(sql), {"somente_ativos": somente_ativos}
        ).mappings().all()

        return [dict(r) for r in rows]

    def registrar_entrada_item_producao(
        self, data: MovimentacaoItemProducaoEntradaCreate
    ) -> int:
        path = os.path.join(
            QUERIES_FOLDER, "insert_movimentacao_itens_producao_estoque_entradas.sql"
        )
        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()

        dt_local = normalize_input_datetime(data.data_movimentacao)

        params = {
            "item_consumo_id": data.item_consumo_id,
            "quantidade": data.quantidade,
            "preco_custo": data.preco_custo,
            "data_movimentacao": dt_local,
            "is_ativo": data.is_ativo,
            "descricao": data.descricao,
        }

        row = self.session.execute(text(sql), params).fetchone()
        self.session.commit()
        return int(row[0]) if row and row[0] is not None else -1
    
    def listar_movimentacoes_itens_producao(
        self,
        dia_limite: date,
    ) -> list[MovimentacaoItemProducaoResponse]:
        path = os.path.join(QUERIES_FOLDER, "listar_movimentacoes_itens_producao.sql")
        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()

        rows = (
            self.session.execute(
                text(sql),
                {"dia_limite": dia_limite.isoformat()},
            )
            .mappings()
            .all()
        )

        return [MovimentacaoItemProducaoResponse(**dict(r)) for r in rows]
    
    def listar_estoque_atual_itens_producao(
        self,
        data_referencia: date,
    ) -> list[EstoqueAtualItemProducaoResponse]:
        path = os.path.join(QUERIES_FOLDER, "select_estoque_atual_itens_producao.sql")
        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()

        rows = (
            self.session.execute(
                text(sql),
                {"data_referencia": data_referencia.isoformat()},
            )
            .mappings()
            .all()
        )
        return [EstoqueAtualItemProducaoResponse(**dict(r)) for r in rows]