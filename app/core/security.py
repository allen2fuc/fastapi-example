from pwdlib import PasswordHash
from fastapi import Depends, status
from fastapi.security import SecurityScopes
from fastapi.exceptions import HTTPException
from fastapi import Request

import logging

from app.modules.user.crud import UserCrud

from .dept import get_user_crud
logger = logging.getLogger(__name__)

USER_ID_KEY = "session_id"
password_hash = PasswordHash.recommended()

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

async def get_current_user(
    security_scopes: SecurityScopes,
    request: Request,
    user_crud: UserCrud = Depends(get_user_crud),
):

    user_id: int | None = request.session.get(USER_ID_KEY)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user = await user_crud.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if security_scopes.scopes and not user.is_superuser:
        permissions = await user_crud.get_permissions(user.id)
        for scope in security_scopes.scopes:
            if scope not in permissions:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return user