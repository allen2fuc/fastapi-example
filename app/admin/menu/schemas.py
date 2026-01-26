


from datetime import datetime
from typing import Annotated, Optional
import uuid

from pydantic import BaseModel, Field


class MenuBase(BaseModel):
    parent_id: Annotated[Optional[uuid.UUID], Field(default=None, description="父菜单ID", examples=[uuid.uuid4()])]
    name: Annotated[str, Field(min_length=3, max_length=50, description="菜单名称", examples=["用户管理"])]
    path: Annotated[str, Field(min_length=3, max_length=200, description="菜单路径", examples=["/admin/user/list"])]
    component: Annotated[str, Field(min_length=3, max_length=200, description="菜单组件", examples=["User"])]
    permission: Annotated[Optional[str], Field(default=None, description="菜单权限", examples=["system:user:list"])]
    type: Annotated[int, Field(description="菜单类型", examples=[1, 2, 3])]
    icon: Annotated[str, Field(min_length=3, max_length=50, description="菜单图标", examples=["fa-solid fa-list"])]
    sort: Annotated[int, Field(description="菜单排序", examples=[1])]
    visible: Annotated[bool, Field(description="是否可见", examples=[True, False])]
    status: Annotated[bool, Field(description="是否启用", examples=[True, False])]

class MenuCreate(MenuBase):
    pass

class MenuRead(MenuBase):
    id: Annotated[uuid.UUID, Field(description="菜单ID", examples=[uuid.uuid4()])]
    created_at: Annotated[datetime, Field(description="创建时间", examples=[datetime.now()])]
    updated_at: Annotated[datetime, Field(description="更新时间", examples=[datetime.now()])]