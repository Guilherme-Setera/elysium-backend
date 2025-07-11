import warnings
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.infra.config.config import settings
from src.infra.rest import rotas_infra, rotas
from src.infra.openapi.schema import configure_openapi

warnings.filterwarnings("ignore")

app = FastAPI(
    title="Painel CRF API",
    version="1.0.0",
    description="API Painel CRF Clean Arch Sparta",
    swagger_ui_parameters={"displayRequestDuration": True}
)

app.include_router(rotas_infra.infra)
app.include_router(rotas.api_router)

if settings.ENVIRONMENT == "local":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ORIGINS or [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

configure_openapi(app)

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
