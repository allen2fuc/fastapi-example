

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.crud import CrudBase
from app.core.schemas import QueryResult
from app.models.menu import Menu
from app.modules.menu.schemas import MenuQuery


class MenuCrud(CrudBase[Menu, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(Menu, session)


    async def query(self, pagination: MenuQuery) -> QueryResult[Menu]:
        filters = []
        if pagination.name:
            filters.append(Menu.name.like(f"%{pagination.name}%"))
        if pagination.get_type() is not None:
            filters.append(Menu.type == pagination.get_type())

        return await super().query(pagination, filters)