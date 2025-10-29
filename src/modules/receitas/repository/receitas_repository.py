import os
from typing import Optional, List, Any, Dict
from decimal import Decimal
from fastapi.encoders import jsonable_encoder
import json
from datetime import datetime
from sqlalchemy.sql import text, bindparam
from sqlalchemy.orm import Session
from sqlalchemy import Integer, Numeric

from src.modules.receitas.abc_classes.receitas_abc import IReceitasRepository
from src.modules.receitas.dto.dto_receitas import (
    ReceitaCreate,
    ReceitaResponse,
    ReceitaItemMateriaPrimaResponse,
    ReceitaItemProducaoResponse,
    FazerReceitaInput,
    FazerReceitaResponse,
    ReceitaMovimentacaoResponse,
)

BASE_DIR: str = os.path.dirname(__file__)
QUERIES_FOLDER: str = os.path.join(BASE_DIR, "queries", "postgres")


def _ensure_list_of_dict(x: Any) -> list[dict]:
    if x is None:
        return []
    if isinstance(x, str):
        try:
            parsed = json.loads(x)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []
    return x if isinstance(x, list) else []


class EstoqueInsuficienteError(Exception):
    def __init__(self, faltas: List[dict]):
        self.faltas = faltas
        nomes = ", ".join(
            f"{f['nome']} (estoque {f['estoque_atual']}, precisa {f['consumo_necessario']})"
            for f in faltas
        )
        super().__init__(f"Estoque insuficiente: {nomes}")


class ReceitasRepository(IReceitasRepository):
    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def _read_query(self, name: str) -> str:
        path = os.path.join(QUERIES_FOLDER, name)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _precheck_itens_producao(self, receita_id: int, quantidade, is_meia_receita: bool) -> List[dict]:
        check_sql = self._read_query("select_check_itens_producao_para_receita.sql")
        rows = self.session.execute(
            text(check_sql),
            {"receita_id": receita_id, "quantidade": quantidade, "is_meia_receita": is_meia_receita},
        ).mappings().fetchall()
        faltas: List[dict] = []
        for r in rows:
            estoque_atual = float(r["estoque_atual"] or 0)
            consumo = float(r["consumo_necessario"] or 0)
            if estoque_atual < consumo:
                faltas.append(
                    {
                        "item_id": r["item_id"],
                        "nome": r["nome"],
                        "estoque_atual": estoque_atual,
                        "consumo_necessario": consumo,
                    }
                )
        return faltas

    def _precheck_itens_producao_explicit(self, itens_producao: List[Dict[str, Any]]) -> List[dict]:
        if not itens_producao:
            return []
        ids = [int(it["item_producao_id"]) for it in itens_producao if "item_producao_id" in it]
        if not ids:
            return []
        saldo_sql = self._read_query("select_saldo_itens_producao_por_ids.sql")
        rows = self.session.execute(text(saldo_sql), {"ids": ids}).mappings().fetchall()
        estoque_map = {int(r["item_id"]): {"nome": r["nome"], "estoque_atual": float(r["estoque_atual"] or 0)} for r in rows}
        faltas: List[dict] = []
        for it in itens_producao:
            item_id = int(it["item_producao_id"])
            qtd = int(it["quantidade_itens"])
            est = estoque_map.get(item_id, {"nome": f"item {item_id}", "estoque_atual": 0.0})
            if est["estoque_atual"] < qtd:
                faltas.append(
                    {
                        "item_id": item_id,
                        "nome": est["nome"],
                        "estoque_atual": est["estoque_atual"],
                        "consumo_necessario": float(qtd),
                    }
                )
        return faltas

    def inserir_receita(self, data: ReceitaCreate) -> int:
        query = self._read_query("insert_receita.sql")
        params = data.to_sql_params()
        if not params.get("itens"):
            params["itens"] = "[]"
        row = self.session.execute(text(query), params).fetchone()
        self.session.commit()
        return int(row[0]) if row else -1

    def fazer_receita(self, data: FazerReceitaInput) -> FazerReceitaResponse:
        fazer_sql = self._read_query("fazer_receita.sql")
        recalc_sql = self._read_query("recalcular_custos_receita_por_rec.sql")
        upd_preco_sql = self._read_query("update_mov_prod_preco_custo_unit.sql")
        upd_quant_sql = self._read_query("update_mov_receita_quantidades.sql")
        upd_custos_sql = self._read_query("update_mov_receita_custos.sql")

        consumos_json = json.dumps(jsonable_encoder(data.consumos or {}))
        produto_final_json = json.dumps(jsonable_encoder(data.produto_final)) if data.produto_final else None

        custo_mp_override = None
        custo_itens_override = None

        if data.consumos:
            mp = data.consumos.get("materias_primas") or []
            it = data.consumos.get("itens_producao") or []
            soma_mp = sum(Decimal(str(x.get("custo_total", 0))) for x in mp if x.get("custo_total") is not None)
            soma_it = sum(Decimal(str(x.get("custo_total", 0))) for x in it if x.get("custo_total") is not None)
            if soma_mp > 0:
                custo_mp_override = soma_mp
            if soma_it > 0:
                custo_itens_override = soma_it

        preco_venda_final = (
            (data.produto_final.preco_venda if data.produto_final else None)
            if (data.produto_final and data.produto_final.preco_venda is not None)
            else data.preco_venda
        )

        try:
            row = self.session.execute(
                text(fazer_sql),
                {
                    "receita_id": data.receita_id,
                    "data_mov": data.data_mov,
                    "preco_venda": preco_venda_final,
                    "consumos_json": consumos_json,
                    "produto_final_json": produto_final_json,
                },
            ).mappings().one()

            rec_id = int(row["rec_id"])
            produto_mov_id = int(row["produto_mov_id"]) if row.get("produto_mov_id") is not None else -1
            op_tag = row["op_tag"]
            mp_qtd = float(row.get("mp_qtd_consumida") or 0)
            it_qtd = int(row.get("it_qtd_consumida") or 0)

            self.session.execute(text(upd_quant_sql), {"rec_id": rec_id, "mp_qtd": mp_qtd, "it_qtd": it_qtd})

            if (custo_mp_override is not None) or (custo_itens_override is not None):
                stmt = text(upd_custos_sql).bindparams(
                    bindparam("rec_id", type_=Integer),
                    bindparam("custo_mp", type_=Numeric(12, 4)),
                    bindparam("custo_it", type_=Numeric(12, 4)),
                )
                self.session.execute(
                    stmt,
                    {
                        "rec_id": rec_id,
                        "custo_mp": custo_mp_override,      # pode ser Decimal ou None
                        "custo_it": custo_itens_override,    # pode ser Decimal ou None
                    },
                )
            else:
                self.session.execute(text(recalc_sql), {"rec_id": rec_id, "op_tag": op_tag})

            if produto_mov_id and produto_mov_id > 0:
                self.session.execute(text(upd_preco_sql), {"produto_mov_id": produto_mov_id})

            self.session.commit()

            return FazerReceitaResponse(
                produto_mov_id=produto_mov_id if produto_mov_id > 0 else -1,
                consumos_reg=int(round(mp_qtd)) + int(it_qtd),
                produto_preco_id=-1,
            )
        except Exception:
            self.session.rollback()
            raise

    def listar_receitas(
        self,
        receita_id: Optional[int] = None,
        apenas_ativas: Optional[bool] = None,
        produto_id: Optional[int] = None,
    ) -> List[ReceitaResponse]:
        sql = self._read_query("select_receitas_e_itens.sql")
        rows = (
            self.session.execute(
                text(sql),
                {"receita_id": receita_id, "produto_id": produto_id},
            )
            .mappings()
            .fetchall()
        )
        receitas: List[ReceitaResponse] = []
        for r in rows:
            mp_list = _ensure_list_of_dict(r.get("materias_primas"))
            ip_list = _ensure_list_of_dict(r.get("itens_producao"))
            receitas.append(
                ReceitaResponse(
                    id=int(r["id"]),
                    nome=r["nome"],
                    descricao=r.get("descricao"),
                    ativo=True,
                    meia_receita=False,
                    produto_id=int(r["produto_id"]),
                    produto_nome=r.get("produto_nome"),
                    materias_primas=[
                        ReceitaItemMateriaPrimaResponse(
                            materia_prima_id=int(mp["materia_prima_id"]),
                            nome_materia_prima=mp["nome_materia_prima"],
                            quantidade_unidade=1.0,
                            quantidade_medida=float(mp.get("quantidade") or 0.0),
                            is_grama=mp.get("is_grama"),
                        )
                        for mp in mp_list
                    ],
                    itens_producao=[
                        ReceitaItemProducaoResponse(
                            item_id=int(ip["item_producao_id"]),
                            nome_item=ip["nome_item"],
                            quantidade=float(ip.get("quantidade_itens") or 0.0),
                            unidade=ip.get("unidade", "un") or "un",
                            descartavel=bool(ip.get("descartavel", True)),
                        )
                        for ip in ip_list
                    ],
                )
            )
        return receitas

    def listar_receitas_com_precos(
        self,
        receita_id: Optional[int] = None,
        produto_id: Optional[int] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
    ) -> List[ReceitaMovimentacaoResponse]:
        sql = self._read_query("select_receitas_com_precos.sql")
        rows = (
            self.session.execute(
                text(sql),
                {
                    "receita_id": receita_id,
                    "produto_id": produto_id,
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                },
            )
            .mappings()
            .fetchall()
        )
        result: List[ReceitaMovimentacaoResponse] = []
        for r in rows:
            result.append(
                ReceitaMovimentacaoResponse(
                    id=int(r["id"]),
                    receita_id=int(r["receita_id"]),
                    receita_nome=r["receita_nome"],
                    produto_id=int(r["produto_id"]),
                    produto_nome=r["produto_nome"],
                    data_execucao=r["data_execucao"],
                    quantidade_materia_prima=r["quantidade_materia_prima"],
                    custo_materia_prima=r["custo_materia_prima"],
                    quantidade_itens_producao=int(r["quantidade_itens_producao"]),
                    custo_itens_producao=r["custo_itens_producao"],
                    produto_estoque_id=int(r["produto_estoque_id"]) if r["produto_estoque_id"] is not None else None,
                    quantidade_produto=int(r["quantidade_produto"]),
                    is_meia_receita=bool(r["is_meia_receita"]),
                    custo_total_producao=r["custo_total_producao"],
                    custo_unitario_produto=r["custo_unitario_produto"],
                )
            )
        return result
