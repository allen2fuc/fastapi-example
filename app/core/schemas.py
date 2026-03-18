


from typing import Annotated, Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")

class QueryPagination(BaseModel):
    page: Annotated[int, Field(ge=1, description="页码")] = 1
    page_size: Annotated[int, Field(default=10, ge=1, description="每页条数")] = 10

    def get_offset(self) -> int:
        return (self.page - 1) * self.page_size

    def get_limit(self) -> int:
        return self.page_size

class QueryResult(BaseModel, Generic[T]):
    items: Annotated[List[T], Field(description="数据列表")]
    total: Annotated[int, Field(description="总条数")]
    page: Annotated[int, Field(description="页码")]
    page_size: Annotated[int, Field(description="每页条数")]