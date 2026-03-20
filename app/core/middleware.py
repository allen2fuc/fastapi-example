from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from fastapi import FastAPI, Request
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_REMEMBER_COOKIE = "remember_token"
_REMEMBER_MAX_AGE = 60 * 60 * 24 * 30  # 30 天


def _get_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.SESSION_SECRET_KEY, salt="remember-me")


def make_remember_token(user_id: int) -> str:
    return _get_serializer().dumps(user_id)


def verify_remember_token(token: str) -> int | None:
    try:
        return _get_serializer().loads(token, max_age=_REMEMBER_MAX_AGE)
    except (SignatureExpired, BadSignature):
        return None


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def remember_me(request: Request, call_next):
        from app.core.security import USER_ID_KEY
        if not request.session.get(USER_ID_KEY):
            token = request.cookies.get(_REMEMBER_COOKIE)
            if token:
                user_id = verify_remember_token(token)
                if user_id:
                    request.session[USER_ID_KEY] = user_id
                    # 恢复用户信息和权限
                    try:
                        from app.modules.user.crud import UserCrud
                        from sqlalchemy.ext.asyncio import async_sessionmaker
                        from sqlmodel.ext.asyncio.session import AsyncSession
                        from typing import cast
                        sf = cast(async_sessionmaker[AsyncSession], request.state.session_factory)
                        async with sf() as session:
                            crud = UserCrud(session)
                            user = await crud.get(user_id)
                            if user:
                                request.session["user_email"] = user.email
                                request.session["is_superuser"] = user.is_superuser
                                if not user.is_superuser:
                                    request.session["permissions"] = await crud.get_permissions(user_id)
                    except Exception:
                        pass
        return await call_next(request)

    @app.middleware("http")
    async def log_request(request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url.path} {request.client.host}")
        response = await call_next(request)
        return response

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SESSION_SECRET_KEY,
        session_cookie=settings.SESSION_COOKIE,
        max_age=settings.SESSION_MAX_AGE,
        https_only=settings.SESSION_HTTPS_ONLY,
        same_site=settings.SESSION_SAME_SITE,
    )
    
    app.add_middleware(
        ProxyHeadersMiddleware,
        trusted_hosts=settings.PROXY_TRUSTED_HOSTS,
    )
