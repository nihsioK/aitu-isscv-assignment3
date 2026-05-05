from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field
from app.models.invoice import InvoiceStatus


class GenerateInvoiceRequest(BaseModel):
    user_id: Annotated[int, Field(gt=0)]
    billing_period: Annotated[str, Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")]

    model_config = ConfigDict(extra="forbid")


class InvoiceResponse(BaseModel):
    id: int
    user_id: int
    tariff_id: int
    billing_period: str
    amount: float
    currency: str
    status: InvoiceStatus
    created_at: datetime

    model_config = {"from_attributes": True}
