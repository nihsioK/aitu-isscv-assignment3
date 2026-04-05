from pydantic import BaseModel


class TariffResponse(BaseModel):
    id: int
    name: str
    monthly_fee: float
    description: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class TariffActivateRequest(BaseModel):
    tariff_id: int
