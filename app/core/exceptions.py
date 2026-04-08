from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.logging import logger


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
