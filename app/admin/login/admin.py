


from app.admin.login.models import LoginLog
from app.core.admin import CustomAdmin


class LoginLogAdmin(CustomAdmin, model=LoginLog):
    category = "系统管理"
    name_plural = "登录日志管理"
    name = "登录日志管理"
    label = "登录日志管理"
    icon = "fa-solid fa-file-alt"
    column_list = [LoginLog.username, LoginLog.ip, LoginLog.user_agent, LoginLog.status, LoginLog.message, LoginLog.created_at]
    column_searchable_list = [LoginLog.username]
    column_sortable_list = [LoginLog.created_at]
    column_default_sort = (LoginLog.created_at, True)
    permission_prefix = "admin:login"

    can_create = False
    can_edit = False
    # can_delete = False
    can_export = False
    can_view_details = False