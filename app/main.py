from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import auth, tariffs, billing
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

register_exception_handlers(app)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tariffs.router, prefix="/tariffs", tags=["tariffs"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])
