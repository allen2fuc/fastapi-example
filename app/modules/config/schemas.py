from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field

from app.core.schemas import QueryPagination


class ConfigBase(BaseModel):
    code: Annotated[str, Field(description="配置编码")]
    key: Annotated[str, Field(description="配置键")]
    value: Annotated[str, Field(description="配置值")]
    sort: Annotated[int, Field(description="排序，越大越靠前")] = 0
    description: Annotated[str | None, Field(description="配置描述")] = None


class ConfigCreate(ConfigBase):
    pass


class ConfigRead(ConfigBase):
    id: Annotated[int, Field(description="配置ID")]
    created_at: Annotated[datetime, Field(description="创建时间")]
    updated_at: Annotated[datetime, Field(description="更新时间")]


class ConfigUpdate(BaseModel):
    code: Annotated[str | None, Field(description="配置编码")] = None
    key: Annotated[str | None, Field(description="配置键")] = None
    value: Annotated[str | None, Field(description="配置值")] = None
    sort: Annotated[int | None, Field(description="排序")] = None
    description: Annotated[str | None, Field(description="配置描述")] = None


class ConfigQuery(QueryPagination):
    code: Annotated[str | None, Field(description="配置编码")] = None
    key: Annotated[str | None, Field(description="配置键")] = None
