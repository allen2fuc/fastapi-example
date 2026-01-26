


import wtforms
from .models import Role
from app.core.admin import CustomAdmin


class RoleAdmin(CustomAdmin, model=Role):
    category = "系统管理"
    name_plural = "角色管理"
    name = "角色管理"   # 详情页的标题
    icon = "fa-solid fa-user-shield"
    column_list = [Role.name, Role.description, Role.menus]
    form_overrides = dict(description=wtforms.TextAreaField)
    column_searchable_list = [Role.name]
    permission_prefix = "admin:role"