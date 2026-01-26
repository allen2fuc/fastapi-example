

import secrets
from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.admin.user.models import User
from app.core.database import get_session
from app.core.schemas import R, Pagination, PaginationQuery
from app.core.security import get_current_user, hash_password, verify_password
from app.admin.user import user_crud

from .schemas import ChangePassword, UserCreate, UserRead, UserUpdate

router = APIRouter(dependencies=[Depends(get_current_user)])

@router.get("/me", summary="获取当前用户", response_model=UserRead)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return R.success(data=current_user)

@router.post("/", summary="创建用户", response_model=R[UserRead])
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    existing_user = await user_crud.get_user_by_username(user.username, session)
    if existing_user:
        return R.error(code=status.HTTP_400_BAD_REQUEST, message="Username already exists")
    existing_user = await user_crud.get_user_by_email(user.email, session)
    if existing_user:
        return R.error(code=status.HTTP_400_BAD_REQUEST, message="Email already exists")
    user_data = user.model_dump(exclude_unset=True)
    user_data["hashed_password"] = hash_password(user_data["password"])
    user = await user_crud.create_user(user_data, session)
    return R.success(data=user)

# 分页
@router.get("/", summary="分页获取用户", response_model=R[Pagination[UserRead]])
async def get_users(query: Annotated[PaginationQuery, Query(...)], session: AsyncSession = Depends(get_session)) -> R[Pagination[UserRead]]:
    users = await user_crud.get_users_with_pagination(query, session)
    return R.success(data=users)

@router.get("/{user_id}", summary="获取用户", response_model=R[UserRead])
async def get_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> R[UserRead]:
    user = await user_crud.get_user_by_id(user_id, session)
    if not user:
        return R.error(code=status.HTTP_404_NOT_FOUND, message="用户不存在")
    return R.success(data=user)

@router.delete("/{user_id}", summary="删除用户", response_model=R[UserRead])
async def delete_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> R[UserRead]:
    user = await user_crud.get_user_by_id(user_id, session)
    if not user:
        return R.error(code=status.HTTP_404_NOT_FOUND, message="用户不存在")
    await user_crud.delete_user(user, session)
    return R.success(data=user)

@router.patch("/{user_id}/change-password", summary="修改密码", response_model=R[UserRead])
async def change_password(user_id: uuid.UUID, change_password: ChangePassword, session: AsyncSession = Depends(get_session)) -> R[UserRead]:
    user = await user_crud.get_user_by_id(user_id, session)
    if not user:
        return R.error(code=status.HTTP_404_NOT_FOUND, message="用户不存在")
    if not verify_password(change_password.old_password, user.hashed_password):
        return R.error(code=status.HTTP_400_BAD_REQUEST, message="旧密码错误")
    hashed_password = hash_password(change_password.new_password)
    user_data = {"hashed_password": hashed_password}
    user = await user_crud.update_user(user, user_data, session)
    return R.success(data=user)

@router.patch("/{user_id}/reset-password", summary="重置密码", response_model=R[UserRead])
async def reset_password(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> R[UserRead]:
    user = await user_crud.get_user_by_id(user_id, session)
    if not user:
        return R.error(code=status.HTTP_404_NOT_FOUND, message="用户不存在")
    random_password = secrets.token_urlsafe(12)
    password = random_password
    user_data = {"hashed_password": hash_password(password)}
    user = await user_crud.update_user(user, user_data, session)
    return R.success(data={ "message": f"密码已重置为：{password}" })

@router.patch("/{user_id}", summary="更新用户", response_model=R[UserRead])
async def update_user(user_id: uuid.UUID, user_update: UserUpdate, session: AsyncSession = Depends(get_session)) -> R[UserRead]:
    user = await user_crud.get_user_by_id(user_id, session)
    if not user:
        return R.error(code=status.HTTP_404_NOT_FOUND, message="用户不存在")
    user_update_data = user_update.model_dump(exclude_unset=True)
    user = await user_crud.update_user(user, user_update_data, session)
    return R.success(data=user)


