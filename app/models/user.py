from datetime import datetime
from typing import List, Optional

from sqlmodel import (
    Boolean, 
    DateTime, 
    Field, 
    Integer, 
    Relationship, 
    SQLModel, 
    Column, 
    String, 
    text,
)

from .role import Role
from .link_model import UserRole

class User(SQLModel, table=True):

    __tablename__ = "sys_users"
    
    __table_args__ = {
        "comment": "用户表",
    }

    id: Optional[int] = Field(sa_column=Column(
        Integer, primary_key=True, autoincrement=True, comment="用户ID"
    ))

    email: str = Field(sa_column=Column(
        String(length=320), unique=True, index=True, nullable=False, comment="登录邮箱"
    ))

    hashed_password: str = Field(sa_column=Column(
        String(length=1024), nullable=False, comment="密码哈希"
    ))

    is_active: bool = Field(sa_column=Column(
        Boolean, default=True, nullable=False, comment="是否激活"
    ))

    is_superuser: bool = Field(sa_column=Column(
        Boolean, default=False, nullable=False, comment="是否超级用户"
    ))

    is_verified: bool = Field(sa_column=Column(
        Boolean, default=False, nullable=False, comment="是否验证"
    ))

    created_at: datetime = Field(sa_column=Column(
        DateTime, nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间"
    ))

    updated_at: datetime = Field(sa_column=Column(
        DateTime, nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
        comment="更新时间"
    ))

    roles: List[Role] = Relationship(back_populates="users", link_model=UserRole, sa_relationship_kwargs={"passive_deletes": True})