from datetime import datetime
from typing import List, Optional
from sqlmodel import Boolean, DateTime, Relationship, SQLModel, Field, Column, SmallInteger, String, UUID, ForeignKey
import uuid
from app.admin.role.models import RoleMenuLink


class Menu(SQLModel, table=True):
    __tablename__ = "sys_menu"

    __table_args__ = {
        'comment': '系统菜单表'
    }

    id: Optional[uuid.UUID] = Field(default=None, sa_column=Column(UUID, primary_key=True, nullable=False, default=uuid.uuid4, comment="菜单ID"))
    parent_id: Optional[uuid.UUID] = Field(sa_column=Column(UUID,ForeignKey("sys_menu.id",ondelete="CASCADE"), default=None, nullable=True, comment="父菜单ID"))
    name: str = Field(sa_column=Column(String(50), unique=True, nullable=False, comment="菜单名称"))
    path: str = Field(sa_column=Column(String(200), nullable=False, comment="前端路由路径"))
    component: str = Field(sa_column=Column(String(200), nullable=False, comment="前端组件路径"))

    permission: Optional[str] = Field(sa_column=Column(String(100), nullable=True, default=None, comment="权限标识"))

    type: int = Field(sa_column=Column(SmallInteger, nullable=False, comment="菜单类型,1:目录,2:菜单,3:按钮"))
    icon: str = Field(sa_column=Column(String(50), nullable=False, comment="菜单图标"))
    sort: int = Field(sa_column=Column(SmallInteger, default=0, nullable=False, comment="排序"))

    visible: bool = Field(sa_column=Column(Boolean, default=True, nullable=False, comment="是否可见"))
    status: bool = Field(sa_column=Column(Boolean, default=True, nullable=False, comment="是否启用"))

    created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now, nullable=False, comment="创建时间"))
    updated_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间"))

    # 如果删除父菜单，需要删除子菜单

    # 如何删除菜单，需要删除角色菜单表中的关联数据
    roles: List["Role"] = Relationship(back_populates="menus", link_model=RoleMenuLink)

    def __str__(self):
        return f"{self.name}"