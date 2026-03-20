from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.crud import CrudBase
from app.core.schemas import QueryResult
from app.models.link_model import RoleMenu
from app.models.menu import Menu
from app.models.role import Role
from app.modules.role.schemas import RoleQuery


class RoleCrud(CrudBase[Role, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(Role, session)

    async def get_menu_ids(self, role_id: int) -> list[int]:
        stmt = select(RoleMenu.menu_id).where(RoleMenu.role_id == role_id)
        result = await self.session.exec(stmt)
        return result.all()

    async def set_menus(self, role: Role, menu_ids: list[int]) -> None:
        await self.session.refresh(role, ["menus"])
        menus = (
            await self.session.exec(select(Menu).where(Menu.id.in_(menu_ids)))
        ).all() if menu_ids else []
        role.menus = list(menus)
        await self.session.commit()

    async def query(self, pagination: RoleQuery) -> QueryResult[Role]:
        filters = []
        if pagination.name:
            filters.append(Role.name.like(f"%{pagination.name}%"))

        return await super().query(pagination, filters)