import uuid
from pydantic import BaseModel, Field

from datetime import datetime
class LoginLogBase(BaseModel):
    username: str = Field(description="用户名", examples=["admin"])
    ip: str = Field(description="IP地址", examples=["127.0.0.1"])
    user_agent: str = Field(description="用户代理", examples=["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"])
    status: bool = Field(description="状态,True:成功,False:失败", examples=[True, False])
    message: str = Field(description="消息", examples=["登录成功", "登录失败"])

class LoginLogCreate(LoginLogBase):
    pass

class LoginLogRead(LoginLogBase):
    id: uuid.UUID = Field(description="登录日志ID", examples=[uuid.uuid4()])
    created_at: datetime = Field(description="创建时间", examples=[datetime.now()])
