from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.exceptions import register_exceptions
from app.core.lifespan import lifespan, use_route_names_as_operation_ids
from app.core.config import settings
from app.core.middleware import register_middleware
from app.core.openai import register_openapi
from app.modules.user.router import router as user_router
from app.modules.role.router import router as role_router
from app.modules.menu.router import router as menu_router
from app.modules.auth.router import router as auth_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.config.router import router as config_router
from fastapi_mcp import FastApiMCP



def create_app() -> FastAPI:

    app = FastAPI(
        lifespan=lifespan,
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
    )

    app.mount(
        settings.STATIC_URL, 
        StaticFiles(directory=settings.STATIC_PATH), 
        name=settings.STATIC_NAME
    )

    register_openapi(app)
    register_exceptions(app)
    register_middleware(app)

    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
    app.include_router(user_router, prefix="/users", tags=["users"])
    app.include_router(role_router, prefix="/roles", tags=["roles"])
    app.include_router(menu_router, prefix="/menus", tags=["menus"])
    app.include_router(config_router, prefix="/configs", tags=["configs"])

    use_route_names_as_operation_ids(app)

    @app.get("/health")
    async def health():
        return {"status": "ok"}


    mcp = FastApiMCP(app)
    mcp.mount_http()

    return app

app = create_app()