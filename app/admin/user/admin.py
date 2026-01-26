
from typing import Any


from datetime import datetime
import logging
from fastapi import Request
from sqladmin import ModelView
import wtforms

from app.core.admin import CustomAdmin
from app.core.security import hash_password
from .models import User

logger = logging.getLogger(__name__)


class UserAdmin(CustomAdmin, model=User):
    category = "系统管理"
    category_icon = "fa-solid fa-user-shield"
    name_plural = "用户管理"
    name = "用户管理"
    label = "用户管理"
    icon = "fa-solid fa-user"
    column_labels = {
        User.hashed_password: "Password",
    }
    column_exclude_list = [User.hashed_password, User.role_id, User.id]
    column_searchable_list = [User.username, User.email]
    form_overrides = dict(email=wtforms.EmailField, hashed_password=wtforms.PasswordField)
    form_columns = [User.username, User.email, User.hashed_password, User.is_admin, User.role]
    # form_create_rules = [User.username, User.email, User.hashed_password, User.is_admin, User.role]
    form_edit_rules = ["username", "email", "is_admin", "role"]

    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        if is_created and "hashed_password" in data:
            data["hashed_password"] = hash_password(data["hashed_password"])
        return await super().on_model_change(data, model, is_created, request)

    permission_prefix = "admin:user"