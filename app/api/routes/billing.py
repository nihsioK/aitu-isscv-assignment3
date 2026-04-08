from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.invoice import GenerateInvoiceRequest, InvoiceResponse
from app.services import billing_service
from app.dependencies.auth import get_current_user
from app.dependencies.roles import require_admin
from app.models.user import User, Role

router = APIRouter()


@router.post("/generate-invoice", response_model=InvoiceResponse, status_code=201)
def generate_invoice(
    data: GenerateInvoiceRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return billing_service.generate_invoice(db, data)


@router.get("/my-invoices", response_model=list[InvoiceResponse])
def my_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return billing_service.get_my_invoices(db, current_user.id)


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    is_admin = current_user.role == Role.ADMIN
    return billing_service.get_invoice(db, invoice_id, current_user.id, is_admin)
