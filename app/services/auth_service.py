from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories import user_repository
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token


def register(db: Session, data: RegisterRequest) -> User:
    if user_repository.get_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    if user_repository.get_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    return user_repository.create(
        db,
        username=data.username,
        email=data.email,
        phone_number=data.phone_number,
        password_hash=hash_password(data.password),
    )


def login(db: Session, data: LoginRequest) -> TokenResponse:
    user = user_repository.get_by_username(db, data.username)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    token = create_access_token(subject=str(user.id), role=user.role.value)
    return TokenResponse(access_token=token)
