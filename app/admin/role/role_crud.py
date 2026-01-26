


from typing import Any
import uuid
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.schemas import Pagination, PaginationQuery

from .models import Role


async def create_role(role_data: dict[str, Any], session: AsyncSession):
    new_role = Role(**role_data)
    session.add(new_role)
    await session.commit()
    await session.refresh(new_role)
    return new_role


async def get_role_by_name(role_name: str, session: AsyncSession):
    result = await session.exec(select(Role).where(Role.name == role_name))
    return result.one_or_none()

async def get_role_by_id(role_id: uuid.UUID, session: AsyncSession):
    result = await session.get(Role, role_id)
    return result

async def get_roles_with_pagination(query: PaginationQuery, session: AsyncSession):
    query_stmt = select(Role).offset(query.offset).limit(query.limit)
    count_stmt = select(func.count(Role.id))

    query_result = await session.exec(query_stmt)
    count_result = await session.exec(count_stmt)

    roles = query_result.all()
    total = count_result.one()
    return Pagination(page=query.page, page_size=query.page_size, total=total, items=roles)

# 删除角色
async def delete_role(role_id: uuid.UUID, session: AsyncSession):
    role = await get_role_by_id(role_id, session)
    if not role:
        return None
    await session.delete(role)
    await session.commit()
    return role

# 更新角色
async def update_role(role: Role, role_data: dict[str, Any], session: AsyncSession):
    if not role_data:
        return role
    for field, value in role_data.items():
        setattr(role, field, value)
    await session.commit()
    return role