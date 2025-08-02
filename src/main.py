import warnings
import json
import os
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


def parse_origins(origins_raw: str | list[str]) -> list[str]:
    if isinstance(origins_raw, list):
        return origins_raw
    try:
        return json.loads(origins_raw) if origins_raw.startswith("[") else [origins_raw]
    except Exception:
        return ["*"]

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
        allow_origins=parse_origins(settings.ORIGINS),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

configure_openapi(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app=app, host="0.0.0.0", port=port)
