from datetime import datetime, timedelta, timezone
import logging
from pwdlib import PasswordHash
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from typing import Annotated
import jwt

from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.admin.login import login_crud
from app.admin.user import user_crud
from app.core.database import get_session
from app.core.slowapi import limiter


SECRET_KEY = "c7a9d1a48eef88edaed40edfc9b96282661d9f93758060b645336a3619491b5d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
security = HTTPBasic()

logger = logging.getLogger(__name__)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


async def authenticate_user(session: AsyncSession, username: str, password: str):
    user = await user_crud.get_user_by_username(username, session)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@limiter.limit("3/minute")
async def get_current_user_with_basic_auth(
    request: Request,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    session: AsyncSession = Depends(get_session),
):
    current_username = credentials.username
    current_password = credentials.password

    logger.info(f"current_username: {current_username}")
    user = await user_crud.get_user_by_username(current_username, session)
    if not user:
        logger.info(f"用户不存在: {current_username}")
        await login_crud.create_login_log_from_request(current_username, False, "用户不存在", request, session)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    if not verify_password(current_password, user.hashed_password):
        logger.info(f"密码错误: {current_username}")
        await login_crud.create_login_log_from_request(current_username, False, "密码错误", request, session)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    await login_crud.create_login_log_from_request(current_username, True, "登录成功", request, session)
    return user


async def get_current_user(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = await user_crud.get_user_by_username(token_data.username, session)
    if user is None:
        raise credentials_exception
    return user


def reigster_auth_routes(app: FastAPI):

    router = APIRouter(prefix="/api/v1", tags=["认证管理"])

    @router.post("/auth/token", summary="登录获取Token", response_model=Token)
    @limiter.limit("3/minute")
    async def login_for_access_token(
        request: Request,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: AsyncSession = Depends(get_session),
    ) -> Token:
        user = await authenticate_user(session, form_data.username, form_data.password)
        if not user:
            logger.info(f"用户不存在: {form_data.username}")
            await login_crud.create_login_log_from_request(form_data.username, False, "用户不存在", request, session)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        logger.info(f"登录成功: {form_data.username}")
        await login_crud.create_login_log_from_request(form_data.username, True, "登录成功", request, session)
        return Token(access_token=access_token, token_type="bearer")

    app.include_router(router)
