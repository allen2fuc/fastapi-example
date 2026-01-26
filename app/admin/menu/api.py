

from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.schemas import R, Pagination, PaginationQuery
from app.admin.menu import menu_crud
from app.admin.menu.schemas import MenuRead
from app.core.security import get_current_user


router = APIRouter(dependencies=[Depends(get_current_user)])

@router.get("/", summary="分页获取菜单", response_model=R[Pagination[MenuRead]])
async def get_menus(query: Annotated[PaginationQuery, Query(...)], session: AsyncSession = Depends(get_session)) -> R[Pagination[MenuRead]]:
    menus = await menu_crud.get_menus_with_pagination(query, session)
    return R.success(data=menus)

@router.get("/{menu_id}", summary="获取菜单", response_model=R[MenuRead])
async def get_menu(menu_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> R[MenuRead]:
    menu = await menu_crud.get_menu_by_id(menu_id, session)
    return R.success(data=menu)

# 禁用菜单
@router.patch("/{menu_id}/disable", summary="禁用菜单", response_model=R[MenuRead])
async def disable_menu(menu_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> R[MenuRead]:
    menu = await menu_crud.disable_menu(menu_id, session)
    if not menu:
        return R.error(code=status.HTTP_404_NOT_FOUND, message="菜单不存在")
    return R.success(data=menu)

# 删除菜单
@router.delete("/{menu_id}", summary="删除菜单", response_model=R[MenuRead])
async def delete_menu(menu_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> R[MenuRead]:
    menu = await menu_crud.delete_menu(menu_id, session)
    if not menu:
        return R.error(code=status.HTTP_404_NOT_FOUND, message="菜单不存在")
    return R.success(data=menu)