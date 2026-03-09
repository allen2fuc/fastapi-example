from datetime import datetime
from typing import List

from sqlmodel import (
    Field, 
    Relationship, 
    SQLModel, 
    Column, 
    Integer, 
    String, 
    DateTime, 
    text,
)

from .link_model import RoleMenu, UserRole
from .menu import Menu

class Role(SQLModel, table=True):
    __tablename__ = "sys_roles"

    __table_args__ = {
        "comment": "角色表",
    }

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True, comment="角色ID"))
    name: str = Field(sa_column=Column(String(length=100), nullable=False, comment="角色名称"))
    description: str = Field(sa_column=Column(String(length=255), nullable=False, comment="角色描述"))
    created_at: datetime = Field(sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"))
    updated_at: datetime = Field(sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="更新时间"))

    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole, sa_relationship_kwargs={"passive_deletes": True})

    menus: List[Menu] = Relationship(back_populates="roles", link_model=RoleMenu, sa_relationship_kwargs={"passive_deletes": True})
