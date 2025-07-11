from typing import Optional
from datetime import date
from src.modules.vendas.dto.dto import VendaCreate, VendaResponse, VendaUpdate, PainelResumoResponse, ResumoVendasPorData, RelatorioDetalhadoProduto, LogVendaResponse
from src.modules.vendas.abc_classes.vendas_abc import IVendasRepository


class RegistrarVendaUseCase:
    def __init__(self, repo: IVendasRepository) -> None:
        self.repo: IVendasRepository = repo

    async def execute(self, payload: VendaCreate) -> int:
        return await self.repo.registrar_venda(payload)

class ListarVendasUseCase:
    def __init__(self, repo: IVendasRepository) -> None:
        self.repo: IVendasRepository = repo

    async def execute(
        self,
        cliente_id: Optional[int] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        forma_pagamento: Optional[str] = None,
    ) -> list[VendaResponse]:
        return await self.repo.listar_vendas(
            cliente_id=cliente_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            forma_pagamento=forma_pagamento
        )
    
class BuscarVendaPorIdUseCase:
    def __init__(self, repo: IVendasRepository) -> None:
        self.repo: IVendasRepository = repo

    async def execute(self, venda_id: int) -> VendaResponse | None:
        return await self.repo.buscar_venda_por_id(venda_id)  

class AtualizarVendaUseCase:
    def __init__(self, repo: IVendasRepository) -> None:
        self.repo: IVendasRepository = repo

    async def execute(self, venda_id: int, payload: VendaUpdate) -> None:
        await self.repo.atualizar_venda(venda_id, payload)

class ExcluirVendaUseCase:
    def __init__(self, repo: IVendasRepository) -> None:
        self.repo: IVendasRepository = repo

    async def execute(self, venda_id: int) -> None:
        await self.repo.excluir_venda(venda_id)        

class GerarPainelResumoUseCase:
    def __init__(self, repo: IVendasRepository) -> None:
        self.repo: IVendasRepository = repo

    async def execute(self, inicio: date, fim: date) -> PainelResumoResponse:
        return await self.repo.painel_resumo(inicio, fim)        
    
class GerarRelatorioResumoUseCase:
    def __init__(self, repo: IVendasRepository) -> None:
        self.repo: IVendasRepository = repo

    async def execute(self, data_inicio: date, data_fim: date) -> list[ResumoVendasPorData]:
        return await self.repo.gerar_relatorio_resumo(data_inicio, data_fim)    
    
class GerarRelatorioDetalhadoProdutosUseCase:
    def __init__(self, repo: IVendasRepository) -> None:
        self.repo: IVendasRepository = repo

    async def execute(self, data_inicio: date, data_fim: date) -> list[RelatorioDetalhadoProduto]:
        return await self.repo.gerar_relatorio_detalhado_produtos(data_inicio, data_fim)    
    
class RegistrarLogAlteracaoUseCase:
    def __init__(self, repo: IVendasRepository) -> None:
        self.repo: IVendasRepository = repo

    async def execute(
        self,
        venda_id: int,
        campo: str,
        valor_anterior: str,
        valor_novo: str,
        usuario: str
    ) -> None:
        await self.repo.registrar_log_alteracao(
            venda_id=venda_id,
            campo=campo,
            valor_anterior=valor_anterior,
            valor_novo=valor_novo,
            usuario=usuario
        )    

class ListarLogsVendaUseCase:
    def __init__(self, repo: IVendasRepository):
        self.repo = repo

    async def execute(
        self,
        venda_id: Optional[int] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> list[LogVendaResponse]:
        return await self.repo.listar_logs_venda(
            venda_id=venda_id,
            data_inicio=data_inicio,
            data_fim=data_fim
        )        