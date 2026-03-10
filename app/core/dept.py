from fastapi import Depends

from app.core.database import get_session
from app.modules.user.crud import UserCrud
from app.modules.role.crud import RoleCrud
from app.modules.menu.crud import MenuCrud

async def get_user_crud(session = Depends(get_session)) -> UserCrud:
    yield UserCrud(session)

async def get_role_crud(session = Depends(get_session)) -> RoleCrud:
    yield RoleCrud(session)

async def get_menu_crud(session = Depends(get_session)) -> MenuCrud:
    yield MenuCrud(session)