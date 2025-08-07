from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date

from sqlalchemy.orm import Session
from src.infra.db.connection import get_db

from src.modules.produtos.repository.produtos_repository import ProdutosRepository
from src.modules.produtos.usecase.produtos_usecase import ProdutosUseCase
from src.modules.produtos.controller.dto import (
    ProdutoCreate,
    ProdutoUpdate,
    ProdutoResponse,
    ProdutoPrecoResponse,
    ProdutoUpdateComId
)

router = APIRouter(prefix="/produtos", tags=["Produtos"])

def get_usecase(db: Session = Depends(get_db)) -> ProdutosUseCase:
    repo = ProdutosRepository(db)
    return ProdutosUseCase(repo)

@router.post("/", response_model=int, status_code=status.HTTP_201_CREATED)
def criar_produto(data: ProdutoCreate, usecase: ProdutosUseCase = Depends(get_usecase)):
    return usecase.cadastrar_produto(data)

@router.get("/", response_model=List[ProdutoResponse])
def listar_produtos(
    data_referencia: Optional[date] = Query(None, description="Data base para preço vigente"),
    usecase: ProdutosUseCase = Depends(get_usecase)
):
    return usecase.listar_produtos(data_referencia=data_referencia)

@router.get("/{produto_id}", response_model=ProdutoResponse)
def buscar_produto_por_id(
    produto_id: int,
    data_referencia: Optional[date] = Query(None, description="Data base para preço vigente"),
    usecase: ProdutosUseCase = Depends(get_usecase)
):
    produto = usecase.buscar_produto_por_id(produto_id, data_referencia)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@router.put("/{produto_id}", response_model=bool)
def atualizar_produto(
    produto_id: int,
    data: ProdutoUpdate,
    usecase: ProdutosUseCase = Depends(get_usecase)
):
    atualizado = usecase.atualizar_produto(produto_id, data)
    if not atualizado:
        raise HTTPException(status_code=404, detail="Produto não encontrado ou não atualizado")
    return True

@router.put("/batch", response_model=int)
def atualizar_produtos_em_lote(
    updates: list[ProdutoUpdateComId],
    usecase: ProdutosUseCase = Depends(get_usecase)
):
    atualizados = usecase.atualizar_produtos_em_lote(updates)
    return atualizados


@router.delete("/{produto_id}", response_model=bool)
def desativar_produto(
    produto_id: int,
    usecase: ProdutosUseCase = Depends(get_usecase)
):
    desativado = usecase.desativar_produto(produto_id)
    if not desativado:
        raise HTTPException(status_code=404, detail="Produto não encontrado ou já desativado")
    return True

@router.get("/{produto_id}/precos", response_model=List[ProdutoPrecoResponse])
def listar_precos_produto(
    produto_id: int,
    usecase: ProdutosUseCase = Depends(get_usecase)
):
    return usecase.listar_precos_produto(produto_id)

@router.post("/{produto_id}/precos", response_model=bool)
def inserir_novo_preco(
    produto_id: int,
    data_referencia: date,
    preco_custo: float,
    preco_venda: float,
    usecase: ProdutosUseCase = Depends(get_usecase)
):
    return usecase.inserir_novo_preco(produto_id, data_referencia, preco_custo, preco_venda)
