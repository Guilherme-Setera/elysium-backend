import os
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Sequence, Optional

from src.modules.vendas.dto.dto import VendaCreate, ItemVendaCreate, VendaResponse, ItemVendaResponse, VendaUpdate
from src.modules.vendas.abc_classes.vendas_abc import IVendaRepository

BASE_DIR = os.path.dirname(__file__)
QUERIES_FOLDER = os.path.join(BASE_DIR, "queries", "postgres")


class VendaRepository(IVendaRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def inserir_venda(self, venda: VendaCreate, total: float) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_venda.sql")
        query = open(query_path).read()

        data_venda = venda.data_venda or datetime.now()
        data_pagamento = venda.data_pagamento

        pago = (
            data_pagamento is not None and
            data_pagamento.date() == data_venda.date()
        )

        result = self.session.execute(text(query), {
            "cliente_id": venda.cliente_id,
            "forma_pagamento_id": venda.forma_pagamento_id,
            "data_venda": data_venda,
            "data_pagamento": data_pagamento,
            "total": total,
            "observacao": venda.observacao,
            "pago": pago
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

    def registrar_saida_por_venda(self, produto_id: int, quantidade: int, data_mov: datetime, venda_id: int) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_movimentacao_estoque_venda.sql")
        query = open(query_path).read()

        result = self.session.execute(text(query), {
            "produto_id": produto_id,
            "quantidade": quantidade,
            "operacao_id": 5,
            "data_mov": data_mov,
            "venda_id": venda_id
        }).fetchone()

        self.session.commit()
        return result[0] if result else -1
    
    def registrar_entrada_por_devolucao(
        self,
        produto_id: int,
        quantidade: int,
        data_mov: datetime,
        venda_id: Optional[int] = None
    ) -> Optional[int]:
        query_path = os.path.join(QUERIES_FOLDER, "insert_movimentacao_estoque_venda.sql")
        query = open(query_path).read()

        print("======== QUERY LIDA ========")
        print(repr(query))  # Verificar escapes corretamente
        print("======== FIM QUERY =========")

        result = self.session.execute(
            text(query),
            {
                "produto_id": produto_id,
                "quantidade": quantidade,
                "operacao_id": 7,
                "data_mov": data_mov,
                "venda_id": venda_id,
            }
        ).fetchone()

        self.session.commit()
        return result[0] if result else None

    def atualizar_venda(self, venda_id: int, venda: VendaUpdate, total: float) -> None:
        query_path = os.path.join(QUERIES_FOLDER, "update_vendas.sql")
        query = open(query_path).read()

        self.session.execute(text(query), {
            "venda_id": venda_id,
            "cliente_id": venda.cliente_id,
            "data_venda": venda.data_venda or datetime.now(),
            "total": total,
            "forma_pagamento_id": venda.forma_pagamento_id,
            "observacao": venda.observacao,
            "data_pagamento": venda.data_pagamento
        })
        self.session.commit()

    def confirmar_pagamento(self, venda_id: int) -> None:
        """Confirma manualmente o pagamento de uma venda (pago = true). Não afeta o estoque."""
        query_path = os.path.join(QUERIES_FOLDER, "update_pagamento.sql")
        query = open(query_path).read()

        self.session.execute(text(query), {"venda_id": venda_id})
        self.session.commit()

    def cancelar_venda(self, venda_id: int, itens: list[ItemVendaResponse]) -> None:
        """Cancela a venda e devolve os itens ao estoque."""
        
        # 1. Devolve os itens ao estoque (entrada)
        for item in itens:
            self.registrar_entrada_por_devolucao(
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                data_mov=datetime.now()
            )

        # 2. Marca a venda como cancelada usando a query externa
        query_path = os.path.join(QUERIES_FOLDER, "cancelar_venda.sql")
        query = open(query_path).read()

        self.session.execute(text(query), {"venda_id": venda_id})
        self.session.commit()

    def deletar_itens_da_venda(self, venda_id: int) -> None:
        query = "DELETE FROM ambrosia.itens_venda WHERE venda_id = :venda_id"
        self.session.execute(text(query), {"venda_id": venda_id})
        self.session.commit()    

    def buscar_venda_por_id(self, venda_id: int) -> Optional[VendaResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_venda_por_id.sql")
        query = open(query_path).read()

        row = self.session.execute(text(query), {"venda_id": venda_id}).fetchone()
        return VendaResponse(**dict(row._mapping)) if row else None   
    
    def deletar_movimentacoes_por_venda(self, venda_id: int) -> None:
        query_path = os.path.join(QUERIES_FOLDER, "delete_movimentacao.sql")
        query = open(query_path).read()

        self.session.execute(text(query), {"venda_id": venda_id})
        self.session.commit()

    def listar_vendas_nao_pagas(self) -> list[VendaResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_vendas_nao_pagas.sql")
        query = open(query_path).read()

        rows = self.session.execute(text(query)).fetchall()
        return [VendaResponse(**dict(row._mapping)) for row in rows]  