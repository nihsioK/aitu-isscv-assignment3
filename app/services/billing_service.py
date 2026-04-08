from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories import invoice_repository, user_repository, tariff_repository
from app.schemas.invoice import GenerateInvoiceRequest
from app.models.invoice import Invoice
from app.core.logging import logger


def generate_invoice(db: Session, data: GenerateInvoiceRequest) -> Invoice:
    if not user_repository.get_by_id(db, data.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    if not tariff_repository.get_by_id(db, data.tariff_id):
        raise HTTPException(status_code=404, detail="Tariff not found")

    invoice = invoice_repository.create(
        db,
        user_id=data.user_id,
        tariff_id=data.tariff_id,
        billing_period=data.billing_period,
        amount=data.amount,
        currency=data.currency,
    )
    logger.info("INVOICE_GENERATED invoice_id=%d user_id=%d period=%s", invoice.id, invoice.user_id, invoice.billing_period)
    return invoice


def get_my_invoices(db: Session, user_id: int) -> list[Invoice]:
    return invoice_repository.get_by_user(db, user_id)


def get_invoice(db: Session, invoice_id: int, requesting_user_id: int, is_admin: bool) -> Invoice:
    invoice = invoice_repository.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if not is_admin and invoice.user_id != requesting_user_id:
        logger.warning("ACCESS_DENIED invoice_id=%d requesting_user_id=%d", invoice_id, requesting_user_id)
        raise HTTPException(status_code=403, detail="Access denied")

    return invoice
