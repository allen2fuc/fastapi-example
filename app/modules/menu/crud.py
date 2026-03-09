

from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.crud import CrudBase
from app.models.menu import Menu


class MenuCrud(CrudBase[Menu, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(Menu, session)