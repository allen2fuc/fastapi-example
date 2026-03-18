
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


def dt_format(value, fmt="%Y-%m-%d %H:%M:%S"):
    return value.strftime(fmt) if value else ""

templates.env.filters["dt"] = dt_format


def render_template(request: Request, template_name: str, context: dict = {}, **kwargs):
    return templates.TemplateResponse(
        template_name, 
        context={"request": request, **context}, 
        **kwargs
    )