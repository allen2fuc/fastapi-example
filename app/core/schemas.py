


from typing import Annotated, Generic, List, Literal, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")

class SortItem(BaseModel):
    field: Annotated[str, Field(description="排序字段")]
    order: Annotated[Literal["asc", "desc"], Field(description="排序顺序")]

class QueryPagination(BaseModel):
    page: Annotated[Optional[int], Field(default=1, description="页码")] = 1
    page_size: Annotated[Optional[int], Field(default=10, description="每页条数")] = 20
    sort: Annotated[Optional[List[SortItem]], Field(description="排序")]

    def get_offset(self) -> int:
        return (self.page - 1) * self.page_size

    def get_limit(self) -> int:
        return self.page_size

    def get_sort_value(self) -> str | None:
        if self.sort is None:
            return None
        return ", ".join([f"{s.field} {s.order}" for s in self.sort])

class QueryResult(BaseModel, Generic[T]):
    items: Annotated[List[T], Field(description="数据列表")]
    total: Annotated[int, Field(description="总条数")]
    page: Annotated[int, Field(description="页码")]
    page_size: Annotated[int, Field(description="每页条数")]