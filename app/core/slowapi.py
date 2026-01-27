import logging
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request, status
from slowapi.util import get_remote_address
from app.core.config import settings
from app.core.schemas import R


logger = logging.getLogger(__name__)


def key_func(request: Request):
    logger.info(f"Rate Limit Request： {request.method} {request.url.path} {request.client.host}")
    return get_remote_address(request)


limiter = Limiter(key_func=key_func)


def register_slowapi(app: FastAPI):
    pass
    # 注册为全局RateLimit
    # app.state.limiter = limiter