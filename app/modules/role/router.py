from datetime import datetime
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Security, status
from fastapi.responses import RedirectResponse
from typing import List

from app.core.dept import get_menu_crud, get_role_crud
from app.core.jinja import render_template
from app.core.schemas import QueryPagination, QueryResult
from app.core.security import get_current_user
from app.models.user import User
from app.modules.menu.crud import MenuCrud
from app.modules.role.crud import RoleCrud
from app.modules.role.schemas import RoleCreate, RoleUpdate

router = APIRouter()


@router.get("/preview")
async def preview_role_list(request: Request, pagination: QueryPagination = Depends()):
    """临时预览路由，仅用于设计调试"""
    from types import SimpleNamespace
    request.state.scopes = ["sys:role:list", "sys:role:edit", "sys:role:delete"]
    total = 8
    now = datetime.now()
    offset = pagination.get_offset()
    mock_roles = [
        SimpleNamespace(id=offset + i, name=f"role_{offset + i}", description=f"角色{offset + i}描述", created_at=now)
        for i in range(1, pagination.page_size + 1)
        if offset + i <= total
    ]
    result = QueryResult(items=mock_roles, total=total, page=pagination.page, page_size=pagination.page_size)
    return render_template(request, "roles/list.jinja", {
        "result": result,
        "role_detail_base": "/roles/preview",
        "bulk_delete_url": "/roles/preview/bulk-delete",
        "menus_tree_url": "/menus/preview/tree",
    })


@router.get("/preview/all")
async def preview_roles_all():
    """临时预览，仅用于设计调试"""
    return [{"id": i, "name": f"role_{i}"} for i in range(1, 5)]


@router.get("/preview/{role_id}/detail")
async def preview_role_detail(role_id: int):
    """临时预览，仅用于设计调试"""
    return {
        "id": role_id,
        "name": f"role_{role_id}",
        "description": f"角色{role_id}描述",
        "menu_ids": [1, 2, 3] if role_id == 1 else ([1] if role_id % 2 == 0 else []),
    }


@router.get("/all")
async def roles_all(
    _current_user: User = Depends(get_current_user),
    role_crud: RoleCrud = Depends(get_role_crud),
):
    roles = await role_crud.get_all()
    return [{"id": r.id, "name": r.name} for r in roles]


@router.get("/{role_id}/detail")
async def role_detail(
    role_id: int,
    _current_user: User = Security(get_current_user, scopes=["sys:role:edit"]),
    role_crud: RoleCrud = Depends(get_role_crud),
):
    role = await role_crud.get(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    menu_ids = await role_crud.get_menu_ids(role_id)
    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "menu_ids": list(menu_ids),
    }


@router.post("/preview/bulk-delete")
async def preview_role_bulk_delete():
    """临时预览，仅用于设计调试"""
    return RedirectResponse(url="/roles/preview", status_code=303)


@router.post("/bulk-delete")
async def bulk_delete_roles(
    request: Request,
    ids: List[int] = Form(...),
    _current_user: User = Security(get_current_user, scopes=["sys:role:delete"]),
    role_crud: RoleCrud = Depends(get_role_crud),
):
    for role_id in ids:
        role = await role_crud.get(role_id)
        if role:
            await role_crud.delete(role)
    return RedirectResponse(url=str(request.url_for("list_roles")), status_code=303)


@router.post("")
async def create_role(
    body: RoleCreate,
    _current_user: User = Security(get_current_user, scopes=["sys:role:edit"]),
    role_crud: RoleCrud = Depends(get_role_crud),
):
    data = body.model_dump()
    menu_ids = data.pop("menu_ids", [])
    role = await role_crud.create(data)
    await role_crud.set_menus(role, menu_ids)
    return {"id": role.id, "name": role.name}


@router.put("/{role_id}")
async def update_role(
    role_id: int,
    body: RoleUpdate,
    _current_user: User = Security(get_current_user, scopes=["sys:role:edit"]),
    role_crud: RoleCrud = Depends(get_role_crud),
):
    role = await role_crud.get(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    data = body.model_dump(exclude_none=True)
    menu_ids = data.pop("menu_ids", None)
    if data:
        role = await role_crud.update(role, data)
    if menu_ids is not None:
        await role_crud.set_menus(role, menu_ids)
    return {"id": role.id, "name": role.name}


@router.get("")
async def list_roles(
    request: Request,
    pagination: QueryPagination = Depends(),
    _current_user: User = Security(get_current_user, scopes=["sys:role:list"]),
    role_crud: RoleCrud = Depends(get_role_crud),
):
    result = await role_crud.query(pagination)
    return render_template(request, "roles/list.jinja", {"result": result})
