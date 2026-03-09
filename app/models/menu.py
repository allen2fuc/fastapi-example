from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, ForeignKey, Relationship, SQLModel, Column, Integer, String, DateTime, text

from .link_model import RoleMenu

class Menu(SQLModel, table=True):
    __tablename__ = "sys_menus"

    __table_args__ = {
        "comment": "菜单表",
    }

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True, comment="菜单ID"))
    parent_id: int = Field(sa_column=Column(Integer, ForeignKey("sys_menus.id", ondelete="cascade"), nullable=True, comment="父菜单ID"))
    name: str = Field(sa_column=Column(String(length=100), nullable=False, comment="菜单名称"))
    code: str = Field(sa_column=Column(String(length=100), nullable=False, comment="菜单编码"))
    path: str = Field(sa_column=Column(String(length=255), nullable=False, comment="菜单路径"))
    icon: str = Field(sa_column=Column(String(length=100), nullable=False, comment="菜单图标"))
    created_at: datetime = Field(sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"))
    updated_at: datetime = Field(sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="更新时间"))

    children: List["Menu"] = Relationship(back_populates="parent")

    parent: Optional["Menu"] = Relationship(back_populates="children")

    roles: List["Role"] = Relationship(back_populates="menus", link_model=RoleMenu, sa_relationship_kwargs={"passive_deletes": True})