from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field

from app.core.schemas import QueryPagination


class MenuBase(BaseModel):
    name: Annotated[str, Field(description="菜单名称")]
    parent_id: Annotated[int | None, Field(description="父菜单ID")] = None
    permission: Annotated[str | None, Field(description="菜单权限")] = None
    path: Annotated[str | None, Field(description="菜单路径")] = None
    icon: Annotated[str | None, Field(description="菜单图标")] = None
    type: Annotated[int, Field(description="菜单类型 1:目录 2:页面 3:按钮")]
    action_type: Annotated[int | None, Field(description="操作类型 1:批量按钮 2:行按钮 3:工具栏按钮")] = None
    sort: Annotated[int, Field(description="菜单排序，越大越靠前")]
    visible: Annotated[bool, Field(description="是否可见")]


class MenuCreate(MenuBase):
    pass


class MenuRead(MenuBase):
    id: Annotated[int, Field(description="菜单ID")]
    created_at: Annotated[datetime, Field(description="创建时间")]
    updated_at: Annotated[datetime, Field(description="更新时间")]


class MenuUpdate(BaseModel):
    name: Annotated[str | None, Field(description="菜单名称")] = None
    parent_id: Annotated[int | None, Field(description="父菜单ID")] = None
    permission: Annotated[str | None, Field(description="菜单权限")] = None
    path: Annotated[str | None, Field(description="菜单路径")] = None
    icon: Annotated[str | None, Field(description="菜单图标")] = None
    type: Annotated[int | None, Field(description="菜单类型")] = None
    action_type: Annotated[int | None, Field(description="操作类型")] = None
    sort: Annotated[int | None, Field(description="菜单排序")] = None
    visible: Annotated[bool | None, Field(description="是否可见")] = None


class MenuQuery(QueryPagination):
    name: Annotated[str | None, Field(description="菜单名称")] = None
    type: Annotated[str | None, Field(description="菜单类型")] = None
    
    def get_type(self) -> int | None:
        if self.type:
            if self.type.isdigit():
                return int(self.type)
        return None