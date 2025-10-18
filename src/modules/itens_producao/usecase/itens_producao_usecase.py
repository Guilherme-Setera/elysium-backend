# src/modules/itens_producao/usecases.py
from __future__ import annotations

from typing import Optional
from datetime import date
from src.modules.itens_producao.abc_classes.abc_classes import IItensProducaoRepository
from src.modules.itens_producao.dto.dto_itens_producao import (
    ItemConsumoCreate,
    ItemConsumoUpdate,
    ItemConsumoResponse,
    MovimentacaoItemProducaoEntradaCreate,
    MovimentacaoItemProducaoResponse,
    EstoqueAtualItemProducaoResponse,
    
)


class CadastrarItemConsumo:
    def __init__(self, repo: IItensProducaoRepository) -> None:
        self.repo = repo

    def __call__(self, data: ItemConsumoCreate) -> int:
        nome = (data.nome or "").strip()
        if not nome:
            raise ValueError("O nome do item de consumo é obrigatório.")

        estoque_minimo = getattr(data, "estoque_minimo", None)
        if estoque_minimo is not None and estoque_minimo < 0:
            raise ValueError("O estoque mínimo deve ser maior ou igual a 0.")

        payload = ItemConsumoCreate(
            nome=nome,
            ativo=bool(getattr(data, "ativo", True)),
            estoque_minimo=estoque_minimo,
        )
        return self.repo.cadastrar_item_consumo(payload)


class AtualizarItemConsumo:
    def __init__(self, repo: IItensProducaoRepository) -> None:
        self.repo = repo

    def __call__(self, item_consumo_id: int, data: ItemConsumoUpdate) -> int:
        if not isinstance(item_consumo_id, int) or item_consumo_id <= 0:
            raise ValueError("item_consumo_id inválido.")

        if data.nome is not None:
            nome = data.nome.strip()
            if not nome:
                raise ValueError("O nome do item de consumo não pode ser vazio.")

        estoque_minimo = getattr(data, "estoque_minimo", None)
        if estoque_minimo is not None and estoque_minimo < 0:
            raise ValueError("O estoque mínimo deve ser maior ou igual a 0.")

        payload = ItemConsumoUpdate(
            nome=(data.nome.strip() if data.nome is not None else None),
            ativo=getattr(data, "ativo", None),
            estoque_minimo=estoque_minimo,
            limpar_estoque_minimo=getattr(data, "limpar_estoque_minimo", None),
        )

        tem_alteracao = any(
            v is not None
            for v in (payload.nome, payload.ativo, payload.estoque_minimo, payload.limpar_estoque_minimo)
        )
        if not tem_alteracao:
            raise ValueError("Nenhuma alteração informada para atualização.")

        return self.repo.atualizar_item_consumo(item_consumo_id, payload)


class DesativarItemConsumo:
    def __init__(self, repo: IItensProducaoRepository) -> None:
        self.repo = repo

    def __call__(self, item_consumo_id: int) -> int:
        if not isinstance(item_consumo_id, int) or item_consumo_id <= 0:
            raise ValueError("item_consumo_id inválido.")
        return self.repo.desativar_item_consumo(item_consumo_id)


class ListarItensProducao:
    def __init__(self, repo: IItensProducaoRepository) -> None:
        self.repo = repo

    def __call__(self, somente_ativos: Optional[bool] = None) -> list[ItemConsumoResponse]:
        rows = self.repo.listar_itens_producao(somente_ativos)
        return [ItemConsumoResponse(**r) for r in rows]


class RegistrarEntradaItemProducao:
    def __init__(self, repo: IItensProducaoRepository) -> None:
        self.repo = repo

    def __call__(self, data: MovimentacaoItemProducaoEntradaCreate) -> int:
        if not isinstance(data.quantidade, int) or data.quantidade < 1:
            raise ValueError("A quantidade deve ser informada e maior que 0.")
        if not isinstance(data.item_consumo_id, int) or data.item_consumo_id <= 0:
            raise ValueError("item_consumo_id inválido.")
        if data.preco_custo is None or data.preco_custo < 0:
            raise ValueError("preco_custo deve ser >= 0.")

        payload = MovimentacaoItemProducaoEntradaCreate(
            item_consumo_id=data.item_consumo_id,
            quantidade=data.quantidade,
            preco_custo=data.preco_custo,
            data_movimentacao=data.data_movimentacao,
            is_ativo=data.is_ativo,
            descricao=(data.descricao or "").strip() or None,
        )
        return self.repo.registrar_entrada_item_producao(payload)


class ListarMovimentacoesItensProducao:
    def __init__(self, repo: IItensProducaoRepository) -> None:
        self.repo = repo

    def __call__(self, dia_limite: date) -> list[MovimentacaoItemProducaoResponse]:
        return self.repo.listar_movimentacoes_itens_producao(dia_limite=dia_limite)
    
class ListarEstoqueAtualItensProducao:
    def __init__(self, repo: IItensProducaoRepository) -> None:
        self.repo = repo

    def __call__(self, data_referencia: date) -> list[EstoqueAtualItemProducaoResponse]:
        return self.repo.listar_estoque_atual_itens_producao(data_referencia) 