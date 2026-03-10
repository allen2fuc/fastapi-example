from fastapi import FastAPI, Request, Security
from fastapi.staticfiles import StaticFiles
from app.core.exceptions import register_exceptions
from app.core.jinja import templates
from app.core.lifespan import lifespan
from app.core.config import settings
from app.core.middleware import register_middleware
from app.core.security import get_current_user

app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

app.mount(
    settings.STATIC_URL, 
    StaticFiles(directory=settings.STATIC_PATH), 
    name=settings.STATIC_NAME
)

register_exceptions(app)
register_middleware(app)

@app.get("/")
async def index(
    request: Request, 
):
    return templates.TemplateResponse("index.jinja", {"request": request})