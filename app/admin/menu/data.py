

import logging
import uuid

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.admin.menu.models import Menu

logger = logging.getLogger(__name__)

async def init_menu_data(session: AsyncSession):
    system_menu = Menu(id=uuid.uuid4(), parent_id=None, name="系统管理", path="system", component="System", permission=None, type=1, icon="setting", sort=1, visible=True, status=True)
    user_menu = Menu(id=uuid.uuid4(), parent_id=system_menu.id, name="用户管理", path="/admin/user/list", component="User", permission="admin:user:list", type=2, icon="user", sort=1, visible=True, status=True)
    user_add_menu = Menu(id=uuid.uuid4(), parent_id=user_menu.id, name="添加用户", path="/admin/user/create", component="UserAdd", permission="admin:user:create", type=3, icon="user-plus", sort=1, visible=True, status=True)
    user_edit_menu = Menu(id=uuid.uuid4(), parent_id=user_menu.id, name="编辑用户", path="/admin/user/edit", component="UserEdit", permission="admin:user:edit", type=3, icon="user-edit", sort=2, visible=True, status=True)
    user_delete_menu = Menu(id=uuid.uuid4(), parent_id=user_menu.id, name="删除用户", path="/admin/user/delete", component="UserDelete", permission="admin:user:delete", type=3, icon="user-minus", sort=3, visible=True, status=True)
    user_export_menu = Menu(id=uuid.uuid4(), parent_id=user_menu.id, name="导出用户", path="/admin/user/export", component="UserExport", permission="admin:user:export", type=3, icon="user-export", sort=4, visible=True, status=True)
    user_details_menu = Menu(id=uuid.uuid4(), parent_id=user_menu.id, name="用户详情", path="/admin/user/details", component="UserDetails", permission="admin:user:details", type=3, icon="user-details", sort=5, visible=True, status=True)

    role_menu = Menu(id=uuid.uuid4(), parent_id=system_menu.id, name="角色管理", path="/admin/role/list", component="Role", permission="admin:role:list", type=2, icon="user-shield", sort=2, visible=True, status=True)
    role_add_menu = Menu(id=uuid.uuid4(), parent_id=role_menu.id, name="添加角色", path="/admin/role/create", component="RoleAdd", permission="admin:role:create", type=3, icon="role-plus", sort=1, visible=True, status=True)
    role_edit_menu = Menu(id=uuid.uuid4(), parent_id=role_menu.id, name="编辑角色", path="/admin/role/edit", component="RoleEdit", permission="admin:role:edit", type=3, icon="role-edit", sort=2, visible=True, status=True)
    role_delete_menu = Menu(id=uuid.uuid4(), parent_id=role_menu.id, name="删除角色", path="/admin/role/delete", component="RoleDelete", permission="admin:role:delete", type=3, icon="role-minus", sort=3, visible=True, status=True)
    role_export_menu = Menu(id=uuid.uuid4(), parent_id=role_menu.id, name="导出角色", path="/admin/role/export", component="RoleExport", permission="admin:role:export", type=3, icon="role-export", sort=4, visible=True, status=True)
    role_details_menu = Menu(id=uuid.uuid4(), parent_id=role_menu.id, name="角色详情", path="/admin/role/details", component="RoleDetails", permission="admin:role:details", type=3, icon="role-details", sort=5, visible=True, status=True)


    menu_menu = Menu(id=uuid.uuid4(), parent_id=system_menu.id, name="菜单管理", path="/admin/menu/list", component="Menu", permission="admin:menu:list", type=2, icon="list-ul", sort=3, visible=True, status=True)
    menu_add_menu = Menu(id=uuid.uuid4(), parent_id=menu_menu.id, name="添加菜单", path="/admin/menu/create", component="MenuAdd", permission="admin:menu:create", type=3, icon="plus", sort=1, visible=True, status=True)
    menu_edit_menu = Menu(id=uuid.uuid4(), parent_id=menu_menu.id, name="编辑菜单", path="/admin/menu/edit", component="MenuEdit", permission="admin:menu:edit", type=3, icon="edit", sort=2, visible=True, status=True)
    menu_delete_menu = Menu(id=uuid.uuid4(), parent_id=menu_menu.id, name="删除菜单", path="/admin/menu/delete", component="MenuDelete", permission="admin:menu:delete", type=3, icon="trash", sort=3, visible=True, status=True)
    menu_export_menu = Menu(id=uuid.uuid4(), parent_id=menu_menu.id, name="导出菜单", path="/admin/menu/export", component="MenuExport", permission="admin:menu:export", type=3, icon="export", sort=4, visible=True, status=True)
    menu_details_menu = Menu(id=uuid.uuid4(), parent_id=menu_menu.id, name="菜单详情", path="/admin/menu/details", component="MenuDetails", permission="admin:menu:details", type=3, icon="info", sort=5, visible=True, status=True)

    login_log_menu = Menu(id=uuid.uuid4(), parent_id=system_menu.id, name="登录日志管理", path="/admin/login/list", component="LoginLog", permission="admin:login:list", type=2, icon="file-alt", sort=4, visible=True, status=True)
    login_log_delete_menu = Menu(id=uuid.uuid4(), parent_id=login_log_menu.id, name="删除登录日志", path="/admin/login/delete", component="LoginLogDelete", permission="admin:login:delete", type=3, icon="trash", sort=1, visible=True, status=True)

    menu_list = [system_menu, user_menu, user_add_menu, user_edit_menu, user_delete_menu, user_export_menu, user_details_menu, role_menu, role_add_menu, role_edit_menu, role_delete_menu, role_export_menu, role_details_menu, menu_menu, menu_add_menu, menu_edit_menu, menu_delete_menu, menu_export_menu, menu_details_menu, login_log_menu, login_log_delete_menu]

    # 根据名称或路径查询是否存在
    menu_names = [menu.name for menu in menu_list]
    existing_menu = await session.exec(select(Menu).where(Menu.name.in_(menu_names)))
    existing_menu_names = {menu.name for menu in existing_menu.all()}
    
    # 比对menu_list和existing_menu，如果existing_menu中不存在，则添加
    non_existing_menu = [menu for menu in menu_list if menu.name not in existing_menu_names]
    if non_existing_menu:
        logger.info(f"添加菜单: {', '.join([menu.name for menu in non_existing_menu])} 成功")
        session.add_all(non_existing_menu)
        await session.commit()
    return menu_list
