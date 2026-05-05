from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field


class TariffResponse(BaseModel):
    id: int
    name: str
    monthly_fee: float
    description: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class TariffActivateRequest(BaseModel):
    tariff_id: Annotated[int, Field(gt=0)]

    model_config = ConfigDict(extra="forbid")
