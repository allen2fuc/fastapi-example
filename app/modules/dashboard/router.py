from fastapi import APIRouter, Depends, Request

from app.core.jinja import render_template
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("")
async def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    menus = request.session.get("menus", [])
    return render_template(request, "auth/dashboard.jinja", {
        "menus": menus,
        "current_user": current_user,
    })
