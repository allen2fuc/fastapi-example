

import uuid
from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated

from app.admin.login import login_crud
from app.admin.login.schemas import LoginLogRead
from app.core.schemas import R, Pagination, PaginationQuery
from app.core.database import get_session

router = APIRouter()

# 分页获取登录日志
@router.get("/", summary="分页获取登录日志", response_model=R[Pagination[LoginLogRead]])
async def get_login_logs(query: Annotated[PaginationQuery, Query(...)], session: AsyncSession = Depends(get_session)):
    login_logs = await login_crud.get_login_logs_with_pagination(query, session)
    return R.success(data=login_logs)

# 根据ID获取登录日志
@router.get("/{id}", summary="根据ID获取登录日志", response_model=R[LoginLogRead])
async def get_login_log_by_id(id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    login_log = await login_crud.get_login_log_by_id(id, session)
    return R.success(data=login_log)

# 删除历史登录日志，排除今天的记录
@router.delete("/", summary="删除历史登录日志，排除今天的记录", response_model=R[dict])
async def delete_login_logs_except_today(session: AsyncSession = Depends(get_session)):
    deleted_count = await login_crud.delete_login_logs_except_today(session)
    return R.success(data={"deleted_count": deleted_count})