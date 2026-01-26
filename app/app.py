from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI

from app.core.admin import register_admin
from app.core.database import init_db
from app.core.exceptions import register_exceptions
from app.core.logger import setup_logger

from app.core.middlewares import register_middlewares
from app.core.security import register_auth_routes
from app.admin.user.api import router as user_router
from app.admin.role.api import router as role_router
from app.admin.menu.api import router as menu_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    logger.info("Starting the application")
    await init_db()
    yield
    logger.info("Stopping the application")

app = FastAPI(lifespan=lifespan)

register_exceptions(app)
register_middlewares(app)
register_admin(app)

app.include_router(user_router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(role_router, prefix="/api/v1/roles", tags=["角色管理"])
app.include_router(menu_router, prefix="/api/v1/menus", tags=["菜单管理"])


