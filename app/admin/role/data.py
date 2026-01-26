

import logging
import uuid
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.admin.menu.models import Menu

from .models import Role

logger = logging.getLogger(__name__)

async def init_role_data(session: AsyncSession):
    query_menus = select(Menu).where(Menu.status == True)
    query_mneus_result = await session.exec(query_menus)
    menus = query_mneus_result.all()

    logger.info(f"menus size: {len(menus)}")

    if not menus:
        logger.error(f"菜单不存在")
        return

    admin_role = Role(id=uuid.uuid4(), name="admin", description="管理员")
    admin_role.menus.extend(menus)

    visitor_menus = [menu for menu in menus if menu.type == 2]
    visitor_role = Role(id=uuid.uuid4(), name="visitor", description="只读用户")
    visitor_role.menus.extend(visitor_menus)

    roles = [admin_role, visitor_role]
    role_names = [role.name for role in roles]

    # 根据名称查询角色是否存在
    query_roles = select(Role).where(Role.name.in_(role_names))
    query_roles_result = await session.exec(query_roles)
    existing_roles = query_roles_result.all()
    existing_role_names = {role.name for role in existing_roles}

    logger.info(f"existing_role_names size: {len(existing_role_names)}")

    non_existing_roles = [role for role in roles if role.name not in existing_role_names]
    logger.info(f"non_existing_roles size: {len(non_existing_roles)}")

    if non_existing_roles:
        logger.info(f"添加角色: {', '.join([role.name for role in non_existing_roles])} 成功")
        session.add_all(non_existing_roles)
        await session.commit()
    return roles