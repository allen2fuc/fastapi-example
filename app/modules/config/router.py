from typing import List
from fastapi import APIRouter, Depends, Form, Request, Security
from fastapi.responses import RedirectResponse

from app.core.dept import get_config_crud
from app.core.jinja import render_template
from app.core.security import get_current_user
from app.models.config import Config
from app.models.user import User
from app.modules.config.crud import ConfigCrud
from app.modules.config.schemas import ConfigCreate, ConfigQuery, ConfigUpdate

router = APIRouter()


@router.get("/{config_id}/detail")
async def config_detail(
    config_id: int,
    _current_user: User = Security(get_current_user, scopes=["sys:config:edit"]),
    config_crud: ConfigCrud = Depends(get_config_crud),
):
    config = await config_crud.get(config_id)
    if not config:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {
        "id": config.id,
        "code": config.code,
        "key": config.key,
        "value": config.value,
        "sort": config.sort,
        "description": config.description,
    }


@router.post("/bulk-delete")
async def bulk_delete_configs(
    request: Request,
    ids: List[int] = Form(...),
    _current_user: User = Security(get_current_user, scopes=["sys:config:delete"]),
    config_crud: ConfigCrud = Depends(get_config_crud),
):
    for config_id in ids:
        config = await config_crud.get(config_id)
        if config:
            await config_crud.delete(config)
    return RedirectResponse(url=str(request.url_for("list_configs")), status_code=303)


@router.post("")
async def create_config(
    body: ConfigCreate,
    _current_user: User = Security(get_current_user, scopes=["sys:config:edit"]),
    config_crud: ConfigCrud = Depends(get_config_crud),
):
    config = await config_crud.create(body.model_dump())
    return {"id": config.id, "key": config.key}


@router.put("/{config_id}")
async def update_config(
    config_id: int,
    body: ConfigUpdate,
    _current_user: User = Security(get_current_user, scopes=["sys:config:edit"]),
    config_crud: ConfigCrud = Depends(get_config_crud),
):
    config = await config_crud.get(config_id)
    if not config:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    config = await config_crud.update(config, body.model_dump(exclude_none=True))
    return {"id": config.id, "key": config.key}


@router.delete("/{config_id}")
async def delete_config(
    config_id: int,
    _current_user: User = Security(get_current_user, scopes=["sys:config:delete"]),
    config_crud: ConfigCrud = Depends(get_config_crud),
):
    config = await config_crud.get(config_id)
    if not config:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await config_crud.delete(config)
    return {"ok": True}


@router.get("")
async def list_configs(
    request: Request,
    pagination: ConfigQuery = Depends(),
    _current_user: User = Security(get_current_user, scopes=["sys:config:list"]),
    config_crud: ConfigCrud = Depends(get_config_crud),
):
    result = await config_crud.query(pagination)
    return render_template(request, "configs/list.jinja", {"result": result})
