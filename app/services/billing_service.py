from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories import invoice_repository, user_repository, tariff_repository
from app.schemas.invoice import GenerateInvoiceRequest
from app.models.invoice import Invoice


def generate_invoice(db: Session, data: GenerateInvoiceRequest) -> Invoice:
    if not user_repository.get_by_id(db, data.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    if not tariff_repository.get_by_id(db, data.tariff_id):
        raise HTTPException(status_code=404, detail="Tariff not found")

    return invoice_repository.create(
        db,
        user_id=data.user_id,
        tariff_id=data.tariff_id,
        billing_period=data.billing_period,
        amount=data.amount,
        currency=data.currency,
    )


def get_my_invoices(db: Session, user_id: int) -> list[Invoice]:
    return invoice_repository.get_by_user(db, user_id)


def get_invoice(db: Session, invoice_id: int, requesting_user_id: int, is_admin: bool) -> Invoice:
    invoice = invoice_repository.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # object-level ownership check — clients can only see their own invoices
    if not is_admin and invoice.user_id != requesting_user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return invoice
