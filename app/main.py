from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.core.config import settings

app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)