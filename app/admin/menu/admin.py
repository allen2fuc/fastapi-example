from .models import Menu
from app.core.admin import CustomAdmin

class MenuAdmin(CustomAdmin, model=Menu):
    category = "系统管理"
    name_plural = "菜单管理"
    name = "菜单管理"
    label = "菜单管理"
    icon = "fa-solid fa-list"
    column_list = [Menu.name, Menu.path, Menu.component, Menu.permission, Menu.type, Menu.icon, Menu.sort, Menu.visible, Menu.status, Menu.created_at, Menu.updated_at]
    column_sortable_list = [Menu.sort]

    permission_prefix = "admin:menu"