import logging
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request, status
from slowapi.util import get_remote_address
from app.core.config import settings
from app.core.schemas import R


logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


def register_slowapi(app: FastAPI):
    app.state.limiter = limiter
    
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
        logger.error(f"Rate limit exceeded: {exc.detail}")
        content = R.error(code=status.HTTP_429_TOO_MANY_REQUESTS, message="Rate limit exceeded").model_dump()
        return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content=content)