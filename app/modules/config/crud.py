


from typing import Sequence
from app.models.config import Config
from app.core.crud import CrudBase
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select


class ConfigCrud(CrudBase[Config, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(Config, session)

    async def get_config_by_code(self, code: str) -> Sequence[Config]:
        stmt = select(Config).where(Config.code == code).order_by(Config.sort.desc())
        result = await self.session.exec(stmt)
        return result.all()