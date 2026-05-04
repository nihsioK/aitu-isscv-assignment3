from sqlalchemy.orm import Session
from app.models.invoice import Invoice


def get_by_id(db: Session, invoice_id: int) -> Invoice | None:
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()


def get_by_user(db: Session, user_id: int) -> list[Invoice]:
    return db.query(Invoice).filter(Invoice.user_id == user_id).all()


def get_by_user_and_period(db: Session, user_id: int, billing_period: str) -> Invoice | None:
    return (
        db.query(Invoice)
        .filter(Invoice.user_id == user_id, Invoice.billing_period == billing_period)
        .first()
    )


def create(
    db: Session,
    user_id: int,
    tariff_id: int,
    billing_period: str,
    amount: float,
    currency: str = "KZT",
) -> Invoice:
    invoice = Invoice(
        user_id=user_id,
        tariff_id=tariff_id,
        billing_period=billing_period,
        amount=amount,
        currency=currency,
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice
