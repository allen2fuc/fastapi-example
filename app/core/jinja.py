
from fastapi import Request
from fastapi.templating import Jinja2Templates
from app.core.config import settings

templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

def has_permission(permission: str, request: Request) -> bool:
    if hasattr(request.state, "scopes"):
        perms = request.state.scopes
    else:
        perms = []
    return permission in perms

templates.env.globals["has_permission"] = has_permission