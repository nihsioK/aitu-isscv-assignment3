from sqlalchemy.orm import Session
from app.models.tariff import Tariff


def get_by_id(db: Session, tariff_id: int) -> Tariff | None:
    return db.query(Tariff).filter(Tariff.id == tariff_id).first()


def get_all_active(db: Session) -> list[Tariff]:
    return db.query(Tariff).filter(Tariff.is_active).all()
