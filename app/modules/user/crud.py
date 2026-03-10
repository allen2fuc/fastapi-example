


from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.crud import CrudBase
from app.models.link_model import RoleMenu, UserRole
from app.models.menu import Menu
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