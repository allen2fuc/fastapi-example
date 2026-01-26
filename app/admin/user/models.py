from datetime import datetime
from typing import Optional
from sqlmodel import Boolean, DateTime, Field, Relationship, SQLModel, Column, String, UUID, ForeignKey
import uuid

class User(SQLModel, table=True):
    __tablename__ = "sys_user"

    __table_args__ = {
        'comment': '系统用户表'
    }

    id: Optional[uuid.UUID] = Field(default=None, sa_column=Column(UUID, primary_key=True, default=uuid.uuid4, comment="用户ID"))
    username: str = Field(sa_column=Column(String(50), unique=True, nullable=False, comment="用户名"))
    hashed_password: str = Field(sa_column=Column(String(255), nullable=False, comment="密码"))
    email: str = Field(sa_column=Column(String(50), unique=True, nullable=False, comment="邮箱"))
    is_admin: bool = Field(sa_column=Column(Boolean, default=False, nullable=False, comment="是否超级用户"))
    role_id: uuid.UUID = Field(sa_column=Column(UUID, ForeignKey("sys_role.id"), nullable=False, comment="角色ID"))

    created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now, nullable=False, comment="创建时间"))
    updated_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间"))
    role: "Role" = Relationship(back_populates="users", sa_relationship_kwargs={"lazy": "selectin"})

    def __str__(self):
        return f"{self.username}"
