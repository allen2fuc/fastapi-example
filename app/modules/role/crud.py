


from app.core.crud import CrudBase
from app.models.role import Role
from sqlmodel.ext.asyncio.session import AsyncSession


class RoleCrud(CrudBase[Role, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(Role, session)