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

# ------------------------------------------------------------
# Inicialização do app FastAPI
# ------------------------------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="API Painel CRF Clean Arch Sparta",
    swagger_ui_parameters={"displayRequestDuration": True},
)

# ------------------------------------------------------------
# Rotas
# ------------------------------------------------------------
app.include_router(rotas_infra.infra)
app.include_router(rotas.api_router)

# ------------------------------------------------------------
# CORS dinâmico (igual ao Ambrosia)
# ------------------------------------------------------------
def parse_origins(origins_raw: str | list[str] | None) -> list[str]:
    """Interpreta o valor de ORIGINS em diversos formatos."""
    if not origins_raw:
        return []
    if isinstance(origins_raw, list):
        return origins_raw
    try:
        raw = origins_raw.strip()
        if raw.startswith("["):
            data = json.loads(raw)
            if isinstance(data, list):
                return [o.strip() for o in data if isinstance(o, str) and o.strip()]
        # fallback: separar por vírgula ou ponto e vírgula
        return [o.strip() for o in raw.replace(",", ";").split(";") if o.strip()]
    except Exception:
        return ["*"]

print("ENVIRONMENT =", settings.ENVIRONMENT)

LOCAL_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

if settings.ENVIRONMENT.lower() == "local":
    allow_origins = LOCAL_ORIGINS
else:
    allow_origins = parse_origins(settings.ORIGINS) or ["https://elysium-fronted.vercel.app"]

print("CORS allow_origins =", allow_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
    max_age=600,
)

# ------------------------------------------------------------
# OpenAPI
# ------------------------------------------------------------
configure_openapi(app)

# ------------------------------------------------------------
# Execução direta
# ------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app=app, host="0.0.0.0", port=port)
