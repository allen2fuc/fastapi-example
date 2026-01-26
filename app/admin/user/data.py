


import logging
import secrets
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import User
from app.admin.role.models import Role
from app.core.security import hash_password
from app.admin.user import user_crud

logger = logging.getLogger(__name__)

async def init_user_data(session: AsyncSession):
    
    admin_user = await user_crud.get_user_by_username("admin", session)
    if not admin_user:
        query_roles = select(Role).where(Role.name == "admin")
        query_roles_result = await session.exec(query_roles)
        admin_role = query_roles_result.one_or_none()

        if admin_role:
            admin_password = secrets.token_urlsafe(12)
            admin_user = User(username="admin", email="admin@example.com", hashed_password=hash_password(admin_password), is_admin=True, role_id=admin_role.id)
            session.add(admin_user)
            logger.info(f"添加管理员用户: {admin_user.username} {admin_password} 成功")
            await session.commit()
        else:
            logger.error(f"管理员角色不存在")

    visitor_user = await user_crud.get_user_by_username("visitor", session)
    if not visitor_user:
        query_roles = select(Role).where(Role.name == "visitor")
        query_roles_result = await session.exec(query_roles)
        visitor_role = query_roles_result.one_or_none()

        if visitor_role:

            visitor_password = secrets.token_urlsafe(12)
            visitor_user = User(username="visitor", email="visitor@example.com", hashed_password=hash_password(visitor_password), is_admin=False, role_id=visitor_role.id)
            session.add(visitor_user)
            logger.info(f"添加访客用户: {visitor_user.username} {visitor_password} 成功")
            await session.commit()
        else:
            logger.error(f"访客角色不存在")

    return [admin_user, visitor_user]