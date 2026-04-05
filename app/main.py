from fastapi import FastAPI
from app.api.routes import auth, tariffs, billing
from app.core.exceptions import register_exception_handlers
from app.db.init_db import seed_db

app = FastAPI(
    title="Telecom Billing MVP",
    description="Client registration and billing system — Variant 6",
    version="1.0.0",
)

register_exception_handlers(app)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tariffs.router, prefix="/tariffs", tags=["tariffs"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])


@app.on_event("startup")
def on_startup() -> None:
    seed_db()
