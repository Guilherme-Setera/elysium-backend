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
    swagger_ui_parameters={"displayRequestDuration": True},
)

# Routers
app.include_router(rotas_infra.infra)
app.include_router(rotas.api_router)


def parse_origins(origins_raw: str | list[str]) -> list[str]:
    """
    Aceita:
      - JSON list (ex: '["https://a.com","https://b.com"]')
      - String separada por ';' ou ',' (ex: "https://a.com;https://b.com")
      - "*" (coringa)
    """
    if isinstance(origins_raw, list):
        return origins_raw

    if not origins_raw:
        return ["*"]

    raw = origins_raw.strip()
    if raw == "*":
        return ["*"]

    # tenta JSON
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
                return [x.strip() for x in parsed if x.strip()]
        except Exception:
            pass

    # fallback: split por ';' ou ','
    parts = [p.strip() for p in raw.replace(",", ";").split(";")]
    return [p for p in parts if p] or ["*"]


print("ENVIRONMENT =", settings.ENVIRONMENT)
print("ORIGINS (raw) =", settings.ORIGINS)

# CORS
if settings.ENVIRONMENT == "local":
    # Ambiente local: libera o front local com credenciais
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    origins = parse_origins(settings.ORIGINS)
    print("ORIGINS (parsed) =", origins)

    # Regra do CORS: se allow_origins == ["*"], NÃO pode allow_credentials=True
    allow_credentials = False if origins == ["*"] else True

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# OpenAPI
configure_openapi(app)


# Opcional: endpoint rápido de healthcheck
@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok", "env": settings.ENVIRONMENT}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app=app, host="0.0.0.0", port=port)
