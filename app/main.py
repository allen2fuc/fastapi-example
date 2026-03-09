from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.core.config import settings
from app.core.users import register_routes

app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

register_routes(app)