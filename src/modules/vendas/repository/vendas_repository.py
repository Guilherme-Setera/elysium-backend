import os
from datetime import date
from decimal import Decimal
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.modules.vendas.dto.dto import (
    PainelResumoResponse,
    VendaListagemResponse,
    VendaResponse,
    ItemVendaResponse,
    VendaUpdate,
    ResumoVendasPorData,
    RelatorioDetalhadoProduto,
    LogVendaResponse,
    VendaCreate
)
from src.modules.vendas.abc_classes.vendas_abc import IVendasRepository


QUERIES_FOLDER = os.path.join(os.path.dirname(__file__), "queries", "postgres")


def carregar_query(nome_arquivo: str) -> str:
    caminho = os.path.join(QUERIES_FOLDER, nome_arquivo)
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()


class VendasRepository(IVendasRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar_vendas(
        self,
        cliente_id: Optional[int],
        data_inicio: Optional[date],
        data_fim: Optional[date],
        forma_pagamento: Optional[str]
    ) -> List[VendaResponse]:
        query = carregar_query("select_vendas_com_itens.sql")
        result = await self.session.execute(
            text(query),
            {
                "cliente_id": cliente_id,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "forma_pagamento": forma_pagamento,
            }
        )
        rows = result.fetchall()

        vendas_dict = {}

        for row in rows:
            venda_id = row.venda_id

            if venda_id not in vendas_dict:
                vendas_dict[venda_id] = VendaResponse(
                    id=row.venda_id,
                    cliente_id=row.cliente_id,
                    data_venda=row.data_venda,
                    total=row.total,
                    forma_pagamento=row.forma_pagamento,
                    itens=[]
                )

            if row.item_id is not None:
                item = ItemVendaResponse(
                    id=row.item_id,
                    produto_id=row.produto_id,
                    quantidade=row.quantidade,
                    preco_unitario=row.preco_unitario,
                    subtotal=row.subtotal,
                    nome_produto=row.nome_produto
                )
                vendas_dict[venda_id].itens.append(item)

        return list(vendas_dict.values())
    
    async def buscar_venda_por_id(self, venda_id: int) -> Optional[VendaResponse]:
        query = carregar_query("select_venda_por_id.sql")
        result = await self.session.execute(
            text(query),
            {"venda_id": venda_id}
        )
        rows = result.fetchall()

        if not rows:
            return None

        row0 = rows[0]

        venda = VendaResponse(
            id=row0.venda_id,
            cliente_id=row0.cliente_id,
            cliente_nome=row0.cliente_nome,
            data_venda=row0.data_venda,
            total=row0.total,
            forma_pagamento=row0.forma_pagamento,
            itens=[]
        )

        for row in rows:
            if row.item_id is not None:
                item = ItemVendaResponse(
                    id=row.item_id,
                    produto_id=row.produto_id,
                    nome_produto=row.nome_produto,
                    quantidade=row.quantidade,
                    preco_unitario=row.preco_unitario,
                    subtotal=row.subtotal
                )
                venda.itens.append(item)

        return venda


    async def atualizar_venda(self, venda_id: int, payload: VendaUpdate) -> None:
        # 1. Buscar total da venda para não sobrescrevê-lo
        result = await self.session.execute(
            text("SELECT total FROM ambrosia.vendas WHERE id = :venda_id"),
            {"venda_id": venda_id}
        )
        row = result.fetchone()
        if not row:
            raise ValueError("Venda não encontrada")

        total = row.total

        # 2. Atualizar
        query = carregar_query("update_venda.sql")
        await self.session.execute(
            text(query),
            {
                "venda_id": venda_id,
                "cliente_id": payload.cliente_id,
                "forma_pagamento": payload.forma_pagamento,
                "total": total
            }
        )

        await self.session.commit()
        
    async def excluir_venda(self, venda_id: int) -> None:
        query = carregar_query("delete_venda.sql")
        await self.session.execute(
            text(query),
            {"venda_id": venda_id}
        )
        await self.session.commit()    

    async def gerar_relatorio_resumo(
        self, data_inicio: date, data_fim: date
    ) -> List[ResumoVendasPorData]:
        query = carregar_query("relatorio_resumo_vendas.sql")
        result = await self.session.execute(
            text(query),
            {"data_inicio": data_inicio, "data_fim": data_fim}
        )
        rows = result.fetchall()

        return [
            ResumoVendasPorData(
                data=row.data,
                total_vendas=row.total_vendas,
                valor_total=row.valor_total
            )
            for row in rows
        ]

    async def gerar_relatorio_detalhado_produtos(
        self, data_inicio: date, data_fim: date
    ) -> List[RelatorioDetalhadoProduto]:
        query = carregar_query("relatorio_detalhado_produtos.sql")
        result = await self.session.execute(
            text(query),
            {"data_inicio": data_inicio, "data_fim": data_fim}
        )
        rows = result.fetchall()

        return [
            RelatorioDetalhadoProduto(
                produto_id=row.produto_id,
                nome_produto=row.nome_produto,
                total_vendido=row.total_vendido,
                total_faturado=row.total_faturado
            )
            for row in rows
        ]
    
    async def registrar_log_alteracao(
        self,
        venda_id: int,
        campo: str,
        valor_anterior: str,
        valor_novo: str,
        usuario: str
    ) -> None:
        query = carregar_query("insert_log_venda.sql")
        await self.session.execute(
            text(query),
            {
                "venda_id": venda_id,
                "campo_alterado": campo,
                "valor_anterior": valor_anterior,
                "valor_novo": valor_novo,
                "usuario_responsavel": usuario
            }
        )
        await self.session.commit()

    async def listar_logs_venda(
        self,
        venda_id: Optional[int],
        data_inicio: Optional[date],
        data_fim: Optional[date]
    ) -> List[LogVendaResponse]:
        query = carregar_query("select_logs_venda.sql")
        result = await self.session.execute(
            text(query),
            {
                "venda_id": venda_id,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
            }
        )
        rows = result.fetchall()

        return [
            LogVendaResponse(
                id=row.id,
                venda_id=row.venda_id,
                campo_alterado=row.campo_alterado,
                valor_anterior=row.valor_anterior,
                valor_novo=row.valor_novo,
                data_alteracao=row.data_alteracao
            )
            for row in rows
        ]    
    
    async def painel_resumo(
        self,
        inicio: date,
        fim: date
    ) -> PainelResumoResponse:
        query = carregar_query("painel_resumo.sql")
        result = await self.session.execute(
            text(query),
            {"inicio": inicio, "fim": fim}
        )
        row = result.fetchone()

        if row is None:
            return PainelResumoResponse(
                total_diario=Decimal("0.00"),
                total_mensal=Decimal("0.00"),
                quantidade_vendas=0
            )

        return PainelResumoResponse(
            total_diario=row.total_diario or Decimal("0.00"),
            total_mensal=row.total_mensal or Decimal("0.00"),
            quantidade_vendas=row.quantidade_vendas or 0
        )
    
    async def registrar_venda(self, payload: VendaCreate) -> int:
        total = sum(
            item.quantidade * item.preco_unitario
            for item in payload.itens
        )

        # 1. Inserir a venda
        query_venda = carregar_query("insert_venda.sql")
        result = await self.session.execute(
            text(query_venda),
            {
                "cliente_id": payload.cliente_id,
                "forma_pagamento": payload.forma_pagamento,
                "total": total
            }
        )
        venda_id = result.scalar_one()

        # 2. Inserir os itens
        query_item = carregar_query("insert_item_venda.sql")

        for item in payload.itens:
            await self.session.execute(
                text(query_item),
                {
                    "venda_id": venda_id,
                    "produto_id": item.produto_id,
                    "quantidade": item.quantidade,
                    "preco_unitario": item.preco_unitario,
                    "subtotal": item.quantidade * item.preco_unitario
                }
            )

        await self.session.commit()
        return venda_id