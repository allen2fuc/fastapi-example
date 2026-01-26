

from datetime import datetime
import uuid
from fastapi import Request
from sqlmodel import delete, func, select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.admin.login.models import LoginLog
from app.admin.login.schemas import LoginLogCreate
from app.core.schemas import Pagination, PaginationQuery


async def create_login_log(login_log: LoginLogCreate, session: AsyncSession):
    new_login_log = LoginLog(**login_log.model_dump())
    session.add(new_login_log)
    await session.commit()
    await session.refresh(new_login_log)
    return new_login_log


async def create_login_log_from_request(
    username: str,
    login_success: bool,
    message: str,
    request: Request,
    session: AsyncSession
):
    login_log = LoginLogCreate(
        username=username,
        ip=request.client.host,
        user_agent=request.headers.get("User-Agent"),
        status=login_success,
        message=message,
    )
    return await create_login_log(login_log, session)


async def get_login_log_by_id(id: uuid.UUID, session: AsyncSession):
    result = await session.exec(select(LoginLog).where(LoginLog.id == id))
    return result.one_or_none()


async def get_login_log_by_username(username: str, session: AsyncSession):
    result = await session.exec(select(LoginLog).where(LoginLog.username == username))
    return result.all()


async def get_login_logs_with_pagination(query: PaginationQuery, session: AsyncSession):
    query_stmt = select(LoginLog).offset(query.offset).limit(query.limit)
    count_stmt = select(func.count(LoginLog.id))
    query_result = await session.exec(query_stmt)
    count_result = await session.exec(count_stmt)
    login_logs = query_result.all()
    total = count_result.one()
    return Pagination(page=query.page, page_size=query.page_size, total=total, items=login_logs)


async def delete_login_logs_except_today(session: AsyncSession):
    # 删除今天之前的登录日志
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await session.exec(delete(LoginLog).where(LoginLog.created_at < today))
    await session.commit()
    return result.rowcount
