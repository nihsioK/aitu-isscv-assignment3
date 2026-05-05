import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from jose import JWTError
from sqlalchemy.orm import Session

from app.bootstrap import create_schema, seed_data
from app.config import settings
from app.database import get_db
from app.models import Customer, Invoice, Plan, Role
from app.redis_limit import clear_failures, is_limited, record_failure
from app.schemas import (
    ActivatePlanIn,
    CustomerOut,
    GenerateInvoiceIn,
    InvoiceOut,
    LoginIn,
    PlanOut,
    RegisterIn,
    TokenOut,
)
from app.security import create_token, decode_token, hash_password, verify_password


logger = logging.getLogger("ai_telecom")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
bearer = HTTPBearer()
WEB_DIR = Path(__file__).resolve().parent / "web"


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_schema()
    db = next(get_db())
    try:
        seed_data(db)
    finally:
        db.close()
    logger.info("AI_ASSISTED_APP_STARTED")
    yield
    logger.info("AI_ASSISTED_APP_STOPPED")


app = FastAPI(
    title="AI-Assisted Telecom Billing MVP",
    description="P6 assignment 2, telecom billing scenario",
    version="2.0.0",
    lifespan=lifespan,
)
app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")


@app.middleware("http")
async def reject_large_bodies(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            size = int(content_length)
        except ValueError:
            return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length"})
        if size > settings.max_body_bytes:
            logger.warning("REQUEST_TOO_LARGE path=%s size=%d", request.url.path, size)
            return JSONResponse(status_code=413, content={"detail": "Request body too large"})
    return await call_next(request)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("UNHANDLED_ERROR method=%s path=%s error=%s", request.method, request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/", include_in_schema=False)
def ui() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


def current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> Customer:
    try:
        payload = decode_token(credentials.credentials)
        customer_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        logger.warning("AUTH_TOKEN_INVALID")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    customer = db.get(Customer, customer_id)
    if not customer or not customer.is_enabled:
        logger.warning("AUTH_CUSTOMER_DENIED customer_id=%s", customer_id)
        raise HTTPException(status_code=401, detail="Invalid account")
    return customer


def require_admin(customer: Customer = Depends(current_customer)) -> Customer:
    if customer.role != Role.ADMIN:
        logger.warning("ADMIN_DENIED customer_id=%d", customer.id)
        raise HTTPException(status_code=403, detail="Admin role required")
    return customer


def require_internal_key(
    x_internal_billing_key: str | None = Header(default=None, alias="X-Internal-Billing-Key"),
) -> None:
    if x_internal_billing_key != settings.internal_billing_key:
        logger.warning("INTERNAL_BILLING_KEY_DENIED")
        raise HTTPException(status_code=403, detail="Internal billing key required")


@app.post("/auth/register", response_model=CustomerOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)) -> Customer:
    if db.query(Customer).filter(Customer.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(Customer).filter(Customer.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    customer = Customer(
        username=data.username,
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role=Role.CLIENT,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    logger.info("CUSTOMER_REGISTERED customer_id=%d", customer.id)
    return customer


@app.post("/auth/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    if is_limited(data.username):
        logger.warning("LOGIN_LIMITED username=<redacted>")
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many failed attempts")

    customer = db.query(Customer).filter(Customer.username == data.username).first()
    if not customer or not verify_password(data.password, customer.password_hash):
        record_failure(data.username)
        logger.warning("LOGIN_FAILED username=<redacted>")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not customer.is_enabled:
        logger.warning("LOGIN_DISABLED customer_id=%d", customer.id)
        raise HTTPException(status_code=403, detail="Account disabled")

    clear_failures(data.username)
    logger.info("LOGIN_SUCCESS customer_id=%d", customer.id)
    return TokenOut(access_token=create_token(customer.id, customer.role.value))


@app.get("/auth/me", response_model=CustomerOut)
def me(customer: Customer = Depends(current_customer)) -> Customer:
    return customer


@app.get("/plans", response_model=list[PlanOut])
def plans(db: Session = Depends(get_db)) -> list[Plan]:
    return db.query(Plan).filter(Plan.is_public).order_by(Plan.monthly_price).all()


@app.post("/plans/activate", response_model=CustomerOut)
def activate_plan(
    data: ActivatePlanIn,
    customer: Customer = Depends(current_customer),
    db: Session = Depends(get_db),
) -> Customer:
    plan = db.get(Plan, data.plan_id)
    if not plan or not plan.is_public:
        logger.warning("PLAN_ACTIVATION_FAILED customer_id=%d plan_id=%d", customer.id, data.plan_id)
        raise HTTPException(status_code=404, detail="Plan not found")
    customer.active_plan_id = plan.id
    db.commit()
    db.refresh(customer)
    logger.info("PLAN_ACTIVATED customer_id=%d plan_id=%d", customer.id, plan.id)
    return customer


@app.get("/billing/invoices", response_model=list[InvoiceOut])
def my_invoices(
    customer: Customer = Depends(current_customer),
    db: Session = Depends(get_db),
) -> list[Invoice]:
    return db.query(Invoice).filter(Invoice.customer_id == customer.id).order_by(Invoice.created_at.desc()).all()


@app.get("/billing/invoices/{invoice_id}", response_model=InvoiceOut)
def invoice_detail(
    invoice_id: int,
    customer: Customer = Depends(current_customer),
    db: Session = Depends(get_db),
) -> Invoice:
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if customer.role != Role.ADMIN and invoice.customer_id != customer.id:
        logger.warning("INVOICE_ACCESS_DENIED invoice_id=%d customer_id=%d", invoice_id, customer.id)
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@app.post("/billing/generate", response_model=InvoiceOut, status_code=201)
def generate_invoice(
    data: GenerateInvoiceIn,
    _admin: Customer = Depends(require_admin),
    _internal_key: None = Depends(require_internal_key),
    db: Session = Depends(get_db),
) -> Invoice:
    customer = db.get(Customer, data.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if not customer.active_plan_id:
        raise HTTPException(status_code=400, detail="Customer has no active plan")
    plan = db.get(Plan, customer.active_plan_id)
    if not plan or not plan.is_public:
        raise HTTPException(status_code=400, detail="Active plan is unavailable")
    duplicate = (
        db.query(Invoice)
        .filter(Invoice.customer_id == customer.id, Invoice.billing_month == data.billing_month)
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Invoice already exists for this month")

    invoice = Invoice(
        customer_id=customer.id,
        plan_id=plan.id,
        billing_month=data.billing_month,
        amount=float(plan.monthly_price),
        currency="KZT",
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    logger.info("INVOICE_GENERATED invoice_id=%d customer_id=%d", invoice.id, customer.id)
    return invoice
