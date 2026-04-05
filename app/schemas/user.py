from datetime import datetime
from pydantic import BaseModel
from app.models.user import Role


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone_number: str
    role: Role
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
