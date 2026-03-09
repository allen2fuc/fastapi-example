


from typing import Any, Generic, Optional, Sequence, TypeVar

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

Model = TypeVar("Model", bound=SQLModel)
ID = TypeVar("ID")

class CrudBase(Generic[Model, ID]):
    def __init__(self, model: type[Model], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: ID) -> Optional[Model]:
        return await self.session.get(self.model, id)

    async def get_all(self) -> Sequence[Model]:
        stmt = select(self.model)
        result = await self.session.exec(stmt)
        return result.all()

    async def create(self, create_dict: dict[str, Any]) -> Model:
        new_model = self.model(**create_dict)
        self.session.add(new_model)
        await self.session.commit()
        await self.session.refresh(new_model)
        return new_model

    async def update(self, model: Model, update_dict: dict[str, Any]) -> Model:
        for field, value in update_dict.items():
            setattr(model, field, value)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def delete(self, model: Model) -> None:
        await self.session.delete(model)
        await self.session.commit()