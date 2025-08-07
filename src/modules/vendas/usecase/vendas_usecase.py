from datetime import datetime, date
from typing import Optional

from src.modules.vendas.dto.dto import (
    VendaCreate,
    VendaUpdate,
    VendaResponse,
    ItemVendaResponse
)
from src.modules.vendas.repository.vendas_repository import VendaRepository
from src.modules.estoque.repository.estoque_repository import EstoqueRepository


class RegistrarVendaUseCase:
    def __init__(self, venda_repo: VendaRepository, estoque_repo: EstoqueRepository):
        self.venda_repo = venda_repo
        self.estoque_repo = estoque_repo

    def executar(self, venda: VendaCreate) -> int:
        print("🟢 [RegistrarVendaUseCase] Iniciando processo de registro de venda")
        data_ref: date = (venda.data_venda or datetime.now()).date()
        print(f"📅 Data da venda: {data_ref}")

        # 1. Buscar saldo de estoque
        print("🔎 Buscando saldo de estoque atual...")
        estoque_atual = self.estoque_repo.listar_estoque_atual(data_referencia=data_ref)
        saldos = {e.produto_id: e.saldo_estoque for e in estoque_atual}
        print(f"📦 Saldos disponíveis: {saldos}")

        # 2. Verificar estoque suficiente
        for item in venda.itens:
            saldo = saldos.get(item.produto_id, 0)
            print(f"🔍 Produto {item.produto_id}: necessário={item.quantidade}, disponível={saldo}")
            if item.quantidade > saldo:
                raise ValueError(f"❌ Estoque insuficiente para o produto ID {item.produto_id}.")

        # 3. Calcular total
        total = sum(item.quantidade * item.preco_unitario for item in venda.itens)
        print(f"💰 Total da venda: R$ {total:.2f}")

        # 4. Definir se já está paga
        # 5. Inserir venda
        print("💾 Inserindo venda...")
        venda_id = self.venda_repo.inserir_venda(venda, total)
        print(f"✅ Venda registrada com ID: {venda_id}")

        # 6. Inserir itens + movimentações
        for item in venda.itens:
            print(f"🧾 Item: produto_id={item.produto_id}, qtd={item.quantidade}")
            self.venda_repo.inserir_item_venda(venda_id, item)

            print(f"📤 Saída no estoque: produto {item.produto_id}")
            self.venda_repo.registrar_saida_por_venda(
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                data_mov=venda.data_venda or datetime.now(),
                venda_id=venda_id
            )

        print("🎉 Venda concluída.")
        return venda_id



class AtualizarVendaUseCase:
    def __init__(self, venda_repo: VendaRepository):
        self.venda_repo = venda_repo

    def executar(self, venda_id: int, nova_venda: VendaUpdate) -> None:
        print(f"🟡 [AtualizarVendaUseCase] Atualizando venda ID: {venda_id}")

        # 1. Buscar venda original
        venda_original = self.venda_repo.buscar_venda_por_id(venda_id)
        if not venda_original:
            raise ValueError(f"Venda com ID {venda_id} não encontrada.")

        # 2. Buscar itens antigos (para log e rastreio, se necessário)
        itens_antigos = self.venda_repo.buscar_itens_por_venda_id(venda_id)
        print(f"♻️ Itens antigos recuperados: {len(itens_antigos)}")

        # 3. Deletar movimentações anteriores
        print("🧨 Deletando movimentações anteriores (saida e devolução)...")
        self.venda_repo.deletar_movimentacoes_por_venda(venda_id)

        self.venda_repo.deletar_itens_da_venda(venda_id)

        # 5. Calcular novo total
        total = sum(item.quantidade * item.preco_unitario for item in nova_venda.itens)
        self.venda_repo.atualizar_venda(venda_id, nova_venda, total)

        # 7. Inserir novos itens + movimentações
        for item in nova_venda.itens:
            self.venda_repo.inserir_item_venda(venda_id, item)
            self.venda_repo.registrar_saida_por_venda(
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                data_mov=nova_venda.data_venda or datetime.now(),
                venda_id=venda_id 
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
    def __init__(self, venda_repo: VendaRepository):
        self.venda_repo = venda_repo

    def executar(self) -> list[VendaResponse]:
        vendas = self.venda_repo.buscar_vendas()
        return vendas


class ListarItensVendaUseCase:
    def __init__(self, venda_repo: VendaRepository):
        self.venda_repo = venda_repo

    def executar(self, venda_id: int) -> list[ItemVendaResponse]:
        print(f"📦 [ListarItensVenda] Buscando itens da venda ID: {venda_id}")
        itens = self.venda_repo.buscar_itens_por_venda_id(venda_id)
        print(f"🔢 Total de itens encontrados: {len(itens)}")
        return itens


class BuscarVendaComItensUseCase:
    def __init__(self, venda_repo: VendaRepository):
        self.venda_repo = venda_repo

    def executar(self, venda_id: int) -> Optional[dict]:
        print(f"🔍 [BuscarVendaComItens] Buscando venda ID: {venda_id}")
        venda = self.venda_repo.buscar_venda_por_id(venda_id)
        if not venda:
            print("❌ Venda não encontrada.")
            return None

        itens = self.venda_repo.buscar_itens_por_venda_id(venda_id)
        print(f"✅ Venda e {len(itens)} itens encontrados.")
        return {"venda": venda, "itens": itens}

class ListarVendasNaoPagasUseCase:
    def __init__(self, venda_repo: VendaRepository):
        self.venda_repo = venda_repo

    def executar(self) -> list[VendaResponse]:
        return self.venda_repo.listar_vendas_nao_pagas()