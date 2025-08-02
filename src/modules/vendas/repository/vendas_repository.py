# src/modules/vendas/repository/venda_repository.py

import os
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Sequence

from src.modules.vendas.dto.dto import VendaCreate, ItemVendaCreate, VendaResponse, ItemVendaResponse
from src.modules.vendas.abc_classes.vendas_abc import IVendaRepository

BASE_DIR = os.path.dirname(__file__)
QUERIES_FOLDER = os.path.join(BASE_DIR, "queries", "postgres")


class VendaRepository(IVendaRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def inserir_venda(self, venda: VendaCreate, total: float) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_venda.sql")
        query = open(query_path).read()

        result = self.session.execute(text(query), {
            "cliente_id": venda.cliente_id,
            "forma_pagamento_id": venda.forma_pagamento_id,
            "data_venda": venda.data_venda or datetime.now(),
            "data_pagamento": venda.data_pagamento,
            "total": total,
            "observacao": venda.observacao
        }).fetchone()

        self.session.commit()
        return result[0] if result else -1

    def inserir_item_venda(self, venda_id: int, item: ItemVendaCreate) -> None:
        query_path = os.path.join(QUERIES_FOLDER, "insert_item_venda.sql")
        query = open(query_path).read()

        self.session.execute(text(query), {
            "venda_id": venda_id,
            "produto_id": item.produto_id,
            "quantidade": item.quantidade,
            "preco_unitario": item.preco_unitario
        })
        self.session.commit()

    def buscar_vendas(self) -> list[VendaResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_vendas.sql")
        query = open(query_path).read()

        rows = self.session.execute(text(query)).fetchall()
        return [VendaResponse(**dict(row._mapping)) for row in rows]

    def buscar_itens_por_venda_id(self, venda_id: int) -> list[ItemVendaResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_itens_venda_por_venda_id.sql")
        query = open(query_path).read()

        rows = self.session.execute(text(query), {"venda_id": venda_id}).fetchall()
        return [ItemVendaResponse(**dict(row._mapping)) for row in rows]

    def registrar_saida_por_venda(self, produto_id: int, quantidade: int, data_mov: datetime) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_movimentacao_estoque.sql")
        query = open(query_path).read()

        result = self.session.execute(text(query), {
            "produto_id": produto_id,
            "quantidade": quantidade,
            "operacao_id": 5,  # Venda
            "data_mov": data_mov
        }).fetchone()

        self.session.commit()
        return result[0] if result else -1