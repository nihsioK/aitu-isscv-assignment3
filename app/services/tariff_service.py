from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories import tariff_repository, user_repository
from app.models.tariff import Tariff
from app.models.user import User


def list_tariffs(db: Session) -> list[Tariff]:
    return tariff_repository.get_all_active(db)


def activate_tariff(db: Session, user: User, tariff_id: int) -> User:
    tariff = tariff_repository.get_by_id(db, tariff_id)
    if not tariff or not tariff.is_active:
        raise HTTPException(status_code=404, detail="Tariff not found")

    return user_repository.set_active_tariff(db, user, tariff_id)
