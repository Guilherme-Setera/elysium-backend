from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import date
from typing import Optional
from src.modules.estoque.dto.dto import (
    MovimentacaoCreate,
    EstoqueAtualResponse,
    EstoqueBaixoResponse,
    OperacaoResponse,
    ProdutoCreate,
    ProdutoResponse,
    ProdutoPrecoResponse,
    PrecoAtualResponse,
    PrecoManualInput,
    CustoOperacionalCreate,
    CustoOperacionalResponse,
    CustoEstoqueResponse,
    CategoriaCustoCreate,
    CategoriaCustoResponse,
    MovimentacaoUpdate
)
from src.modules.estoque.dto.dto_materia_prima import (
    MateriaPrimaCreate,
    MateriaPrimaResponse,
    MateriaPrimaUpdate,
    MateriaPrimaPrecoCreate,
    PrecoMateriaPrimaResponse,
    PrecoMateriaPrimaUnitarioResponse,
    EstoqueMateriaPrimaAtualResponse,
    MovimentacaoMateriaPrimaCreate
)
from src.modules.estoque.usecase.estoque_usecase import EstoqueUseCase
from src.modules.estoque.usecase.materias_prima_usecase import MateriasPrimaUseCase
from src.modules.estoque.estoque_dependencies import get_estoque_usecase, get_materias_prima_usecase

router = APIRouter(prefix="/estoque", tags=["Estoque"])


@router.post("/movimentar", status_code=status.HTTP_201_CREATED)
def movimentar_estoque(
    data: MovimentacaoCreate,
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
):
    return usecase.registrar_movimentacao(data)


@router.get("/atual", response_model=list[EstoqueAtualResponse])
def obter_estoque_atual(
    data_referencia: date = Query(default_factory=date.today),
    usecase: EstoqueUseCase = Depends(get_estoque_usecase)
) -> list[EstoqueAtualResponse]:
    return usecase.listar_estoque_atual(data_referencia)


@router.get("/baixo", response_model=list[EstoqueBaixoResponse])
def obter_estoque_baixo(
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
) -> list[EstoqueBaixoResponse]:
    return usecase.listar_estoque_baixo()


@router.get("/operacoes", response_model=list[OperacaoResponse])
def listar_operacoes(
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
) -> list[OperacaoResponse]:
    return usecase.listar_operacoes()


@router.post("/produtos/", response_model=int)
def criar_produto(
    data: ProdutoCreate,
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
):
    return usecase.cadastrar_produto(data)


@router.post("/produtos/batch", response_model=list[int])
def criar_produtos_em_lote(
    data: list[ProdutoCreate],
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
):
    return usecase.cadastrar_produtos_em_lote(data)


@router.get("/produtos/", response_model=list[ProdutoResponse])
def listar_produtos(
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
) -> list[ProdutoResponse]:
    return usecase.listar_produtos()


@router.delete("/produtos/{id}", response_model=bool)
def desativar_produto(
    id: int,
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
) -> bool:
    sucesso = usecase.desativar_produto(id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Produto não encontrado ou já inativo")
    return True


@router.get("/produtos/{produto_id}/preco-atual", response_model=PrecoAtualResponse)
def obter_preco_atual(
    produto_id: int,
    data_base: Optional[date] = None,
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
) -> PrecoAtualResponse:
    if data_base is None:
        data_base = date.today()
    preco = usecase.buscar_preco_atual(produto_id, data_base)
    if not preco:
        raise HTTPException(status_code=404, detail="Nenhum preço encontrado para esse produto")
    return preco


@router.get("/produtos/{produto_id}/precos", response_model=list[ProdutoPrecoResponse])
def listar_precos_produto(
    produto_id: int,
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
) -> list[ProdutoPrecoResponse]:
    return usecase.listar_precos_produto(produto_id)


@router.post("/produtos/{produto_id}/precos", status_code=201)
def registrar_preco_manual(
    produto_id: int,
    data: PrecoManualInput,
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
):
    data_referencia = data.data_referencia or date.today()
    return usecase.inserir_preco_produto(produto_id, data.preco_custo, data.preco_venda, data_referencia)


@router.post("/custos-operacionais", response_model=int)
def criar_custo_operacional(
    data: CustoOperacionalCreate,
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
):
    return usecase.inserir_custo_operacional(data)


@router.get("/custos", response_model=list[CustoOperacionalResponse])
def listar_custos_operacionais(
    data_inicio: date,
    data_fim: date,
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
):
    return usecase.listar_custos_operacionais(data_inicio, data_fim)


@router.get("/custos/estoque", response_model=list[CustoEstoqueResponse])
def listar_custos_estoque(
    data_inicio: date,
    data_fim: date,
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
) -> list[CustoEstoqueResponse]:
    return usecase.listar_custos_estoque_por_data(data_inicio, data_fim)


@router.post("/categorias-custo", response_model=int)
def criar_categoria_custo(
    data: CategoriaCustoCreate,
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
):
    return usecase.inserir_categoria_custo(data)


@router.get("/categorias-custo", response_model=list[CategoriaCustoResponse])
def listar_categorias_custo(
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
) -> list[CategoriaCustoResponse]:
    return usecase.listar_categorias_custo()


@router.post("/materias-prima", response_model=int, status_code=status.HTTP_201_CREATED)
def criar_materia_prima(
    data: MateriaPrimaCreate,
    usecase: MateriasPrimaUseCase = Depends(get_materias_prima_usecase),
) -> int:
    return usecase.cadastrar_materia_prima(data)


@router.get("/materias-prima", response_model=list[MateriaPrimaResponse])
def listar_materias_prima(
    usecase: MateriasPrimaUseCase = Depends(get_materias_prima_usecase),
) -> list[MateriaPrimaResponse]:
    return usecase.listar_materia_prima()


@router.delete("/materias-prima/{id}", response_model=bool)
def inativar_materia_prima(
    id: int,
    usecase: MateriasPrimaUseCase = Depends(get_materias_prima_usecase),
) -> bool:
    sucesso = usecase.inativar_materia_prima(id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Matéria-prima não encontrada ou já inativa")
    return True


@router.patch("/materias-prima/{id}", response_model=bool)
def atualizar_materia_prima(
    id: int,
    data: MateriaPrimaUpdate,
    usecase: MateriasPrimaUseCase = Depends(get_materias_prima_usecase),
) -> bool:
    sucesso = usecase.atualizar_materia_prima(id, data)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Matéria-prima não encontrada ou já inativa")
    return True


@router.post(
    "/materias-prima/movimentar",
    response_model=int,
    status_code=status.HTTP_201_CREATED,
)
def movimentar_materia_prima(
    data: MovimentacaoMateriaPrimaCreate,
    usecase: MateriasPrimaUseCase = Depends(get_materias_prima_usecase),
) -> int:
    return usecase.registrar_movimentacao_materia_prima(data)


@router.get("/materias-prima/estoque/atual", response_model=list[EstoqueMateriaPrimaAtualResponse])
def obter_estoque_materia_prima_atual(
    data_referencia: date = Query(default_factory=date.today),
    usecase: MateriasPrimaUseCase = Depends(get_materias_prima_usecase),
) -> list[EstoqueMateriaPrimaAtualResponse]:
    return usecase.listar_estoque_materia_prima_atual(data_referencia)


@router.get("/materias-prima/{materia_prima_id}/preco-atual", response_model=PrecoMateriaPrimaResponse)
def obter_preco_materia_prima_atual(
    materia_prima_id: int,
    data_base: Optional[date] = None,
    usecase: MateriasPrimaUseCase = Depends(get_materias_prima_usecase),
) -> PrecoMateriaPrimaResponse:
    if data_base is None:
        data_base = date.today()
    preco = usecase.buscar_preco_materia_prima(materia_prima_id, data_base)
    if not preco:
        raise HTTPException(status_code=404, detail="Nenhum preço encontrado para essa matéria-prima")
    return preco


@router.get("/materias-prima/{materia_prima_id}/precos", response_model=list[PrecoMateriaPrimaUnitarioResponse])
def listar_precos_materia_prima(
    materia_prima_id: int,
    usecase: MateriasPrimaUseCase = Depends(get_materias_prima_usecase),
) -> list[PrecoMateriaPrimaUnitarioResponse]:
    return usecase.listar_precos_materia_prima(materia_prima_id)


@router.post("/materias-prima/{materia_prima_id}/precos", status_code=201)
def registrar_preco_materia_prima(
    materia_prima_id: int,
    data: MateriaPrimaPrecoCreate,
    usecase: MateriasPrimaUseCase = Depends(get_materias_prima_usecase),
):
    data_referencia = data.data_referencia or date.today()
    payload = MateriaPrimaPrecoCreate(
        materia_prima_id=materia_prima_id,
        data_referencia=data_referencia,
        preco_custo=data.preco_custo,
        data_fim=data.data_fim,
    )
    return usecase.inserir_preco_materia_prima(payload)


@router.patch("/movimentacoes/{mov_id}", response_model=int, status_code=status.HTTP_200_OK)
def editar_movimentacao(
    mov_id: int,
    data: MovimentacaoUpdate,
    usecase: EstoqueUseCase = Depends(get_estoque_usecase),
):
    if (
        data.produto_id is None
        and data.tipo is None
        and data.quantidade is None
        and data.data_mov is None
        and data.operacao_id is None
        and data.venda_id is None
        and data.lote_numero is None
        and data.data_validade is None
        and data.preco_custo is None
        and data.preco_venda is None
    ):
        raise HTTPException(status_code=400, detail="Nenhum campo enviado para atualização.")

    try:
        updated_id = usecase.editar_movimentacao(mov_id, data)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if updated_id == -1:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada ou não pode ser alterada.")

    return updated_id
