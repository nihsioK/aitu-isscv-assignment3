from datetime import datetime
from pydantic import BaseModel
from app.models.invoice import InvoiceStatus


class GenerateInvoiceRequest(BaseModel):
    user_id: int
    tariff_id: int
    billing_period: str  # "YYYY-MM"
    amount: float
    currency: str = "KZT"


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
