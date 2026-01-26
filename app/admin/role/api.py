from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.schemas import R, Pagination, PaginationQuery
from app.admin.role import role_crud
from .schemas import RoleCreate, RoleRead, RoleUpdate
from app.core.security import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])

@router.post("/", summary="创建角色", response_model=R[RoleRead])
async def post_role(role: RoleCreate, session: AsyncSession = Depends(get_session)):
    existing_role = await role_crud.get_role_by_name(role.name, session)
    if existing_role:
        return R.error(code=status.HTTP_400_BAD_REQUEST, message="角色名称已存在")
    role_data = role.model_dump(exclude_unset=True)
    role = await role_crud.create_role(role_data, session)
    return R.success(data=role)


@router.put("/{role_id}", summary="更新角色", response_model=R[RoleRead])
async def put_role(role_id: uuid.UUID, role: RoleUpdate, session: AsyncSession = Depends(get_session)) -> R[RoleRead]:
    existing_role = await role_crud.get_role_by_id(role_id, session)
    if not existing_role:
        return R.error(code=status.HTTP_404_NOT_FOUND, message="角色不存在")
    role_data = role.model_dump(exclude_unset=True)
    if role_data:
        role = await role_crud.update_role(existing_role, role_data, session)
        return R.success(data=role)
    else:
        return R.error(code=status.HTTP_400_BAD_REQUEST, message="修改数据不能为空")

@router.get("/", summary="分页获取角色", response_model=R[Pagination[RoleRead]])
async def get_roles(query: Annotated[PaginationQuery, Query(...)], session: AsyncSession = Depends(get_session)) -> R[Pagination[RoleRead]]:
    roles = await role_crud.get_roles_with_pagination(query, session)
    return R.success(data=roles)

    
@router.get("/{role_id}", summary="获取角色", response_model=R[RoleRead])
async def get_role(role_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> R[RoleRead]:
    role = await role_crud.get_role_by_id(role_id, session)
    if not role:
        return R.error(code=status.HTTP_404_NOT_FOUND, message="角色不存在")
    return R.success(data=role)

# 删除角色
@router.delete("/{role_id}", summary="删除角色", response_model=R[RoleRead])
async def delete_role(role_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> R[RoleRead]:
    role = await role_crud.delete_role(role_id, session)
    if not role:
        return R.error(code=status.HTTP_404_NOT_FOUND, message="角色不存在")
    return R.success(data=role)