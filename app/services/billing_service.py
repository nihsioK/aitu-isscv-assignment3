from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories import invoice_repository, user_repository, tariff_repository
from app.schemas.invoice import GenerateInvoiceRequest
from app.models.invoice import Invoice
from app.core.logging import logger


def generate_invoice(db: Session, data: GenerateInvoiceRequest) -> Invoice:
    user = user_repository.get_by_id(db, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.active_tariff_id:
        raise HTTPException(status_code=400, detail="User has no active tariff")

    tariff = tariff_repository.get_by_id(db, user.active_tariff_id)
    if not tariff or not tariff.is_active:
        raise HTTPException(status_code=400, detail="Active tariff is not available")
    if invoice_repository.get_by_user_and_period(db, user.id, data.billing_period):
        raise HTTPException(status_code=409, detail="Invoice already exists for this period")

    invoice = invoice_repository.create(
        db,
        user_id=user.id,
        tariff_id=tariff.id,
        billing_period=data.billing_period,
        amount=float(tariff.monthly_fee),
        currency="KZT",
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
        raise HTTPException(status_code=404, detail="Invoice not found")

    return invoice
