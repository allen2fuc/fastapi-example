

# 登录日志表
from datetime import datetime
from typing import Optional
from sqlmodel import Boolean, DateTime, Field, SQLModel, Column, String, UUID
import uuid

class LoginLog(SQLModel, table=True):
    __tablename__ = "sys_login_log"

    id: Optional[uuid.UUID] = Field(default=None, sa_column=Column(UUID, primary_key=True, default=uuid.uuid4, comment="登录日志ID"))
    username: str = Field(sa_column=Column(String(50), nullable=False, comment="用户名"))
    ip: str = Field(sa_column=Column(String(50), nullable=False, comment="IP地址"))
    user_agent: str = Field(sa_column=Column(String(255), nullable=False, comment="用户代理"))
    status: bool = Field(sa_column=Column(Boolean, default=True, nullable=False, comment="状态,True:成功,False:失败"))
    message: str = Field(sa_column=Column(String(255), nullable=True, comment="消息"))
    created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now, nullable=False, comment="创建时间"))