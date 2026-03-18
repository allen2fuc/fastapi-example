from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request, Security
from fastapi.responses import RedirectResponse
from typing import List

from app.core.dept import get_menu_crud
from app.core.jinja import render_template
from app.core.schemas import QueryPagination, QueryResult
from app.core.security import get_current_user
from app.models.user import User
from app.modules.menu.crud import MenuCrud
from app.modules.menu.schemas import MenuCreate, MenuUpdate

router = APIRouter()

_TYPE_LABEL = {1: "目录", 2: "页面", 3: "按钮"}
_ACTION_LABEL = {1: "批量按钮", 2: "行按钮", 3: "工具栏按钮"}


def _build_tree(menus) -> list:
    nodes = {m.id: {"id": m.id, "name": m.name, "type": m.type, "children": []} for m in menus}
    roots = []
    for m in menus:
        node = nodes[m.id]
        if m.parent_id and m.parent_id in nodes:
            nodes[m.parent_id]["children"].append(node)
        else:
            roots.append(node)
    return roots


@router.get("/preview/tree")
async def preview_menu_tree():
    """临时预览，仅用于设计调试"""
    flat = [
        {"id": 1, "parent_id": None, "name": "系统管理", "type": 1},
        {"id": 2, "parent_id": 1,    "name": "用户管理", "type": 2},
        {"id": 3, "parent_id": 2,    "name": "用户新增", "type": 3},
        {"id": 4, "parent_id": 2,    "name": "用户编辑", "type": 3},
        {"id": 5, "parent_id": 2,    "name": "用户删除", "type": 3},
        {"id": 6, "parent_id": 1,    "name": "角色管理", "type": 2},
        {"id": 7, "parent_id": 6,    "name": "角色编辑", "type": 3},
        {"id": 8, "parent_id": 1,    "name": "菜单管理", "type": 2},
    ]
    from types import SimpleNamespace
    menus = [SimpleNamespace(**m) for m in flat]
    return _build_tree(menus)


@router.get("/tree")
async def menu_tree(
    _current_user: User = Depends(get_current_user),
    menu_crud: MenuCrud = Depends(get_menu_crud),
):
    menus = await menu_crud.get_all()
    return _build_tree(menus)


@router.get("/preview")
async def preview_menu_list(request: Request, pagination: QueryPagination = Depends()):
    """临时预览路由，仅用于设计调试"""
    from types import SimpleNamespace
    request.state.scopes = ["sys:menu:list", "sys:menu:edit", "sys:menu:delete"]
    total = 10
    now = datetime.now()
    offset = pagination.get_offset()
    mock_menus = [
        SimpleNamespace(
            id=offset + i,
            parent_id=None if (offset + i) % 3 == 1 else (offset + i) - 1,
            name=f"菜单{offset + i}",
            permission=f"sys:res{offset + i}:list" if (offset + i) % 3 != 1 else None,
            path=f"/res{offset + i}" if (offset + i) % 3 != 3 else None,
            type=((offset + i - 1) % 3) + 1,
            type_label=_TYPE_LABEL[((offset + i - 1) % 3) + 1],
            sort=offset + i,
            visible=(offset + i) % 4 != 0,
            created_at=now,
        )
        for i in range(1, pagination.page_size + 1)
        if offset + i <= total
    ]
    result = QueryResult(items=mock_menus, total=total, page=pagination.page, page_size=pagination.page_size)
    return render_template(request, "menus/list.jinja", {
        "result": result,
        "menu_detail_base": "/menus/preview",
        "bulk_delete_url": "/menus/preview/bulk-delete",
    })


@router.get("/{menu_id}/detail")
async def menu_detail(
    menu_id: int,
    _current_user: User = Security(get_current_user, scopes=["sys:menu:edit"]),
    menu_crud: MenuCrud = Depends(get_menu_crud),
):
    menu = await menu_crud.get(menu_id)
    if not menu:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {
        "id": menu.id,
        "parent_id": menu.parent_id,
        "name": menu.name,
        "permission": menu.permission,
        "path": menu.path,
        "icon": menu.icon,
        "type": menu.type,
        "action_type": menu.action_type,
        "sort": menu.sort,
        "visible": menu.visible,
    }


@router.get("/preview/{menu_id}/detail")
async def preview_menu_detail(menu_id: int):
    """临时预览，仅用于设计调试"""
    t = ((menu_id - 1) % 3) + 1
    return {
        "id": menu_id,
        "parent_id": None if t == 1 else menu_id - 1,
        "name": f"菜单{menu_id}",
        "permission": f"sys:res{menu_id}:list" if t != 1 else None,
        "path": f"/res{menu_id}" if t != 3 else None,
        "icon": None,
        "type": t,
        "action_type": None,
        "sort": menu_id,
        "visible": menu_id % 4 != 0,
    }


@router.post("/preview/bulk-delete")
async def preview_menu_bulk_delete():
    """临时预览，仅用于设计调试"""
    return RedirectResponse(url="/menus/preview", status_code=303)


@router.post("/bulk-delete")
async def bulk_delete_menus(
    request: Request,
    ids: List[int] = Form(...),
    _current_user: User = Security(get_current_user, scopes=["sys:menu:delete"]),
    menu_crud: MenuCrud = Depends(get_menu_crud),
):
    for menu_id in ids:
        menu = await menu_crud.get(menu_id)
        if menu:
            await menu_crud.delete(menu)
    return RedirectResponse(url=str(request.url_for("list_menus")), status_code=303)


@router.post("")
async def create_menu(
    body: MenuCreate,
    _current_user: User = Security(get_current_user, scopes=["sys:menu:edit"]),
    menu_crud: MenuCrud = Depends(get_menu_crud),
):
    menu = await menu_crud.create(body.model_dump())
    return {"id": menu.id, "name": menu.name}


@router.put("/{menu_id}")
async def update_menu(
    menu_id: int,
    body: MenuUpdate,
    _current_user: User = Security(get_current_user, scopes=["sys:menu:edit"]),
    menu_crud: MenuCrud = Depends(get_menu_crud),
):
    menu = await menu_crud.get(menu_id)
    if not menu:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    menu = await menu_crud.update(menu, body.model_dump(exclude_none=True))
    return {"id": menu.id, "name": menu.name}


@router.get("")
async def list_menus(
    request: Request,
    pagination: QueryPagination = Depends(),
    _current_user: User = Security(get_current_user, scopes=["sys:menu:list"]),
    menu_crud: MenuCrud = Depends(get_menu_crud),
):
    from types import SimpleNamespace
    result = await menu_crud.query(pagination)
    items = [
        SimpleNamespace(**m.model_dump(), type_label=_TYPE_LABEL.get(m.type, str(m.type)))
        for m in result.items
    ]
    return render_template(request, "menus/list.jinja", {
        "result": QueryResult(items=items, total=result.total, page=result.page, page_size=result.page_size),
    })
