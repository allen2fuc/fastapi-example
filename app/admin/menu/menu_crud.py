

import uuid
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.schemas import Pagination, PaginationQuery

from .models import Menu


async def get_menu_by_id(menu_id: uuid.UUID, session: AsyncSession):
    result = await session.get(Menu, menu_id)
    return result

# 分页查询菜单
async def get_menus_with_pagination(query: PaginationQuery, session: AsyncSession):
    query_stmt = select(Menu).offset(query.offset).limit(query.limit)
    count_stmt = select(func.count(Menu.id))

    query_result = await session.exec(query_stmt)
    count_result = await session.exec(count_stmt)

    menus = query_result.all()
    total = count_result.one()
    return Pagination(page=query.page, page_size=query.page_size, total=total, items=menus)

# 禁用菜单
async def disable_menu(menu_id: uuid.UUID, session: AsyncSession):
    menu = await get_menu_by_id(menu_id, session)
    if not menu:
        return None
    menu.status = False
    await session.commit()
    return menu

# 删除菜单
async def delete_menu(menu_id: uuid.UUID, session: AsyncSession):
    menu = await get_menu_by_id(menu_id, session)
    if not menu:
        return None
    await session.delete(menu)
    await session.commit()
    return menu