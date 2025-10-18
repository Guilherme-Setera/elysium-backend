from datetime import datetime, date
from typing import Optional

from src.modules.vendas.dto.dto import (
    VendaCreate,
    VendaUpdate,
    VendaResponse,
    ItemVendaResponse,
    RegistrarPagamentoDTO,
)
from src.modules.vendas.repository.vendas_repository import VendaRepository
from src.modules.estoque.repository.estoque_repository import EstoqueRepository


class RegistrarVendaUseCase:
    def __init__(self, venda_repo: VendaRepository, estoque_repo: EstoqueRepository):
        self.venda_repo = venda_repo
        self.estoque_repo = estoque_repo

    def executar(self, venda: VendaCreate) -> int:
        data_ref: date = (venda.data_venda or datetime.now()).date()
        estoque_atual = self.estoque_repo.listar_estoque_atual(data_referencia=data_ref)
        saldos = {e.produto_id: e.saldo_estoque for e in estoque_atual}

        for item in venda.itens:
            saldo = saldos.get(item.produto_id, 0)
            if item.quantidade > saldo:
                raise ValueError(f"Estoque insuficiente para o produto ID {item.produto_id}.")

        total = sum(item.quantidade * item.preco_unitario for item in venda.itens)

        venda_id = self.venda_repo.inserir_venda(venda, total)

        for item in venda.itens:
            self.venda_repo.inserir_item_venda(venda_id, item)
            self.venda_repo.registrar_saida_por_venda(
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                data_mov=venda.data_venda or datetime.now(),
                venda_id=venda_id,
            )

        return venda_id


class AtualizarVendaUseCase:
    def __init__(self, venda_repo: VendaRepository):
        self.venda_repo = venda_repo

    def executar(self, venda_id: int, nova_venda: VendaUpdate) -> None:
        venda_original = self.venda_repo.buscar_venda_por_id(venda_id)
        if not venda_original:
            raise ValueError(f"Venda com ID {venda_id} não encontrada.")

        itens_antigos = self.venda_repo.buscar_itens_por_venda_id(venda_id)
        self.venda_repo.deletar_movimentacoes_por_venda(venda_id)
        self.venda_repo.deletar_itens_da_venda(venda_id)

        total = sum(item.quantidade * item.preco_unitario for item in nova_venda.itens)
        self.venda_repo.atualizar_venda(venda_id, nova_venda, total)

        for item in nova_venda.itens:
            self.venda_repo.inserir_item_venda(venda_id, item)
            self.venda_repo.registrar_saida_por_venda(
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                data_mov=nova_venda.data_venda or datetime.now(),
                venda_id=venda_id,
            )


class ConfirmarPagamentoVendaUseCase:
    def __init__(self, venda_repo: VendaRepository):
        self.venda_repo = venda_repo

    def executar(self, venda_id: int) -> None:
        self.venda_repo.confirmar_pagamento(venda_id)


class CancelarVendaUseCase:
    def __init__(self, venda_repo: VendaRepository):
        self.venda_repo = venda_repo

    def executar(self, venda_id: int) -> None:
        itens = self.venda_repo.buscar_itens_por_venda_id(venda_id)
        self.venda_repo.cancelar_venda(venda_id, itens)


class ListarVendasUseCase:
    def __init__(self, venda_repo: VendaRepository) -> None:
        self.venda_repo = venda_repo

    def executar(self) -> list[VendaResponse]:
        return self.venda_repo.buscar_vendas()


class ListarItensVendaUseCase:
    def __init__(self, venda_repo: VendaRepository):
        self.venda_repo = venda_repo

    def executar(self, venda_id: int) -> list[ItemVendaResponse]:
        itens = self.venda_repo.buscar_itens_por_venda_id(venda_id)
        return itens


class BuscarVendaComItensUseCase:
    def __init__(self, venda_repo: VendaRepository):
        self.venda_repo = venda_repo

    def executar(self, venda_id: int) -> Optional[dict]:
        venda = self.venda_repo.buscar_venda_por_id(venda_id)
        if not venda:
            return None
        itens = self.venda_repo.buscar_itens_por_venda_id(venda_id)
        return {"venda": venda, "itens": itens}


class ListarVendasNaoPagasUseCase:
    def __init__(self, venda_repo: VendaRepository):
        self.venda_repo = venda_repo

    def executar(self) -> list[VendaResponse]:
        return self.venda_repo.listar_vendas_nao_pagas()


class RegistrarPagamentoVendaUseCase:
    def __init__(self, venda_repo: VendaRepository):
        self.venda_repo = venda_repo

    def executar(self, data: RegistrarPagamentoDTO) -> bool:
        return self.venda_repo.registrar_pagamento_venda(data)
