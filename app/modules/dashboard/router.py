from fastapi import APIRouter, Depends, Request

from app.core.dept import get_user_crud
from app.core.jinja import render_template
from app.core.security import get_current_user
from app.models.user import User
from app.modules.user.crud import UserCrud

router = APIRouter()


@router.get("")
async def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    user_crud: UserCrud = Depends(get_user_crud),
):
    menus = await user_crud.get_accessible_menus(current_user)
    return render_template(request, "auth/dashboard.jinja", {
        "menus": menus,
        "current_user": current_user,
    })
