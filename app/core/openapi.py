

from fastapi import Depends, FastAPI

from app.core.security import get_current_user_with_basic_auth


def register_openapi(app: FastAPI):

    openapi_url = "/openapi.json"

    from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html, get_redoc_html
    from fastapi.openapi.utils import get_openapi
    from fastapi import APIRouter

    router = APIRouter(dependencies=[Depends(get_current_user_with_basic_auth)])

    @router.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
            swagger_favicon_url="/static/favicon.ico",
        )

    @router.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()


    @router.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url=openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url="https://unpkg.com/redoc@2/bundles/redoc.standalone.js",
        )

    @router.get(openapi_url, include_in_schema=False)
    async def openapi_json():
        return get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

    app.include_router(router)