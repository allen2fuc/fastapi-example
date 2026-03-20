from typing import Sequence
from app.models.config import Config
from app.core.crud import CrudBase
from app.core.schemas import QueryResult
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.modules.config.schemas import ConfigQuery


class ConfigCrud(CrudBase[Config, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(Config, session)

    async def get_config_by_code(self, code: str) -> Sequence[Config]:
        stmt = select(Config).where(Config.code == code).order_by(Config.sort.desc())
        result = await self.session.exec(stmt)
        return result.all()

    async def query(self, pagination: ConfigQuery) -> QueryResult[Config]:
        filters = []
        if pagination.code:
            filters.append(Config.code.like(f"%{pagination.code}%"))
        if pagination.key:
            filters.append(Config.key.like(f"%{pagination.key}%"))
        return await super().query(pagination, filters)
