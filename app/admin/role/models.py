from typing import List, Optional
from sqlmodel import ForeignKey, Relationship, SQLModel, Field, Column, String, UUID
import uuid

class RoleMenuLink(SQLModel, table=True):
    """角色菜单关联表"""
    __tablename__ = "sys_role_menu"

    __table_args__ = {
        'comment': '系统角色菜单表'
    }

    role_id: uuid.UUID = Field(sa_column=Column(UUID, ForeignKey("sys_role.id", ondelete="CASCADE"), primary_key=True))
    menu_id: uuid.UUID = Field(sa_column=Column(UUID, ForeignKey("sys_menu.id", ondelete="CASCADE"), primary_key=True))

class Role(SQLModel, table=True):
    __tablename__ = "sys_role"

    __table_args__ = {
        'comment': '系统角色表'
    }

    id: Optional[uuid.UUID] = Field(default=None, sa_column=Column(UUID, primary_key=True, nullable=False, default=uuid.uuid4, comment="角色ID"))
    name: str = Field(sa_column=Column(String(50), unique=True, nullable=False, comment="角色名称"))
    description: str = Field(sa_column=Column(String(255), nullable=False, comment="角色描述"))

    # 如果删除角色，需要删除角色菜单表中的关联数据
    menus: List["Menu"] = Relationship(back_populates="roles", link_model=RoleMenuLink, sa_relationship_kwargs={"lazy": "selectin"})
    # 如果删除角色，需要删除用户表中的关联数据
    users: List["User"] = Relationship(back_populates="role")

    def __str__(self):
        return f"{self.name}"