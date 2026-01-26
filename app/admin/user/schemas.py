


from datetime import datetime
from typing import Annotated, Optional
import uuid
from pydantic import BaseModel, Field, ValidationInfo, field_validator
from app.admin.role.schemas import RoleRead

class UserBase(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=50, description="用户名", examples=["admin"])]
    email: Annotated[str, Field(min_length=3, max_length=50, description="邮箱", examples=["admin@example.com"])]
    is_admin: Annotated[bool, Field(description="是否超级用户", examples=[True, False])]
    role_id: Annotated[Optional[uuid.UUID], Field(default=None, description="角色ID", examples=[uuid.uuid4()])]

class UserCreate(UserBase):
    password: Annotated[str, Field(min_length=8, max_length=255, description="密码", examples=["123456"])]

class UserRead(UserBase):
    id: Annotated[uuid.UUID, Field(description="用户ID")]
    created_at: Annotated[datetime, Field(description="创建时间")]
    updated_at: Annotated[datetime, Field(description="更新时间")]
    role: Annotated[Optional[RoleRead], Field(default=None, description="角色")]

class ChangePassword(BaseModel):
    old_password: Annotated[str, Field(min_length=8, max_length=255, description="旧密码")]
    new_password: Annotated[str, Field(min_length=8, max_length=255, description="新密码")]
    confirm_password: Annotated[str, Field(min_length=8, max_length=255, description="确认密码")]

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, v: str, info: ValidationInfo) -> str:
        if v != info.data["new_password"]:
            raise ValueError("确认密码与新密码不一致")
        return v

class UserUpdate(BaseModel):
    username: Annotated[Optional[str], Field(min_length=3, max_length=50, description="用户名")]
    email: Annotated[Optional[str], Field(min_length=3, max_length=50, description="邮箱")]
    is_admin: Annotated[Optional[bool], Field(description="是否超级用户")]
    role_id: Annotated[Optional[uuid.UUID], Field(description="角色ID")]