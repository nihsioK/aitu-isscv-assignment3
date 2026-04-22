import re
from typing import Annotated
from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=64)]
    email: Annotated[str, Field(max_length=128, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")]
    phone_number: Annotated[str, Field(pattern=r"^\+?[0-9]{7,15}$")]
    password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[@$!%*?&]", value):
            raise ValueError("Password must contain at least one special character (@$!%*?&)")
        if re.search(r"[^A-Za-z\d@$!%*?&]", value):
            raise ValueError("Password contains unsupported characters")
        return value


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
