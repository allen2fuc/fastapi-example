

from datetime import datetime
import logging
from contextvars import ContextVar
import traceback
from typing import override
from fastapi import FastAPI, Request
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend

from app.core.database import get_session_context
from app.core.security import verify_password
from app.system.user import user_crud

logger = logging.getLogger(__name__)

# Context variable to store current request
_current_request: ContextVar[Request | None] = ContextVar("current_request", default=None)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        async with get_session_context() as session:
            user = await user_crud.get_user_by_username(username, session)
            if not user:
                return False

            if not verify_password(password, user.hashed_password):
                return False

        permissions = {menu.permission for menu in user.role.menus if menu.permission}

        logger.info(f"permissions: {permissions}")

        # Validate username/password credentials
        # And update session
        request.session.update({
            "username": user.username,
            "is_admin": user.is_admin,
            "permissions": list(permissions)
        })

        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        username = request.session.get("username")

        logger.info(f"authenticate username: {username}")

        if not username:
            return False

        # Check the token in depth
        return True

class CustomAdminApp(Admin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def index(self, request: Request):
        _current_request.set(request)
        return await super().index(request)
    
    async def list(self, request: Request):
        _current_request.set(request)
        return await super().list(request)
    
    async def details(self, request: Request):
        _current_request.set(request)
        return await super().details(request)

    async def delete(self, request: Request):
        _current_request.set(request)
        return await super().delete(request)

    async def create(self, request: Request):
        _current_request.set(request)
        return await super().create(request)

    async def edit(self, request: Request):
        _current_request.set(request)
        return await super().edit(request)

    async def export(self, request: Request):
        _current_request.set(request)
        return await super().export(request)
    
   
class CustomAdmin(ModelView):

    def date_format(value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")

    column_type_formatters = {
        **ModelView.column_type_formatters,
        datetime: date_format
    }


    # 检查是否有权限
    def check_permission(self, request: Request, permission: str) -> bool:
        permissions = request.session.get("permissions", [])
        is_admin = request.session.get("is_admin", False)
        logger.info(f"check_permission is_admin: {is_admin} {permission} {permissions}")
        return is_admin or permission in permissions

    @override
    def is_accessible(self, request: Request) -> bool:
        return self.check_permission(request, f"{self.permission_prefix}:list")

    @override
    def is_visible(self, request: Request) -> bool:
        # 设置 contextvar 以便权限检查方法可以访问 request
        _current_request.set(request)
        logger.info(f"is_visible request: {request}")
        return self.check_permission(request, f"{self.permission_prefix}:list")

    def _get_permission_from_session(self, permission: str) -> bool:
        """从 session 中获取权限信息"""
        try:

            # 打印堆栈信息
            # logger.info(f"stack trace: {traceback.extract_stack()}")

            logger.info(f"_get_permission_from_session permission: {permission}")
            request = _current_request.get()
            if request:
                logger.info(f"_get_permission_from_session request: {request}")
                return self.check_permission(request, permission)
        except Exception as e:
            logger.warning(f"Failed to get permission from session: {e}")
        return False

    @override
    @property
    def can_create(self) -> bool:
        return self._get_permission_from_session(f"{self.permission_prefix}:create")

    @override
    @property
    def can_edit(self) -> bool:
        return self._get_permission_from_session(f"{self.permission_prefix}:edit")

    @override
    @property
    def can_delete(self) -> bool:
        return self._get_permission_from_session(f"{self.permission_prefix}:delete")

    @override
    @property
    def can_export(self) -> bool:
        return self._get_permission_from_session(f"{self.permission_prefix}:export")

    @override
    @property
    def can_view_details(self) -> bool:
        return self._get_permission_from_session(f"{self.permission_prefix}:details")

    @property
    def permission_prefix(self) -> str:
        raise NotImplementedError("get_permission_prefix method must be implemented")

def register_admin(app: FastAPI):
    from sqladmin import Admin

    from app.core.database import SessionLocal, engine
    from app.system.menu.admin import MenuAdmin
    from app.system.role.admin import RoleAdmin
    from app.system.user.admin import UserAdmin

    # hex
    authentication_backend = AdminAuth(
        secret_key="74d82f44b1218a992a1dc5fbba06bdec987203e876c2b8552da7d7c5533a32e8")
    admin = CustomAdminApp(
        app,
        engine=engine,
        session_maker=SessionLocal,
        title="后台管理",
        logo_url="https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png",
        favicon_url="https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png",
        authentication_backend=authentication_backend
    )

    admin.add_view(UserAdmin)
    admin.add_view(RoleAdmin)
    admin.add_view(MenuAdmin)
