from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field

from app.core.schemas import QueryPagination


class RoleBase(BaseModel):
    name: Annotated[str, Field(description="角色名称")]
    description: Annotated[str, Field(description="角色描述")]


class RoleCreate(RoleBase):
    menu_ids: Annotated[list[int], Field(description="菜单ID列表")] = []


class RoleRead(RoleBase):
    id: Annotated[int, Field(description="角色ID")]
    created_at: Annotated[datetime, Field(description="创建时间")]
    updated_at: Annotated[datetime, Field(description="更新时间")]


class RoleUpdate(BaseModel):
    name: Annotated[str | None, Field(description="角色名称")] = None
    description: Annotated[str | None, Field(description="角色描述")] = None
    menu_ids: Annotated[list[int] | None, Field(description="菜单ID列表")] = None


class RoleQuery(QueryPagination):
    name: Annotated[str | None, Field(description="角色名称")] = None