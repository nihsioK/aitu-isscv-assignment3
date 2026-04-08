from typing import Annotated
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=64)]
    email: Annotated[str, Field(max_length=128, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")]
    phone_number: Annotated[str, Field(pattern=r"^\+?[0-9]{7,15}$")]
    password: Annotated[str, Field(min_length=8, max_length=128)]


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
