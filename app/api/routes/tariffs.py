from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.tariff import TariffResponse, TariffActivateRequest
from app.schemas.user import UserResponse
from app.services import tariff_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=list[TariffResponse])
def list_tariffs(db: Session = Depends(get_db)):
    return tariff_service.list_tariffs(db)


@router.post("/activate", response_model=UserResponse)
def activate_tariff(
    data: TariffActivateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_user = tariff_service.activate_tariff(db, current_user, data.tariff_id)
    return updated_user
