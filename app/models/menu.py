from datetime import datetime
from typing import List, Optional
from sqlmodel import Boolean, Field, ForeignKey, Relationship, SQLModel, Column, Integer, String, DateTime, text

from .link_model import RoleMenu

class Menu(SQLModel, table=True):
    __tablename__ = "sys_menus"

    __table_args__ = {
        "comment": "菜单表",
    }

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True, comment="菜单ID"))
    parent_id: int | None = Field(sa_column=Column(Integer, ForeignKey("sys_menus.id", ondelete="cascade"), nullable=True, comment="父菜单ID"))
    name: str = Field(sa_column=Column(String(length=100), nullable=False, comment="菜单名称"))

    # list、add、edit、delete、detail、export、import
    permission: str | None = Field(sa_column=Column(String(length=100), nullable=True, comment="菜单权限, NULL:目录"))
    path: str | None = Field(sa_column=Column(String(length=255), nullable=True, comment="菜单路径"))
    icon: str | None = Field(sa_column=Column(String(length=100), nullable=True, comment="菜单图标"))
    type: int = Field(sa_column=Column(Integer, nullable=False, comment="菜单类型, 1:目录, 2:页面, 3:按钮"))
    action_type: int | None = Field(sa_column=Column(Integer, nullable=True, comment="操作类型, NULL:页面/目录 1:批量按钮 2:行按钮 3:工具栏按钮"))
    sort: int = Field(sa_column=Column(Integer, nullable=False, comment="菜单排序, 越大越靠前"))
    visible: bool = Field(sa_column=Column(Boolean, nullable=False, default=True, comment="是否可见"))
    created_at: datetime = Field(sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"))
    updated_at: datetime = Field(sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP"), comment="更新时间"))

    children: List["Menu"] = Relationship(back_populates="parent", sa_relationship_kwargs={"passive_deletes": True})

    parent: Optional["Menu"] = Relationship(back_populates="children")

    roles: List["Role"] = Relationship(back_populates="menus", link_model=RoleMenu, sa_relationship_kwargs={"passive_deletes": True})


    # INSERT INTO sys_menus (id, parent_id, name, permission, path, icon, type, action_type, sort, visible) VALUES 
    # (1, NULL, '系统管理', NULL, NULL, NULL, 1, NULL, 1, TRUE),
    # (2, 1, '用户管理', 'user:list', '/users', 'user', 2, NULL, 1, TRUE),
    # (3, 2, '用户新增', 'user:add', NULL, NULL, 3, 3, 1, TRUE),
    # (4, 2, '用户编辑', 'user:edit', NULL, NULL, 3, 2, 1, TRUE),
    # (5, 2, '用户删除', 'user:delete', NULL, NULL, 3, 1, 1, TRUE),
    # (6, 2, '用户详情', 'user:detail', NULL, NULL, 3, 2, 1, TRUE),