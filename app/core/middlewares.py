import time
from fastapi import FastAPI, Request


def register_middlewares(app: FastAPI):

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    # @app.middleware("http")
    # async def add_security_headers(request: Request, call_next):
    #     response = await call_next(request)
    #     response.headers["X-Frame-Options"] = "DENY"
    #     response.headers["X-Content-Type-Options"] = "nosniff"
    #     response.headers["X-XSS-Protection"] = "1; mode=block"
    #     response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; frame-src 'self'; media-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; sandbox 'allow-same-origin allow-scripts allow-forms'; report-uri /csp-report"
    #     return response

    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])
