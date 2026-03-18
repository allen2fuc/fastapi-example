from datetime import datetime
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Security, status
from fastapi.responses import RedirectResponse
from typing import List

from app.core.dept import get_user_crud
from app.core.jinja import render_template
from app.core.schemas import QueryPagination, QueryResult
from app.core.security import get_current_user, get_password_hash
from app.models.user import User
from app.modules.user.crud import UserCrud
from app.modules.user.schemas import UserCreate, UserUpdate

router = APIRouter()


@router.get("/preview")
async def preview_list(request: Request, pagination: QueryPagination = Depends()):
    """临时预览路由，仅用于设计调试"""
    from types import SimpleNamespace
    request.state.scopes = ["sys:user:list", "sys:user:edit", "sys:user:delete"]
    total = 32
    now = datetime.now()
    offset = pagination.get_offset()
    mock_users = [
        SimpleNamespace(id=offset + i, email=f"user{offset + i}@example.com",
                        is_active=(offset + i) % 3 != 0, is_superuser=offset + i == 1,
                        is_verified=(offset + i) % 2 == 0, created_at=now)
        for i in range(1, pagination.page_size + 1)
        if offset + i <= total
    ]
    result = QueryResult(items=mock_users, total=total, page=pagination.page, page_size=pagination.page_size)
    return render_template(request, "users/list.jinja", {
        "result": result,
        "user_detail_base": "/users/preview",
        "bulk_delete_url": "/users/preview/bulk-delete",
        "roles_all_url": "/roles/preview/all",
    })


@router.get("/preview/{user_id}/detail")
async def preview_user_detail(user_id: int):
    """临时预览，仅用于设计调试"""
    return {
        "id": user_id,
        "email": f"user{user_id}@example.com",
        "is_active": user_id % 3 != 0,
        "is_superuser": user_id == 1,
        "is_verified": user_id % 2 == 0,
        "role_ids": [1, 2] if user_id == 1 else ([1] if user_id % 2 == 0 else []),
    }


@router.get("/{user_id}/detail")
async def user_detail(
    user_id: int,
    _current_user: User = Security(get_current_user, scopes=["sys:user:edit"]),
    user_crud: UserCrud = Depends(get_user_crud),
):
    user = await user_crud.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    role_ids = await user_crud.get_role_ids(user_id)
    return {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_verified": user.is_verified,
        "role_ids": list(role_ids),
    }


@router.post("/preview/bulk-delete")
async def preview_bulk_delete():
    """临时预览，仅用于设计调试"""
    return RedirectResponse(url="/users/preview", status_code=303)


@router.post("/bulk-delete")
async def bulk_delete_users(
    request: Request,
    ids: List[int] = Form(...),
    _current_user: User = Security(get_current_user, scopes=["sys:user:delete"]),
    user_crud: UserCrud = Depends(get_user_crud),
):
    for user_id in ids:
        user = await user_crud.get(user_id)
        if user:
            await user_crud.delete(user)
    return RedirectResponse(url=str(request.url_for("list_users")), status_code=303)


@router.post("")
async def create_user(
    body: UserCreate,
    _current_user: User = Security(get_current_user, scopes=["sys:user:edit"]),
    user_crud: UserCrud = Depends(get_user_crud),
):
    data = body.model_dump()
    role_ids = data.pop("role_ids", [])
    data["hashed_password"] = get_password_hash(data.pop("password").get_secret_value())
    user = await user_crud.create(data)
    await user_crud.set_roles(user, role_ids)
    return {"id": user.id, "email": user.email}


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    body: UserUpdate,
    _current_user: User = Security(get_current_user, scopes=["sys:user:edit"]),
    user_crud: UserCrud = Depends(get_user_crud),
):
    user = await user_crud.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    data = body.model_dump(exclude_none=True)
    role_ids = data.pop("role_ids", None)
    if "password" in data:
        data["hashed_password"] = get_password_hash(data.pop("password").get_secret_value())
    if data:
        user = await user_crud.update(user, data)
    if role_ids is not None:
        await user_crud.set_roles(user, role_ids)
    return {"id": user.id, "email": user.email}


@router.get("")
async def list_users(
    request: Request,
    pagination: QueryPagination = Depends(),
    _current_user: User = Security(get_current_user, scopes=["sys:user:list"]),
    user_crud: UserCrud = Depends(get_user_crud),
):
    result = await user_crud.query(pagination)
    return render_template(request, "users/list.jinja", {"result": result})
