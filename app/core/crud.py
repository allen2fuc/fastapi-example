


from typing import Any, Callable, Generic, Optional, Sequence, TypeVar

from sqlmodel import SQLModel, func, select, text
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select

from app.core.schemas import QueryPagination, QueryResult

Model = TypeVar("Model", bound=SQLModel)
ID = TypeVar("ID")

class CrudBase(Generic[Model, ID]):
    def __init__(self, model: type[Model], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: ID) -> Optional[Model]:
        return await self.session.get(self.model, id)

    async def get_all(self, filters: Callable[[Select], Select] | None = None) -> Sequence[Model]:
        stmt = select(self.model)
        if filters:
            stmt = filters(stmt)
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


    async def query(self, pagination: QueryPagination, filters: Callable[[Select], Select] | None = None) -> QueryResult[Model]:

        offset = pagination.get_offset()
        limit = pagination.get_limit()
        sort = pagination.get_sort_value()

        query_stmt = select(self.model)
        total_stmt = select(func.count()).select_from(self.model)

        if filters:
            query_stmt = filters(query_stmt)
            total_stmt = filters(total_stmt)

        if sort:
            query_stmt = query_stmt.order_by(text(sort))

        query_stmt = query_stmt.offset(offset).limit(limit)
        query_result = await self.session.exec(query_stmt)
        results = query_result.all()

        total_result = await self.session.exec(total_stmt)
        total = total_result.one()

        return QueryResult[Model](
            items=results, 
            total=total, 
            page=pagination.page, 
            page_size=pagination.page_size
        )