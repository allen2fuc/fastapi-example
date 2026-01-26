

from typing import Annotated, Optional
import uuid
from pydantic import BaseModel, Field

class RoleBase(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=50, description="角色名称", examples=["admin"])]
    description: Annotated[str, Field(min_length=3, max_length=255, description="角色描述", examples=["管理员"])]

class RoleCreate(RoleBase):
    pass

class RoleRead(RoleBase):
    id: Annotated[uuid.UUID, Field(description="角色ID")]


class RoleUpdate(BaseModel):
    name: Annotated[Optional[str], Field(None, max_length=50, description="角色名称", examples=["admin"])]
    description: Annotated[Optional[str], Field(None, max_length=255, description="角色描述", examples=["管理员"])]