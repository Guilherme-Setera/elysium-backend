from fastapi import APIRouter
from src.modules.auth.controller.router import router as auth_router
from src.modules.clientes.controller.router import router as clientes_router
from src.modules.produtos.controller.router import router as produtos_router
from src.modules.estoque.controller.router import router as estoque_router 
from src.modules.vendas.controller.router import router as vendas_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(clientes_router)
api_router.include_router(produtos_router)
api_router.include_router(estoque_router)
api_router.include_router(vendas_router)
