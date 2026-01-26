from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.admin.menu.data import init_menu_data
from app.admin.role.data import init_role_data
from app.admin.user.data import init_user_data
from app.core.admin import register_admin
from app.core.database import get_session_context, init_db
from app.core.exceptions import register_exceptions
from app.core.logger import setup_logger

from app.core.middlewares import register_middlewares
from app.admin.user.api import router as user_router
from app.admin.role.api import router as role_router
from app.admin.menu.api import router as menu_router
from app.core.openapi import register_openapi
from app.core.security import reigster_auth_routes
from app.core.slowapi import register_slowapi

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    logger.info("Starting the application")
    await init_db()
    async with get_session_context() as session:
        try:
            logger.info("Initializing menu data...")
            await init_menu_data(session)
            logger.info("Menu data initialized successfully")
            
            logger.info("Initializing role data...")
            await init_role_data(session)
            logger.info("Role data initialized successfully")
            
            logger.info("Initializing user data...")
            await init_user_data(session)
            logger.info("User data initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize data: {e}", exc_info=True)
            raise
    yield
    logger.info("Stopping the application")

app = FastAPI(
    lifespan=lifespan, title="Admin API", version="1.0.0", description="Admin API",
    openapi_url=None, docs_url=None, redoc_url=None
)

app.mount("/static", StaticFiles(directory="static"), name="static")

register_exceptions(app)
register_middlewares(app)
register_admin(app)
register_openapi(app)
reigster_auth_routes(app)
register_slowapi(app)

app.include_router(user_router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(role_router, prefix="/api/v1/roles", tags=["角色管理"])
app.include_router(menu_router, prefix="/api/v1/menus", tags=["菜单管理"])
