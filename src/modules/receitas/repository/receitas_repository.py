import os
from typing import Optional, List, Any
import json
from decimal import ROUND_FLOOR
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session

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

    def _precheck_itens_producao(self, receita_id: int, quantidade, is_meia_receita: bool) -> List[dict]:
        check_path = os.path.join(QUERIES_FOLDER, "select_check_itens_producao_para_receita.sql")
        with open(check_path, "r", encoding="utf-8") as f:
            check_sql = f.read()
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

    def inserir_receita(self, data: ReceitaCreate) -> int:
        query_path = os.path.join(QUERIES_FOLDER, "insert_receita.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        params = data.to_sql_params()
        if not params.get("itens"):
            params["itens"] = "[]"
        row = self.session.execute(text(query), params).fetchone()
        self.session.commit()
        return int(row[0]) if row else -1

    def fazer_receita(self, data: FazerReceitaInput) -> FazerReceitaResponse:
        faltas = self._precheck_itens_producao(data.receita_id, data.quantidade, bool(data.is_meia_receita))
        if faltas:
            raise EstoqueInsuficienteError(faltas)

        fazer_receita_path = os.path.join(QUERIES_FOLDER, "fazer_receita.sql")
        upd_quant_path = os.path.join(QUERIES_FOLDER, "update_mov_receita_quantidades.sql")
        recalc_path = os.path.join(QUERIES_FOLDER, "recalcular_custos_receita_por_rec.sql")
        upd_preco_path = os.path.join(QUERIES_FOLDER, "update_mov_prod_preco_custo_unit.sql")

        with open(fazer_receita_path, "r", encoding="utf-8") as f:
            fazer_sql = f.read()
        with open(upd_quant_path, "r", encoding="utf-8") as f:
            upd_quant_sql = f.read()
        with open(recalc_path, "r", encoding="utf-8") as f:
            recalc_sql = f.read()
        with open(upd_preco_path, "r", encoding="utf-8") as f:
            upd_preco_sql = f.read()

        qtd_int = int(data.quantidade.to_integral_value(rounding=ROUND_FLOOR))

        try:
            row = self.session.execute(
                text(fazer_sql),
                {
                    "receita_id": data.receita_id,
                    "qtd_prod": qtd_int,
                    "is_meia": bool(data.is_meia_receita),
                    "preco_venda": data.preco_venda,
                    "data_mov": data.data_mov,
                },
            ).mappings().one()

            rec_id = int(row["rec_id"])
            produto_mov_id = int(row["produto_mov_id"])
            mp_qtd = float(row["mp_qtd_consumida"] or 0)
            it_qtd = int(row["it_qtd_consumida"] or 0)
            op_tag = row["op_tag"]

            self.session.execute(
                text(upd_quant_sql),
                {"rec_id": rec_id, "mp_qtd": mp_qtd, "it_qtd": it_qtd},
            )
            self.session.execute(
                text(recalc_sql),
                {"rec_id": rec_id, "op_tag": op_tag},
            )
            self.session.execute(
                text(upd_preco_sql),
                {"produto_mov_id": produto_mov_id},
            )
            self.session.commit()

            return FazerReceitaResponse(
                produto_mov_id=produto_mov_id,
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
        query_path = os.path.join(QUERIES_FOLDER, "select_receitas_e_itens.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            sql = f.read()
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
        query_path = os.path.join(QUERIES_FOLDER, "select_receitas_com_precos.sql")
        with open(query_path, "r", encoding="utf-8") as f:
            sql = f.read()
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
