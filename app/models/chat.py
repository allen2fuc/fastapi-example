from typing import Any, Dict, List
from sqlmodel import JSON, Boolean, Field, SQLModel, Column, Integer, String, DateTime, Text, text, Relationship

from sqlmodel import ForeignKey
from datetime import datetime

class Chat(SQLModel, table=True):
    __tablename__ = "sys_chats"

    __table_args__ = {
        "comment": "聊天记录表",
    }

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True, comment="聊天记录ID"))
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("sys_users.id", ondelete="cascade"), nullable=False, comment="用户ID"))
    title: str = Field(sa_column=Column(String(length=100), nullable=False, comment="聊天标题"))
    created_at: datetime = Field(sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"))
    updated_at: datetime = Field(sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP"), comment="更新时间"))

    chat_messages: List["ChatMessage"] = Relationship(back_populates="chat")


class ChatMessage(SQLModel, table=True):
    __tablename__ = "sys_chat_messages"

    __table_args__ = {
        "comment": "聊天消息表",
    }

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True, comment="聊天消息ID"))
    chat_id: int = Field(sa_column=Column(Integer, ForeignKey("sys_chats.id", ondelete="cascade"), nullable=False, comment="聊天记录ID"))
    content: str = Field(sa_column=Column(Text, nullable=False, comment="聊天内容"))
    role: str = Field(sa_column=Column(String(length=100), nullable=False, comment="聊天角色"))
    extra: Dict[str, Any] | None = Field(sa_column=Column(JSON, nullable=True, comment="聊天额外信息,记录Token消耗等数据"))
    # 是否已汇总
    summarized: bool = Field(sa_column=Column(Boolean, nullable=False, default=False, comment="是否已汇总"))
    created_at: datetime = Field(sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"))
    updated_at: datetime = Field(sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP"), comment="更新时间"))

    chat: Chat = Relationship(back_populates="chat_messages")