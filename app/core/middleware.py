from fastapi import FastAPI, Request
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def register_middleware(app: FastAPI):

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
