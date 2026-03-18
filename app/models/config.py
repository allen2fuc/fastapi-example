from datetime import datetime

from sqlmodel import Field, SQLModel, Column, Integer, String, DateTime, text
# 配置表
class Config(SQLModel, table=True):
    __tablename__ = "sys_configs"

    __table_args__ = {
        "comment": "配置表",
    }

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True, comment="配置ID"))
    code: str = Field(sa_column=Column(String(length=100), nullable=False, comment="配置编码"))
    key: str = Field(sa_column=Column(String(length=100), nullable=False, comment="配置键"))
    value: str = Field(sa_column=Column(String(length=100), nullable=False, comment="配置值"))
    sort: int = Field(sa_column=Column(Integer, nullable=False, default=0, comment="配置排序,越大越靠前"))
    description: str | None = Field(sa_column=Column(String(length=255), nullable=True, comment="配置描述"))
    created_at: datetime = Field(sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"))
    updated_at: datetime = Field(sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP"), comment="更新时间"))