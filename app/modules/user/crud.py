


from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.crud import CrudBase
from app.models.user import User

class UserCrud(CrudBase[User, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.exec(stmt)
        return result.one_or_none()