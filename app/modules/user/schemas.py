

from datetime import datetime
from typing import Annotated
from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, Field, SecretStr

class UserBase(BaseModel):
    email: Annotated[EmailStr, Field(description="邮箱")]
    password: Annotated[SecretStr, Field(description="密码")]
    is_active: Annotated[bool, Field(description="是否激活")]
    is_superuser: Annotated[bool, Field(description="是否超级用户")]
    is_verified: Annotated[bool, Field(description="是否验证")]

class UserCreate(UserBase):
    pass

class UserRead(schemas.BaseUser[int]):
    id: Annotated[int, Field(description="用户ID")]
    created_at: Annotated[datetime, Field(description="创建时间")]
    updated_at: Annotated[datetime, Field(description="更新时间")]

class UserUpdate(BaseModel):
    email: Annotated[EmailStr | None, Field(description="邮箱")]
    password: Annotated[SecretStr | None, Field(description="密码")]
    is_active: Annotated[bool | None, Field(description="是否激活")]
    is_superuser: Annotated[bool | None, Field(description="是否超级用户")]
    is_verified: Annotated[bool | None, Field(description="是否验证")]