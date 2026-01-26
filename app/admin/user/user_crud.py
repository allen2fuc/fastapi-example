


from typing import Any
import uuid

from sqlmodel import func, select

from app.core.schemas import Pagination, PaginationQuery
from app.core.security import hash_password
from .models import User
from sqlmodel.ext.asyncio.session import AsyncSession

async def create_user(user_data: dict[str, Any], session: AsyncSession):
    new_user = User(**user_data)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

async def get_user_by_id(user_id: uuid.UUID, session: AsyncSession):
    result = await session.get(User, user_id)
    return result

async def get_user_by_username(username: str, session: AsyncSession):
    result = await session.exec(select(User).where(User.username == username))
    return result.one_or_none()

async def get_user_by_email(email:str, session: AsyncSession):
    result = await session.exec(select(User).where(User.email == email))
    return result.one_or_none()

async def delete_user(user: User, session: AsyncSession):
    await session.delete(user)
    await session.commit()
    return user

async def update_user(user: User, user_data: dict[str, Any], session: AsyncSession):
    if not user_data:
        return user
    for field, value in user_data.items():
        setattr(user, field, value)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def get_users_with_pagination(query: PaginationQuery, session: AsyncSession):
    query_stmt = select(User).offset(query.offset).limit(query.limit)
    count_stmt = select(func.count(User.id))

    query_result = await session.exec(query_stmt)
    count_result = await session.exec(count_stmt)

    users = query_result.all()
    total = count_result.one()
    return Pagination(page=query.page, page_size=query.page_size, total=total, items=users)


async def get_user_by_ids(ids: list[uuid.UUID], session: AsyncSession):
    result = await session.exec(select(User).where(User.id.in_(ids)))
    return result.all()