from datetime import date
from src.modules.vendas.dto.dto import VendaCreate, ItemVendaCreate, VendaResponse, ItemVendaResponse
from src.modules.vendas.repository.vendas_repository import VendaRepository
from src.modules.estoque.repository.estoque_repository import EstoqueRepository
from datetime import datetime


class RegistrarVendaUseCase:
    def __init__(self, venda_repo: VendaRepository, estoque_repo: EstoqueRepository):
        self.venda_repo = venda_repo
        self.estoque_repo = estoque_repo

    def executar(self, venda: VendaCreate) -> int:
        data_ref: date = (venda.data_venda or datetime.now()).date()

        # 1. Buscar saldo de estoque na data da venda
        estoque_atual = self.estoque_repo.listar_estoque_atual(data_referencia=data_ref)
        saldos = {e.produto_id: e.saldo_estoque for e in estoque_atual}

        # 2. Verificar estoque suficiente para todos os itens
        for item in venda.itens:
            saldo = saldos.get(item.produto_id, 0)
            if item.quantidade > saldo:
                raise ValueError(f"Estoque insuficiente para o produto ID {item.produto_id}.")

        # 3. Calcular total da venda
        total = sum(item.quantidade * item.preco_unitario for item in venda.itens)

        # 4. Inserir venda
        venda_id = self.venda_repo.inserir_venda(venda, total)

        # 5. Inserir itens e movimentações
        for item in venda.itens:
            self.venda_repo.inserir_item_venda(venda_id, item)
            self.venda_repo.registrar_saida_por_venda(
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                data_mov=venda.data_venda or datetime.now()
            )

        return venda_id

class ListarVendasUseCase:
    def __init__(self, repo: VendaRepository):
        self.repo = repo

    def executar(self) -> list[VendaResponse]:
        return self.repo.buscar_vendas()
    
class ListarItensVendaUseCase:
    def __init__(self, repo: VendaRepository):
        self.repo = repo

    def executar(self, venda_id: int) -> list[ItemVendaResponse]:
        return self.repo.buscar_itens_por_venda_id(venda_id)    