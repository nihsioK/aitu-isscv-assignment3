from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.routes import auth, tariffs, billing
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import logger
from app.db.init_db import seed_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up")
    seed_db()
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="Telecom Billing MVP",
    description="Вариант 6",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            request_size = int(content_length)
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid Content-Length header"},
            )

        if request_size > settings.max_request_size_bytes:
            logger.warning(
                "REQUEST_TOO_LARGE path=%s size=%d limit=%d",
                request.url.path,
                request_size,
                settings.max_request_size_bytes,
            )
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large"},
            )

    return await call_next(request)


register_exception_handlers(app)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tariffs.router, prefix="/tariffs", tags=["tariffs"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])
