from fastapi.openapi.utils import get_openapi

def configure_openapi(app):
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="Ambrosia API",
            version="1.0.0",
            description="API Ambrosia Clean Arch - Gestão de Vendas e Clientes",
            routes=app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/api/autenticacao/auth_form"
                    }
                }
            }
        }
        openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
