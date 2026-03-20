from fastapi import FastAPI, HTTPException, Request, status

import logging

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse

logger = logging.getLogger(__name__)

def register_exceptions(app: FastAPI):

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTPException: {exc.status_code} {exc.detail} {request.url.path} {request.client.host}")
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            accept = request.headers.get("accept", "")
            x_requested_with = request.headers.get("x-requested-with", "")
            if "text/html" in accept and "XMLHttpRequest" not in x_requested_with:
                return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(request: Request, exc: RequestValidationError):
        logger.error(f"RequestValidationError: {exc.errors()} {request.url.path} {request.client.host}")
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": exc.errors()})