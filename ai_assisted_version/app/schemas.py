from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import InvoiceStatus, Role


class RegisterIn(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=64)]
    email: Annotated[str, Field(max_length=128, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")]
    phone: Annotated[str, Field(pattern=r"^\+?[0-9]{7,15}$")]
    password: Annotated[str, Field(min_length=8, max_length=128)]

    model_config = ConfigDict(extra="forbid")

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        checks = [
            any(char.islower() for char in value),
            any(char.isupper() for char in value),
            any(char.isdigit() for char in value),
            any(char in "@$!%*?&" for char in value),
        ]
        if not all(checks):
            raise ValueError("Password must include lower, upper, digit and special character")
        if any(not (char.isalnum() or char in "@$!%*?&") for char in value):
            raise ValueError("Password contains unsupported characters")
        return value


class LoginIn(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=64)]
    password: Annotated[str, Field(min_length=8, max_length=128)]

    model_config = ConfigDict(extra="forbid")


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CustomerOut(BaseModel):
    id: int
    username: str
    email: str
    phone: str
    role: Role
    is_enabled: bool
    active_plan_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlanOut(BaseModel):
    id: int
    title: str
    monthly_price: float
    traffic_limit_gb: int
    description: str
    is_public: bool

    model_config = ConfigDict(from_attributes=True)


class ActivatePlanIn(BaseModel):
    plan_id: Annotated[int, Field(gt=0)]

    model_config = ConfigDict(extra="forbid")


class GenerateInvoiceIn(BaseModel):
    customer_id: Annotated[int, Field(gt=0)]
    billing_month: Annotated[str, Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")]

    model_config = ConfigDict(extra="forbid")


class InvoiceOut(BaseModel):
    id: int
    customer_id: int
    plan_id: int
    billing_month: str
    amount: float
    currency: str
    status: InvoiceStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
