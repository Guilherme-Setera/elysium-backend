import os
import json
from datetime import datetime, date
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.modules.vendas.dto.dto import (
    VendaCreate,
    ItemVendaCreate,
    VendaResponse,
    ItemVendaResponse,
    VendaUpdate,
    RegistrarPagamentoDTO,
    VendaHistoricoConsolidadoFiltro,
    VendaHistoricoConsolidadoItem,
    VendaHistoricoMateriaPrima,
    VendaHistoricoItemProducao,
)
from src.modules.vendas.abc_classes.vendas_abc import IVendaRepository

BASE_DIR = os.path.dirname(__file__)
QUERIES_FOLDER = os.path.join(BASE_DIR, "queries", "postgres")


class VendaRepository(IVendaRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def inserir_venda(self, venda: VendaCreate, total: float) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_venda.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()

        data_venda = venda.data_venda or datetime.now()
        data_pagamento = venda.data_pagamento
        a_prazo = bool(venda.a_prazo or False)

        if a_prazo:
            valor_pago = float(venda.valor_pago or 0.0)
            pago = False
        else:
            if data_pagamento and total > 0:
                valor_pago = float(total)
                pago = True
            else:
                valor_pago = float(venda.valor_pago or 0.0)
                pago = False

        row = self.session.execute(
            text(query),
            {
                "cliente_id": venda.cliente_id,
                "forma_pagamento_id": venda.forma_pagamento_id,
                "data_venda": data_venda,
                "data_pagamento": data_pagamento,
                "total": total,
                "observacao": venda.observacao,
                "valor_pago": valor_pago,
                "a_prazo": a_prazo,
                "pago": pago,
                "frete": float(venda.frete or 0.0),
                "data_entrega": venda.data_entrega,
                "codigo_rastreio": venda.codigo_rastreio,
            },
        ).fetchone()

        self.session.commit()
        return int(row[0]) if row else -1

    def atualizar_venda(self, venda_id: int, venda: VendaUpdate, total: float) -> None:
        query_path = os.path.join(QUERIES_FOLDER, "update_vendas.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()

        self.session.execute(
            text(query),
            {
                "venda_id": venda_id,
                "cliente_id": venda.cliente_id,
                "data_venda": venda.data_venda or datetime.now(),
                "total": total,
                "forma_pagamento_id": venda.forma_pagamento_id,
                "observacao": venda.observacao,
                "data_pagamento": venda.data_pagamento,
                "frete": None if venda.frete is None else float(venda.frete),
                "data_entrega": venda.data_entrega,
                "codigo_rastreio": venda.codigo_rastreio,
                "a_prazo": venda.a_prazo,
                "valor_pago": venda.valor_pago,
            },
        )
        self.session.commit()

    def confirmar_pagamento(self, venda_id: int) -> None:
        query_path = os.path.join(QUERIES_FOLDER, "update_pagamento.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        self.session.execute(text(query), {"venda_id": venda_id})
        self.session.commit()

    def registrar_pagamento_venda(self, data: RegistrarPagamentoDTO) -> bool:
        query_path = os.path.join(QUERIES_FOLDER, "update_venda_registrar_pagamento.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()

        result = self.session.execute(
            text(query),
            {
                "venda_id": data.venda_id,
                "valor_recebido": data.valor_recebido,
            },
        )
        self.session.commit()
        return getattr(result, "rowcount", 0) > 0

    def cancelar_venda(self, venda_id: int, itens: list[ItemVendaResponse]) -> None:
        for item in itens:
            self.registrar_entrada_por_devolucao(
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                data_mov=datetime.now(),
                venda_id=venda_id,
            )
        query_path = os.path.join(QUERIES_FOLDER, "cancelar_venda.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        self.session.execute(text(query), {"venda_id": venda_id})
        self.session.commit()

    def buscar_vendas(self) -> list[VendaResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_vendas.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()

        rows = self.session.execute(text(query)).mappings().all()
        vendas: list[VendaResponse] = []

        for row in rows:
            data = dict(row)

            for k in ("total", "valor_pago", "frete"):
                if k in data and data[k] is not None:
                    data[k] = float(data[k])

            up = data.get("ultima_parcela_paga")
            if isinstance(up, datetime):
                data["ultima_parcela_paga"] = up.date()
            elif isinstance(up, str):
                data["ultima_parcela_paga"] = date.fromisoformat(up)

            dpp = data.get("datas_parcelas_pagas")
            if dpp is not None:
                if isinstance(dpp, str):
                    s = dpp.strip("{}").strip()
                    itens = [x for x in s.split(",") if x] if s else []
                    data["datas_parcelas_pagas"] = [date.fromisoformat(x) for x in itens]
                elif isinstance(dpp, list):
                    norm: list[date] = []
                    for x in dpp:
                        if isinstance(x, datetime):
                            norm.append(x.date())
                        elif isinstance(x, date):
                            norm.append(x)
                        elif isinstance(x, str):
                            norm.append(date.fromisoformat(x))
                    data["datas_parcelas_pagas"] = norm

            parcelas = data.get("parcelas")
            if parcelas is not None:
                if isinstance(parcelas, str):
                    try:
                        parcelas = json.loads(parcelas)
                    except Exception:
                        parcelas = None
                if isinstance(parcelas, list):
                    norm_parcelas = []
                    for p in parcelas:
                        venc = p.get("vencimento")
                        pago_em = p.get("pago_em")
                        valor = p.get("valor")
                        valor_pago = p.get("valor_pago")

                        if isinstance(venc, str):
                            venc = date.fromisoformat(venc)
                        elif isinstance(venc, datetime):
                            venc = venc.date()

                        if isinstance(pago_em, str):
                            pago_em = date.fromisoformat(pago_em)
                        elif isinstance(pago_em, datetime):
                            pago_em = pago_em.date()

                        if valor is not None:
                            valor = float(valor)
                        if valor_pago is not None:
                            valor_pago = float(valor_pago)

                        norm_parcelas.append(
                            {
                                "numero": p.get("numero"),
                                "vencimento": venc,
                                "valor": valor or 0.0,
                                "valor_pago": valor_pago,
                                "pago_em": pago_em,
                            }
                        )
                    data["parcelas"] = norm_parcelas

            vendas.append(VendaResponse(**data))

        return vendas

    def buscar_venda_por_id(self, venda_id: int) -> Optional[VendaResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_venda_por_id.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        row = self.session.execute(text(query), {"venda_id": venda_id}).mappings().one_or_none()
        if row:
            d = dict(row)
            for k in ("total", "valor_pago", "frete"):
                if k in d and d[k] is not None:
                    d[k] = float(d[k])
            return VendaResponse(**d)
        return None

    def listar_vendas_nao_pagas(self) -> list[VendaResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_vendas_nao_pagas.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        rows = self.session.execute(text(query)).mappings().all()
        out: list[VendaResponse] = []
        for r in rows:
            d = dict(r)
            for k in ("total", "valor_pago", "frete"):
                if k in d and d[k] is not None:
                    d[k] = float(d[k])
            out.append(VendaResponse(**d))
        return out

    def inserir_item_venda(self, venda_id: int, item: ItemVendaCreate) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_item_venda.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        row = self.session.execute(
            text(query),
            {
                "venda_id": venda_id,
                "produto_id": item.produto_id,
                "quantidade": item.quantidade,
                "preco_unitario": item.preco_unitario,
            },
        ).fetchone()
        self.session.commit()
        return int(row[0]) if row else -1

    def buscar_itens_por_venda_id(self, venda_id: int) -> list[ItemVendaResponse]:
        query_path = os.path.join(QUERIES_FOLDER, "select_itens_venda_por_venda_id.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        rows = self.session.execute(text(query), {"venda_id": venda_id}).mappings().all()
        return [ItemVendaResponse(**row) for row in rows]

    def deletar_itens_da_venda(self, venda_id: int) -> None:
        query = "DELETE FROM elysium.itens_venda WHERE venda_id = :venda_id"
        self.session.execute(text(query), {"venda_id": venda_id})
        self.session.commit()

    def registrar_saida_por_venda(self, produto_id: int, quantidade: int, data_mov: datetime, venda_id: int) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_movimentacao_estoque_venda.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        row = self.session.execute(
            text(query),
            {
                "produto_id": produto_id,
                "quantidade": quantidade,
                "operacao_id": 5,
                "data_mov": data_mov,
                "venda_id": venda_id,
            },
        ).fetchone()
        self.session.commit()
        return int(row[0]) if row else -1

    def registrar_entrada_por_devolucao(
        self,
        produto_id: int,
        quantidade: int,
        data_mov: datetime,
        venda_id: Optional[int] = None,
    ) -> Optional[int]:
        query_path = os.path.join(QUERIES_FOLDER, "insert_movimentacao_estoque_venda.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        row = self.session.execute(
            text(query),
            {
                "produto_id": produto_id,
                "quantidade": quantidade,
                "operacao_id": 7,
                "data_mov": data_mov,
                "venda_id": venda_id,
            },
        ).fetchone()
        self.session.commit()
        return int(row[0]) if row else None

    def deletar_movimentacoes_por_venda(self, venda_id: int) -> None:
        query_path = os.path.join(QUERIES_FOLDER, "delete_movimentacao.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        self.session.execute(text(query), {"venda_id": venda_id})
        self.session.commit()

    def desabilitar_triggers_recalculo(self) -> None:
        """Desabilita temporariamente os triggers de recálculo durante inserção em lote de itens."""
        self.session.execute(text("SET session_replication_role = replica;"))

    def habilitar_triggers_recalculo(self) -> None:
        """Reabilita os triggers de recálculo após inserção em lote de itens."""
        self.session.execute(text("SET session_replication_role = DEFAULT;"))

    def listar_historico_consolidado(
        self, filtro: VendaHistoricoConsolidadoFiltro
    ) -> list[VendaHistoricoConsolidadoItem]:
        """Retorna o histórico consolidado de vendas com custos e lucros."""
        query_path = os.path.join(QUERIES_FOLDER, "select_historico_consolidado.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()

        rows = self.session.execute(
            text(query),
            {
                "data_de": filtro.data_de,
                "data_ate": filtro.data_ate,
                "usar_data": filtro.usar_data or "data_venda",
            },
        ).mappings().all()

        resultado: list[VendaHistoricoConsolidadoItem] = []

        for row in rows:
            data = dict(row)

            # Converter valores numéricos
            for k in ("valor_total", "valor_pago", "valor_custo", "lucro"):
                if k in data and data[k] is not None:
                    data[k] = float(data[k])

            # Processar matérias-primas JSON
            if data.get("materias_primas"):
                materias = data["materias_primas"]
                if isinstance(materias, str):
                    materias = json.loads(materias)
                if materias and isinstance(materias, list):
                    data["materias_primas"] = [
                        VendaHistoricoMateriaPrima(
                            nome=mp.get("nome") or "",
                            quantidade=float(mp["quantidade"]) if mp.get("quantidade") is not None else None,
                            valor=float(mp["valor"]) if mp.get("valor") is not None else 0.0,
                        )
                        for mp in materias if mp  # Filtrar matérias None
                    ]
                else:
                    data["materias_primas"] = []
            else:
                data["materias_primas"] = []

            # Processar itens de produção JSON
            if data.get("itens_producao"):
                itens = data["itens_producao"]
                if isinstance(itens, str):
                    itens = json.loads(itens)
                if itens and isinstance(itens, list):
                    data["itens_producao"] = [
                        VendaHistoricoItemProducao(
                            nome=item.get("nome") or "",
                            quantidade=int(item["quantidade"]) if item.get("quantidade") is not None else None,
                            valor=float(item["valor"]) if item.get("valor") is not None else 0.0,
                        )
                        for item in itens if item  # Filtrar itens None
                    ]
                else:
                    data["itens_producao"] = []
            else:
                data["itens_producao"] = []

            resultado.append(VendaHistoricoConsolidadoItem(**data))

        return resultado
