from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.crud import CrudBase
from app.core.schemas import QueryResult
from app.models.link_model import RoleMenu, UserRole
from app.models.menu import Menu
from app.models.role import Role
from app.models.user import User
from app.modules.user.schemas import UserQuery


def _menu_to_dict(menu: Menu) -> dict:
    return {
        "id": menu.id,
        "parent_id": menu.parent_id,
        "name": menu.name,
        "path": menu.path,
        "icon": menu.icon,
        "type": menu.type,
        "sort": menu.sort,
    }


class UserCrud(CrudBase[User, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.exec(stmt)
        return result.one_or_none()

    async def get_permissions(self, user_id: int) -> list[str]:
        stmt = (
            select(Menu.permission)
            .select_from(Menu)
            .join(RoleMenu, RoleMenu.menu_id == Menu.id)
            .join(UserRole, UserRole.role_id == RoleMenu.role_id)
            .where(UserRole.user_id == user_id, Menu.permission.isnot(None), Menu.permission != '')
            .distinct()
        )
        result = await self.session.exec(stmt)
        return result.all()

    async def get_role_ids(self, user_id: int) -> list[int]:
        stmt = select(UserRole.role_id).where(UserRole.user_id == user_id)
        result = await self.session.exec(stmt)
        return result.all()

    async def get_accessible_menus(self, user: User) -> list[dict]:
        if user.is_superuser:
            stmt = (
                select(Menu)
                .where(Menu.visible == True, Menu.type.in_([1, 2]))
                .order_by(Menu.sort.desc())
            )
        else:
            stmt = (
                select(Menu)
                .select_from(Menu)
                .join(RoleMenu, RoleMenu.menu_id == Menu.id)
                .join(UserRole, UserRole.role_id == RoleMenu.role_id)
                .where(
                    UserRole.user_id == user.id,
                    Menu.visible == True,
                    Menu.type.in_([1, 2]),
                )
                .distinct()
                .order_by(Menu.sort.desc())
            )
        result = await self.session.exec(stmt)
        return [_menu_to_dict(m) for m in result.all()]

    async def set_roles(self, user: User, role_ids: list[int]) -> None:
        await self.session.refresh(user, ["roles"])
        roles = (
            await self.session.exec(select(Role).where(Role.id.in_(role_ids)))
        ).all() if role_ids else []
        user.roles = list(roles)
        await self.session.commit()


    async def query(self, pagination: UserQuery) -> QueryResult[User]:
        filters = []
        if pagination.email:
            filters.append(User.email.like(f"%{pagination.email}%"))
        if pagination.get_is_active() is not None:
            filters.append(User.is_active == pagination.get_is_active())


        return await super().query(pagination, filters)