
from fastapi import Depends, FastAPI, APIRouter
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

from app.core.security import get_current_user

def register_openapi(app: FastAPI):

    OPENAPI_URL = "/openapi.json"

    router = APIRouter(dependencies=[Depends(get_current_user)])

    @router.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=OPENAPI_URL,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        )

    @router.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    @router.get("/redoc", include_in_schema=False)
    async def custom_redoc_html():
        return get_redoc_html(
            openapi_url=OPENAPI_URL,
            title=app.title + " - ReDoc",
            redoc_js_url="https://unpkg.com/redoc@2/bundles/redoc.standalone.js",
        )

    @router.get(OPENAPI_URL, include_in_schema=False)
    async def custom_openapi():
        return app.openapi()

    app.include_router(router, tags=["openapi"])
