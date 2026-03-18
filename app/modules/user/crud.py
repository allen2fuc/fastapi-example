from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.crud import CrudBase
from app.models.link_model import RoleMenu, UserRole
from app.models.menu import Menu
from app.models.role import Role
from app.models.user import User


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

    async def set_roles(self, user: User, role_ids: list[int]) -> None:
        await self.session.refresh(user, ["roles"])
        roles = (
            await self.session.exec(select(Role).where(Role.id.in_(role_ids)))
        ).all() if role_ids else []
        user.roles = list(roles)
        await self.session.commit()
