

from pydantic import BaseModel, Field
from typing import Annotated, Generic, List, Optional, TypeVar


T = TypeVar("T", bound=BaseModel)


class R(BaseModel, Generic[T]):
    code: Annotated[int, Field(default=200,description="状态码")]
    message: Annotated[str, Field(default="Success", description="消息内容")]
    data: Annotated[Optional[T], Field(default=None, description="数据内容")]

    @classmethod
    def success(cls, data: T, message: str = "Success") -> "R[T]":
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int = 500, message: str = "Internal Server Error") -> "R[T]":
        return cls(code=code, message=message, data=None)


class Pagination(BaseModel, Generic[T]):
    page: Annotated[int, Field(description="页码", examples=[1])]
    page_size: Annotated[int, Field(description="每页条数", examples=[10])]
    total: Annotated[int, Field(description="总条数", examples=[0])]
    items: Annotated[List[T], Field(description="数据列表")]

class PaginationQuery(BaseModel):
    page: Annotated[int, Field(default=1, description="页码", examples=[1])]
    page_size: Annotated[int, Field(default=10, description="每页条数", examples=[10])]

    # 获取offset
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    # 获取limit
    @property
    def limit(self) -> int:
        return self.page_size